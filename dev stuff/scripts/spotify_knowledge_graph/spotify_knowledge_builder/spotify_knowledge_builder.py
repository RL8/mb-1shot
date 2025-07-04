#!/usr/bin/env python3
"""
Enhanced Spotify Knowledge Graph Builder with Era-Based Consolidation
Captures comprehensive album metadata and organizes content by eras
Artist-agnostic system that works for all musicians
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j import GraphDatabase
import os
import time
from dotenv import load_dotenv
from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

# Load environment variables from the main .env file (single source of truth)
# Get the project root directory (3 levels up from this script)
project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

print(f"🔧 Loading configuration from: {env_path}")
print(f"✅ Environment file exists: {env_path.exists()}")

class EraManager:
    """Manages era detection and album consolidation for any artist"""
    
    UNIVERSAL_TAGS = {
        'release_type': ['original', 'deluxe', 'remaster', 'reissue', 'anniversary', 'expanded', 'collectors'],
        'content_type': ['standard', 'explicit', 'clean', 'instrumental', 'acoustic', 'live'],
        'exclusivity': ['vault', 'bonus', 'exclusive', 'rare', 'unreleased', 'demo', 'outtake'],
        'format': ['physical', 'digital', 'vinyl', 'cd', 'streaming', 'cassette'],
        'market': ['japan_edition', 'uk_edition', 'eu_edition', 'target_exclusive', 'deluxe_edition'],
        'collaboration': ['remix', 'feature', 'acoustic', 'orchestral', 'stripped'],
        'version': ['radio_edit', 'extended', 'single_version', 'album_version', 'taylors_version']
    }
    
    def detect_eras(self, albums: List[Dict]) -> List[Dict]:
        """Detect natural eras in an artist's discography"""
        if not albums:
            return []
        
        # Sort albums by release date
        sorted_albums = sorted(albums, key=lambda x: x.get('release_date', ''))
        studio_albums = [a for a in sorted_albums if a.get('album_type') == 'album']
        
        if not studio_albums:
            return [{'era_name': 'singles_era', 'albums': albums, 'main_album': albums[0] if albums else None}]
        
        eras = []
        current_era_albums = []
        era_start_date = None
        
        for i, album in enumerate(studio_albums):
            album_date = album.get('release_date', '')
            
            # Start new era if this is the first album or significant time gap
            if (not current_era_albums or 
                self._is_era_boundary(album, studio_albums[i-1] if i > 0 else None)):
                
                # Save previous era
                if current_era_albums:
                    era_name = self._generate_era_name(current_era_albums[0])
                    main_album = self._select_main_album(current_era_albums)
                    eras.append({
                        'era_name': era_name,
                        'albums': current_era_albums.copy(),
                        'main_album': main_album,
                        'start_date': era_start_date,
                        'end_date': album_date
                    })
                
                # Start new era
                current_era_albums = [album]
                era_start_date = album_date
            else:
                current_era_albums.append(album)
        
        # Add final era
        if current_era_albums:
            era_name = self._generate_era_name(current_era_albums[0])
            main_album = self._select_main_album(current_era_albums)
            eras.append({
                'era_name': era_name,
                'albums': current_era_albums,
                'main_album': main_album,
                'start_date': era_start_date,
                'end_date': None
            })
        
        # Add non-studio albums to appropriate eras
        self._assign_non_studio_albums(albums, eras)
        
        return eras
    
    def _is_era_boundary(self, current_album: Dict, previous_album: Optional[Dict]) -> bool:
        """Determine if current album starts a new era"""
        if not previous_album:
            return True
        
        current_date = current_album.get('release_date', '')
        previous_date = previous_album.get('release_date', '')
        
        # Parse dates
        try:
            current_year = int(current_date[:4]) if current_date else 0
            previous_year = int(previous_date[:4]) if previous_date else 0
            
            # New era if more than 3 years gap
            if current_year - previous_year > 3:
                return True
        except:
            pass
        
        # Check for genre shifts
        current_genres = set(current_album.get('genres', []))
        previous_genres = set(previous_album.get('genres', []))
        
        if current_genres and previous_genres:
            genre_overlap = len(current_genres.intersection(previous_genres))
            if genre_overlap / max(len(current_genres), len(previous_genres)) < 0.3:
                return True
        
        # Check for label changes (often indicates new era)
        if (current_album.get('label', '').lower() != previous_album.get('label', '').lower() and
            current_album.get('label') and previous_album.get('label')):
            return True
        
        return False
    
    def _generate_era_name(self, representative_album: Dict) -> str:
        """Generate era name based on representative album"""
        album_name = representative_album.get('name', 'unknown')
        release_date = representative_album.get('release_date', '')
        
        # Extract year
        year = release_date[:4] if release_date else 'unknown'
        
        # Clean album name for era
        era_base = re.sub(r'[^\w\s]', '', album_name.lower()).replace(' ', '_')
        return f"{era_base}_{year}_era"
    
    def _select_main_album(self, era_albums: List[Dict]) -> Dict:
        """Select the main/canonical album for the era"""
        if len(era_albums) == 1:
            return era_albums[0]
        
        # Priority scoring
        def score_album(album):
            score = 0
            
            # Prefer studio albums
            if album.get('album_type') == 'album':
                score += 100
            
            # Prefer original releases
            name_lower = album.get('name', '').lower()
            if not any(variant in name_lower for variant in ['deluxe', 'remaster', 'reissue', 'anniversary']):
                score += 50
            
            # Prefer earlier releases
            release_date = album.get('release_date', '')
            if release_date:
                try:
                    year = int(release_date[:4])
                    score += 2024 - year  # Favor older
                except:
                    pass
            
            # Prefer albums with more tracks (more complete)
            score += album.get('total_tracks', 0)
            
            # Prefer higher popularity
            score += album.get('popularity', 0) * 0.1
            
            return score
        
        return max(era_albums, key=score_album)
    
    def _assign_non_studio_albums(self, all_albums: List[Dict], eras: List[Dict]):
        """Assign singles, compilations, etc. to appropriate eras"""
        non_studio = [a for a in all_albums if a.get('album_type') != 'album']
        
        for album in non_studio:
            album_date = album.get('release_date', '')
            best_era = None
            min_distance = float('inf')
            
            for era in eras:
                era_start = era.get('start_date', '')
                era_end = era.get('end_date', '')
                
                # Calculate temporal distance to era
                distance = self._calculate_temporal_distance(album_date, era_start, era_end)
                if distance < min_distance:
                    min_distance = distance
                    best_era = era
            
            if best_era:
                best_era['albums'].append(album)
    
    def _calculate_temporal_distance(self, album_date: str, era_start: str, era_end: Optional[str]) -> float:
        """Calculate how close an album is to an era"""
        try:
            album_year = int(album_date[:4]) if album_date else 2000
            start_year = int(era_start[:4]) if era_start else 2000
            end_year = int(era_end[:4]) if era_end else 2024
            
            if start_year <= album_year <= end_year:
                return 0  # Within era
            elif album_year < start_year:
                return start_year - album_year
            else:
                return album_year - end_year
        except:
            return float('inf')
    
    def generate_track_tags(self, track: Dict, source_albums: List[Dict]) -> List[str]:
        """Generate comprehensive tags for a track based on which albums it appears on"""
        tags = set()
        
        for album in source_albums:
            album_name = album.get('name', '').lower()
            album_type = album.get('album_type', '')
            
            # Release type tags
            if 'deluxe' in album_name:
                tags.add('deluxe_edition')
            if 'remaster' in album_name:
                tags.add('remaster')
            if 'anniversary' in album_name:
                tags.add('anniversary')
            if 'vault' in album_name or 'from the vault' in album_name:
                tags.add('vault')
            if 'bonus' in album_name:
                tags.add('bonus')
            
            # Album type tags
            if album_type == 'single':
                tags.add('single_release')
            elif album_type == 'compilation':
                tags.add('compilation')
            
            # Version tags
            if 'taylor\'s version' in album_name or 'tv' in album_name:
                tags.add('taylors_version')
            if 'explicit' in album_name:
                tags.add('explicit')
            if 'clean' in album_name:
                tags.add('clean')
            if 'acoustic' in album_name:
                tags.add('acoustic')
            if 'live' in album_name:
                tags.add('live')
        
        # Add original tag if this appears to be the first/main release
        if not tags or 'deluxe_edition' not in tags:
            tags.add('original_release')
        
        return list(tags)

class SpotifyKnowledgeGraphBuilder:
    def __init__(self):
        """Initialize Spotify API client and Neo4j connection"""
        
        print("🎵 Initializing Spotify Knowledge Graph Builder")
        print("=" * 60)
        
        # Spotify API credentials
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("❌ Spotify credentials not found. Check SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        
        # Neo4j credentials - using correct variable names from .env
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not self.neo4j_uri or not self.neo4j_password:
            raise ValueError("❌ Neo4j credentials not found. Check AURA_DB_URI and AURA_DB_PASSWORD in .env file")
        
        # Initialize connections
        self.sp = None
        self.driver = None
        self.era_manager = EraManager()
        
        self._setup_connections()
        
        print("✅ Spotify API and Neo4j connections initialized")
        print(f"🎯 Configuration loaded from: {env_path}")
        print("=" * 60)
    
    def _setup_connections(self):
        """Initialize Spotify and Neo4j connections"""
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
            client_id=self.client_id,
            client_secret=self.client_secret
        ))
        
        self.driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
    
    def get_artist_by_name(self, artist_name):
        """Get artist information from Spotify by name"""
        try:
            results = self.sp.search(q=artist_name, type='artist', limit=1)
            if results['artists']['items']:
                artist = results['artists']['items'][0]
                print(f"✅ Found artist: {artist['name']} (ID: {artist['id']})")
                return artist
            else:
                print(f"❌ Artist not found: {artist_name}")
                return None
        except Exception as e:
            print(f"❌ Error searching for artist {artist_name}: {e}")
            return None
    
    def get_artist_albums_comprehensive(self, artist_id, limit=50):
        """Get ALL albums for an artist with comprehensive metadata"""
        try:
            albums = []
            offset = 0
            
            while True:
                # Get albums batch
                results = self.sp.artist_albums(
                    artist_id, 
                    album_type='album,single,compilation,appears_on', 
                    limit=min(limit, 50),
                    offset=offset
                )
                
                if not results['items']:
                    break
                
                for album in results['items']:
                    # Get full album details with enhanced metadata
                    try:
                        album_details = self.sp.album(album['id'])
                        albums.append(album_details)
                    except Exception as e:
                        print(f"⚠️ Could not get details for album {album.get('name', 'unknown')}: {e}")
                        continue
                
                # Check if we have more results
                if len(results['items']) < 50 or len(albums) >= limit:
                    break
                
                offset += 50
                time.sleep(0.1)  # Rate limiting
            
            print(f"✅ Found {len(albums)} albums for artist {artist_id}")
            return albums
            
        except Exception as e:
            print(f"❌ Error getting albums for artist {artist_id}: {e}")
            return []
    
    def get_album_tracks_comprehensive(self, album_id):
        """Get all tracks for an album with comprehensive metadata and audio features"""
        try:
            results = self.sp.album_tracks(album_id)
            tracks = results['items']
            
            # Get audio features for all tracks
            track_ids = [track['id'] for track in tracks if track['id']]
            if track_ids:
                try:
                    audio_features = self.sp.audio_features(track_ids)
                    
                    # Merge track info with audio features
                    for i, track in enumerate(tracks):
                        if i < len(audio_features) and audio_features[i]:
                            track['audio_features'] = audio_features[i]
                except Exception as e:
                    print(f"⚠️ Could not get audio features for album {album_id}: {e}")
            
            print(f"✅ Found {len(tracks)} tracks for album {album_id}")
            return tracks
            
        except Exception as e:
            print(f"❌ Error getting tracks for album {album_id}: {e}")
            return []
    
    def create_artist_node(self, artist_data):
        """Create artist node in Neo4j with comprehensive metadata"""
        with self.driver.session() as session:
            try:
                cypher = """
                MERGE (a:Artist {spotify_id: $spotify_id})
                SET a.name = $name,
                    a.followers = $followers,
                    a.popularity = $popularity,
                    a.genres = $genres,
                    a.image_url = $image_url,
                    a.spotify_url = $spotify_url,
                    a.updated_at = datetime()
                RETURN a
                """
                
                session.run(cypher, 
                    spotify_id=artist_data['id'],
                    name=artist_data['name'],
                    followers=artist_data['followers']['total'],
                    popularity=artist_data['popularity'],
                    genres=artist_data['genres'],
                    image_url=artist_data['images'][0]['url'] if artist_data['images'] else None,
                    spotify_url=artist_data['external_urls']['spotify']
                )
                print(f"✅ Created/updated artist node: {artist_data['name']}")
                
            except Exception as e:
                print(f"❌ Error creating artist node: {e}")
    
    def create_era_album_node(self, era_data, artist_id):
        """Create consolidated era album node with comprehensive metadata"""
        main_album = era_data['main_album']
        era_name = era_data['era_name']
        all_albums = era_data['albums']
        
        with self.driver.session() as session:
            try:
                cypher = """
                MATCH (a:Artist {spotify_id: $artist_id})
                MERGE (al:Album {spotify_id: $album_id})
                SET al.name = $name,
                    al.era_name = $era_name,
                    al.release_date = $release_date,
                    al.total_tracks = $total_tracks,
                    al.album_type = $album_type,
                    al.genres = $genres,
                    al.popularity = $popularity,
                    al.label = $label,
                    al.release_date_precision = $release_date_precision,
                    al.available_markets = $available_markets,
                    al.copyrights = $copyrights,
                    al.external_ids = $external_ids,
                    al.album_group = $album_group,
                    al.image_url = $image_url,
                    al.spotify_url = $spotify_url,
                    al.era_albums = $era_albums,
                    al.updated_at = datetime()
                MERGE (a)-[:RELEASED]->(al)
                RETURN al
                """
                
                # Prepare comprehensive metadata
                copyrights_json = json.dumps([
                    {'text': c.get('text', ''), 'type': c.get('type', '')} 
                    for c in main_album.get('copyrights', [])
                ])
                
                external_ids_json = json.dumps(main_album.get('external_ids', {}))
                
                era_albums_json = json.dumps([
                    {'name': album.get('name', ''), 'type': album.get('album_type', ''), 'id': album.get('id', '')}
                    for album in all_albums
                ])
                
                session.run(cypher,
                    artist_id=artist_id,
                    album_id=main_album['id'],
                    name=main_album['name'],
                    era_name=era_name,
                    release_date=main_album.get('release_date', ''),
                    total_tracks=main_album.get('total_tracks', 0),
                    album_type=main_album.get('album_type', ''),
                    genres=main_album.get('genres', []),
                    popularity=main_album.get('popularity', 0),
                    label=main_album.get('label', ''),
                    release_date_precision=main_album.get('release_date_precision', ''),
                    available_markets=main_album.get('available_markets', []),
                    copyrights=copyrights_json,
                    external_ids=external_ids_json,
                    album_group=main_album.get('album_group', ''),
                    image_url=main_album['images'][0]['url'] if main_album.get('images') else None,
                    spotify_url=main_album.get('external_urls', {}).get('spotify', ''),
                    era_albums=era_albums_json
                )
                print(f"✅ Created/updated era album node: {era_name} (main: {main_album['name']})")
                
            except Exception as e:
                print(f"❌ Error creating era album node: {e}")
    
    def create_consolidated_track_node(self, track_data, era_album_id, source_albums, era_name):
        """Create track node with comprehensive tags and audio features"""
        with self.driver.session() as session:
            try:
                # Generate comprehensive tags
                track_tags = self.era_manager.generate_track_tags(track_data, source_albums)
                
                cypher = """
                MATCH (al:Album {spotify_id: $album_id})
                MERGE (t:Track {spotify_id: $track_id})
                SET t.name = $name,
                    t.duration_ms = $duration_ms,
                    t.explicit = $explicit,
                    t.track_number = $track_number,
                    t.preview_url = $preview_url,
                    t.spotify_url = $spotify_url,
                    t.era_name = $era_name,
                    t.track_tags = $track_tags,
                    t.source_albums = $source_albums_json,
                    t.disc_number = $disc_number,
                    t.is_local = $is_local,
                    t.updated_at = datetime()
                """
                
                # Add audio features if available
                if 'audio_features' in track_data and track_data['audio_features']:
                    af = track_data['audio_features']
                    cypher += """
                    SET t.danceability = $danceability,
                        t.energy = $energy,
                        t.valence = $valence,
                        t.tempo = $tempo,
                        t.acousticness = $acousticness,
                        t.instrumentalness = $instrumentalness,
                        t.speechiness = $speechiness,
                        t.liveness = $liveness,
                        t.loudness = $loudness,
                        t.key = $key,
                        t.mode = $mode,
                        t.time_signature = $time_signature
                    """
                
                cypher += """
                MERGE (al)-[:CONTAINS {track_number: $track_number, era_name: $era_name}]->(t)
                RETURN t
                """
                
                # Prepare source albums metadata
                source_albums_json = json.dumps([
                    {
                        'name': album.get('name', ''),
                        'type': album.get('album_type', ''),
                        'id': album.get('id', ''),
                        'release_date': album.get('release_date', '')
                    }
                    for album in source_albums
                ])
                
                params = {
                    'album_id': era_album_id,
                    'track_id': track_data['id'],
                    'name': track_data['name'],
                    'duration_ms': track_data.get('duration_ms', 0),
                    'explicit': track_data.get('explicit', False),
                    'track_number': track_data.get('track_number', 1),
                    'preview_url': track_data.get('preview_url', ''),
                    'spotify_url': track_data.get('external_urls', {}).get('spotify', ''),
                    'era_name': era_name,
                    'track_tags': track_tags,
                    'source_albums_json': source_albums_json,
                    'disc_number': track_data.get('disc_number', 1),
                    'is_local': track_data.get('is_local', False)
                }
                
                # Add audio features to params if available
                if 'audio_features' in track_data and track_data['audio_features']:
                    af = track_data['audio_features']
                    params.update({
                        'danceability': af.get('danceability'),
                        'energy': af.get('energy'),
                        'valence': af.get('valence'),
                        'tempo': af.get('tempo'),
                        'acousticness': af.get('acousticness'),
                        'instrumentalness': af.get('instrumentalness'),
                        'speechiness': af.get('speechiness'),
                        'liveness': af.get('liveness'),
                        'loudness': af.get('loudness'),
                        'key': af.get('key'),
                        'mode': af.get('mode'),
                        'time_signature': af.get('time_signature')
                    })
                
                session.run(cypher, **params)
                print(f"✅ Created/updated track: {track_data['name']} (tags: {', '.join(track_tags[:3])}{'...' if len(track_tags) > 3 else ''})")
                
            except Exception as e:
                print(f"❌ Error creating track node: {e}")
    
    def consolidate_era_tracks(self, era_data):
        """Consolidate all tracks from multiple albums in an era"""
        all_tracks = {}  # track_id -> track_data with source albums
        
        print(f"📀 Consolidating tracks for era: {era_data['era_name']}")
        
        for album in era_data['albums']:
            print(f"   📀 Processing album: {album['name']} ({album.get('album_type', 'unknown')})")
            
            # Get tracks for this album
            tracks = self.get_album_tracks_comprehensive(album['id'])
            
            for track in tracks:
                track_id = track['id']
                track_name = track['name']
                
                if track_id in all_tracks:
                    # Track already exists, add this album as a source
                    all_tracks[track_id]['source_albums'].append(album)
                    print(f"      🔗 Track '{track_name}' also appears in {album['name']}")
                else:
                    # New track
                    track['source_albums'] = [album]
                    all_tracks[track_id] = track
                    print(f"      ✅ Added track: {track_name}")
            
            # Increased rate limiting between albums to prevent API limits
            time.sleep(1.0)
        
        print(f"   🎯 Era consolidation complete: {len(all_tracks)} unique tracks")
        return list(all_tracks.values())
    
    def process_artist_with_eras(self, artist_name):
        """Process a single artist with era-based consolidation"""
        print(f"\n🎤 Processing artist with era consolidation: {artist_name}")
        print("=" * 70)
        
        # Get artist info
        artist = self.get_artist_by_name(artist_name)
        if not artist:
            return False
        
        # Create artist node
        self.create_artist_node(artist)
        print(f"✅ Created artist node for: {artist['name']}")
        
        # Get all albums (comprehensive approach)
        print(f"📀 Fetching comprehensive album catalog...")
        albums = self.get_artist_albums_comprehensive(artist['id'], limit=100)
        
        if not albums:
            print(f"❌ No albums found for {artist_name}")
            return False
        
        print(f"📊 Found {len(albums)} total releases")
        
        # Detect eras
        print(f"🎭 Detecting natural eras in discography...")
        eras = self.era_manager.detect_eras(albums)
        
        print(f"🎯 Detected {len(eras)} eras:")
        for era in eras:
            main_album = era['main_album']
            album_count = len(era['albums'])
            print(f"   📀 {era['era_name']}: {album_count} releases (main: {main_album['name']})")
        
        # Process each era
        successful_eras = 0
        total_tracks = 0
        
        for i, era in enumerate(eras, 1):
            try:
                print(f"\n🎭 Processing Era {i}/{len(eras)}: {era['era_name']}")
                print("-" * 50)
                
                # Create consolidated era album node
                self.create_era_album_node(era, artist['id'])
                
                # Consolidate tracks from all albums in this era
                consolidated_tracks = self.consolidate_era_tracks(era)
                
                # Create track nodes with comprehensive tagging
                era_track_count = 0
                for track in consolidated_tracks:
                    try:
                        self.create_consolidated_track_node(
                            track, 
                            era['main_album']['id'],
                            track['source_albums'],
                            era['era_name']
                        )
                        era_track_count += 1
                    except Exception as e:
                        print(f"⚠️ Failed to create track {track.get('name', 'unknown')}: {e}")
                        continue
                
                print(f"✅ Era complete: {era_track_count} tracks processed")
                successful_eras += 1
                total_tracks += era_track_count
                
                # Increased rate limiting between eras
                if i < len(eras):
                    print("⏱️  Extended pause before next era...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ Error processing era {era['era_name']}: {e}")
                continue
        
        print(f"\n🎉 Artist processing complete!")
        print(f"✅ Successful eras: {successful_eras}/{len(eras)}")
        print(f"✅ Total tracks processed: {total_tracks}")
        print(f"✅ Data consolidated and stored with comprehensive tagging")
        
        return successful_eras > 0

    def process_artist(self, artist_name):
        """Legacy method - redirects to era-based processing"""
        return self.process_artist_with_eras(artist_name)

    def build_knowledge_graph(self, artist_names):
        """Build complete knowledge graph with era-based consolidation"""
        print("🎵 Starting Enhanced Spotify Knowledge Graph Builder")
        print("🎭 Using Era-Based Consolidation System")
        print("=" * 70)
        
        successful = 0
        failed = 0
        total_eras = 0
        total_tracks = 0
        
        for i, artist_name in enumerate(artist_names, 1):
            print(f"\n📊 Progress: {i}/{len(artist_names)} artists")
            print(f"🎯 Current success rate: {successful}/{i-1 if i > 1 else 1} artists" if i > 1 else "")
            
            try:
                if self.process_artist_with_eras(artist_name):
                    successful += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Fatal error processing {artist_name}: {e}")
                failed += 1
                continue
            
            # Significant rate limiting between artists
            if i < len(artist_names):
                print("⏱️  Extended wait before next artist...")
                time.sleep(10)
        
        print(f"\n" + "=" * 70)
        print("🎉 ENHANCED KNOWLEDGE GRAPH BUILD COMPLETE!")
        print("=" * 70)
        print(f"✅ Successfully processed: {successful} artists")
        print(f"❌ Failed to process: {failed} artists")
        print(f"🎭 Era-based consolidation: ACTIVE")
        print(f"🏷️  Comprehensive tagging system applied")
        print(f"📊 Enhanced metadata: CAPTURED")
        print(f"🗄️  Data stored in: {self.neo4j_uri}")
        print("🔍 View your data at: https://browser.neo4j.io/")
        print("🎯 Your Vue.js app can now query rich, consolidated music data!")
        
        return successful, failed

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            print("✅ Neo4j connection closed")

# Enhanced test function
def test_enhanced_spotify_builder():
    """Build enhanced knowledge graph with era consolidation"""
    
    # Artists from user's Reddit communities - optimized for era testing
    target_artists = [
        "Taylor Swift",      # Perfect for era testing (country->pop->folk->pop)
        "Kanye West",        # Clear eras (college dropout->graduation->808s->mbdtf->yeezus->pablo->ye->donda)
        "Billie Eilish",     # Emerging artist with clear phases
        "Eminem",            # Long career with distinct periods
        "Arctic Monkeys",    # Genre evolution across albums
        "BTS",               # International releases and repackages
        "Beyoncé",           # Solo career with distinct eras
        "Frank Ocean",       # Minimal but distinct releases
        "Harry Styles",      # Solo transition from 1D
        "Ariana Grande"      # Pop evolution
    ]
    
    print("🎵 Enhanced Music Besties - Era-Based Knowledge Graph Builder")
    print("=" * 80)
    print(f"🎭 Processing {len(target_artists)} artists with era consolidation")
    print("📊 Capturing comprehensive metadata and relationships")
    print("🏷️  Implementing universal tagging system")
    print("⏱️  Estimated completion time: 60-90 minutes")
    print("🗄️  Data will be stored in your Neo4j AuraDB instance")
    print("=" * 80)
    
    try:
        builder = SpotifyKnowledgeGraphBuilder()
        successful, failed = builder.build_knowledge_graph(target_artists)
        
        print("=" * 80)
        print("🎉 ENHANCED KNOWLEDGE GRAPH BUILD COMPLETE!")
        print("=" * 80)
        print(f"✅ Successfully processed: {successful} artists")
        print(f"❌ Failed to process: {failed} artists")
        print(f"🎭 Era-based consolidation: ACTIVE")
        print(f"🏷️  Universal tagging system: APPLIED")
        print(f"📊 Enhanced metadata: CAPTURED")
        print(f"🗄️  Data stored with comprehensive relationships")
        print("🔍 View your organized data at: https://browser.neo4j.io/")
        print("🎯 Ready for lyrics analysis pipeline integration!")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        print("💡 Check your .env file credentials and try again")
    finally:
        if 'builder' in locals():
            builder.close()

if __name__ == "__main__":
    test_enhanced_spotify_builder()
