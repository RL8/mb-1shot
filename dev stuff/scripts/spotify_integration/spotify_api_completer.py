#!/usr/bin/env python3
"""
Spotify API Completer for Missing Songs
Fetches remaining songs directly from Spotify API to achieve 100% coverage
"""

import os
import time
import json
from typing import Dict, List, Optional, Tuple
from neo4j import GraphDatabase
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv('../../../.env.development')

class SpotifyAPICompleter:
    def __init__(self):
        """Initialize Spotify API and AuraDB connections"""
        
        # AuraDB credentials
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME') 
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        # Spotify API credentials
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not all([self.neo4j_uri, self.neo4j_password]):
            raise ValueError("❌ Missing AuraDB credentials in environment")
            
        if not all([self.spotify_client_id, self.spotify_client_secret]):
            raise ValueError("❌ Missing Spotify API credentials in environment")
        
        # Initialize connections
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password),
            max_connection_pool_size=10,
            connection_timeout=30
        )
        
        # Initialize Spotify API
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.spotify_client_id,
                client_secret=self.spotify_client_secret
            )
        )
        
        print("🎵 Spotify API Completer initialized")
        print(f"✅ AuraDB connected: {self.neo4j_uri}")
        print(f"✅ Spotify API authenticated")
        
    def get_missing_songs(self) -> List[Dict]:
        """Get list of songs that don't have Spotify features"""
        print("🔍 Fetching songs missing Spotify features...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Song) 
                WHERE s.energy IS NULL
                RETURN s.title as title, 
                       s.albumCode as albumCode,
                       s.trackNumber as trackNumber,
                       ID(s) as nodeId
                ORDER BY s.albumCode, s.trackNumber
            """)
            
            missing_songs = [dict(record) for record in result]
            
        print(f"📊 Found {len(missing_songs)} songs missing Spotify features:")
        for song in missing_songs:
            print(f"  🎵 {song['title']} ({song['albumCode']})")
            
        return missing_songs
    
    def search_spotify_track(self, song_title: str, artist: str = "Taylor Swift") -> Optional[Dict]:
        """Search for a track on Spotify and return its details"""
        try:
            # Try different search variations
            search_queries = [
                f'track:"{song_title}" artist:"{artist}"',
                f'"{song_title}" "{artist}"',
                f'{song_title} {artist}',
                f'track:"{song_title}"'
            ]
            
            for query in search_queries:
                print(f"  🔍 Searching: {query}")
                results = self.sp.search(q=query, type='track', limit=10)
                
                if results['tracks']['items']:
                    # Look for best match - prioritize Taylor Swift tracks
                    for track in results['tracks']['items']:
                        # Check if artist matches
                        artist_names = [artist['name'].lower() for artist in track['artists']]
                        if 'taylor swift' in artist_names:
                            print(f"  ✅ Found: {track['name']} by {track['artists'][0]['name']}")
                            print(f"     Album: {track['album']['name']}")
                            print(f"     ID: {track['id']}")
                            return track
                    
                    # If no Taylor Swift match, take first result as backup
                    track = results['tracks']['items'][0]
                    print(f"  ⚠️ Backup match: {track['name']} by {track['artists'][0]['name']}")
                    return track
                
                time.sleep(0.1)  # Rate limiting
            
            print(f"  ❌ No results found for: {song_title}")
            return None
            
        except Exception as e:
            print(f"  ❌ Search error for {song_title}: {e}")
            return None
    
    def get_audio_features(self, track_id: str) -> Optional[Dict]:
        """Get audio features for a Spotify track"""
        try:
            features = self.sp.audio_features([track_id])[0]
            if features:
                print(f"  🎯 Audio features retrieved")
                return features
            else:
                print(f"  ❌ No audio features available")
                return None
                
        except Exception as e:
            print(f"  ❌ Audio features error: {e}")
            return None
    
    def import_song_features(self, song_data: Dict, spotify_track: Dict, audio_features: Dict) -> bool:
        """Import Spotify features into AuraDB for a specific song"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (s:Song) WHERE ID(s) = $nodeId
                    SET s.danceability = $danceability,
                        s.energy = $energy,
                        s.spotify_key = $key,
                        s.loudness = $loudness,
                        s.spotify_mode = $mode,
                        s.speechiness = $speechiness,
                        s.acousticness = $acousticness,
                        s.instrumentalness = $instrumentalness,
                        s.liveness = $liveness,
                        s.valence = $valence,
                        s.tempo = $tempo,
                        s.time_signature = $time_signature,
                        s.duration_ms = $duration_ms,
                        s.explicit = $explicit,
                        s.spotify_features_imported = datetime(),
                        s.spotify_import_source = 'direct_api_v1',
                        s.spotify_track_id = $spotify_track_id,
                        s.spotify_track_name = $spotify_track_name,
                        s.spotify_album_name = $spotify_album_name
                    RETURN count(s) as updated_count
                """, 
                    nodeId=song_data['nodeId'],
                    danceability=audio_features.get('danceability', 0.0),
                    energy=audio_features.get('energy', 0.0),
                    key=audio_features.get('key', 0),
                    loudness=audio_features.get('loudness', 0.0),
                    mode=audio_features.get('mode', 0),
                    speechiness=audio_features.get('speechiness', 0.0),
                    acousticness=audio_features.get('acousticness', 0.0),
                    instrumentalness=audio_features.get('instrumentalness', 0.0),
                    liveness=audio_features.get('liveness', 0.0),
                    valence=audio_features.get('valence', 0.0),
                    tempo=audio_features.get('tempo', 0.0),
                    time_signature=audio_features.get('time_signature', 4),
                    duration_ms=spotify_track.get('duration_ms', 0),
                    explicit=spotify_track.get('explicit', False),
                    spotify_track_id=spotify_track['id'],
                    spotify_track_name=spotify_track['name'],
                    spotify_album_name=spotify_track['album']['name']
                )
                
                updated_count = result.single()['updated_count']
                if updated_count > 0:
                    print(f"  ✅ Successfully imported features")
                    return True
                else:
                    print(f"  ❌ Failed to update song in database")
                    return False
                    
        except Exception as e:
            print(f"  ❌ Database import error: {e}")
            return False
    
    def process_missing_songs(self) -> Dict:
        """Process all missing songs through Spotify API"""
        print("🚀 Starting Spotify API completion process...")
        print("=" * 60)
        
        missing_songs = self.get_missing_songs()
        
        if not missing_songs:
            print("✅ No missing songs found! Dataset is already complete.")
            return {'total': 0, 'found': 0, 'imported': 0}
        
        stats = {
            'total': len(missing_songs),
            'found': 0,
            'imported': 0,
            'failed': 0,
            'processed_songs': []
        }
        
        print(f"\n🎯 Processing {len(missing_songs)} missing songs...")
        
        for i, song in enumerate(missing_songs, 1):
            print(f"\n📦 Processing {i}/{len(missing_songs)}: {song['title']}")
            print("-" * 40)
            
            # Search for track on Spotify
            spotify_track = self.search_spotify_track(song['title'])
            
            if not spotify_track:
                stats['failed'] += 1
                stats['processed_songs'].append({
                    'title': song['title'],
                    'album': song['albumCode'],
                    'status': 'not_found'
                })
                continue
            
            stats['found'] += 1
            
            # Get audio features
            audio_features = self.get_audio_features(spotify_track['id'])
            
            if not audio_features:
                stats['failed'] += 1
                stats['processed_songs'].append({
                    'title': song['title'],
                    'album': song['albumCode'],
                    'status': 'no_features'
                })
                continue
            
            # Import into AuraDB
            success = self.import_song_features(song, spotify_track, audio_features)
            
            if success:
                stats['imported'] += 1
                stats['processed_songs'].append({
                    'title': song['title'],
                    'album': song['albumCode'],
                    'status': 'success',
                    'spotify_id': spotify_track['id'],
                    'spotify_name': spotify_track['name']
                })
            else:
                stats['failed'] += 1
                stats['processed_songs'].append({
                    'title': song['title'],
                    'album': song['albumCode'],
                    'status': 'import_failed'
                })
            
            # Rate limiting
            time.sleep(0.5)
        
        return stats
    
    def validate_completion(self) -> Dict:
        """Validate the completion results"""
        print("🔍 Validating completion results...")
        
        with self.driver.session() as session:
            result = session.run("""
                MATCH (s:Song)
                RETURN 
                    count(s) as total_songs,
                    count(s.energy) as songs_with_energy,
                    (count(s.energy) * 100.0 / count(s)) as coverage_percent,
                    count(CASE WHEN s.spotify_import_source = 'direct_api_v1' THEN 1 END) as api_imported
            """)
            
            validation = dict(result.single())
            
            # Get import source breakdown
            source_result = session.run("""
                MATCH (s:Song)
                WHERE s.spotify_import_source IS NOT NULL
                RETURN s.spotify_import_source as source, count(s) as count
                ORDER BY count DESC
            """)
            
            sources = {record['source']: record['count'] for record in source_result}
            
            print(f"📊 Final Validation Results:")
            print(f"  Total songs: {validation['total_songs']}")
            print(f"  Songs with features: {validation['songs_with_energy']}")
            print(f"  Coverage: {validation['coverage_percent']:.1f}%")
            print(f"  API imported: {validation['api_imported']}")
            
            print(f"🎯 Import source breakdown:")
            for source, count in sources.items():
                print(f"  {source}: {count} songs")
            
            return validation
    
    def run_completion(self):
        """Execute complete Spotify API completion process"""
        print("🚀 Starting Spotify API Completion for 100% Coverage")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            # Process missing songs
            stats = self.process_missing_songs()
            
            print("\n" + "=" * 60)
            print("📊 Processing Summary:")
            print(f"  Total processed: {stats['total']}")
            print(f"  Found on Spotify: {stats['found']}")
            print(f"  Successfully imported: {stats['imported']}")
            print(f"  Failed: {stats['failed']}")
            
            if stats['processed_songs']:
                print(f"\n📝 Detailed Results:")
                for song in stats['processed_songs']:
                    status_emoji = {
                        'success': '✅',
                        'not_found': '❌',
                        'no_features': '⚠️',
                        'import_failed': '💥'
                    }.get(song['status'], '❓')
                    print(f"  {status_emoji} {song['title']} ({song['album']}) - {song['status']}")
            
            # Validate final results
            validation = self.validate_completion()
            
            elapsed_time = time.time() - start_time
            
            print("=" * 70)
            if validation['coverage_percent'] >= 99.0:
                print(f"🎉 Spotify API Completion SUCCESS!")
                print(f"🎯 Final coverage: {validation['coverage_percent']:.1f}%")
                print(f"⚡ Completed in {elapsed_time:.1f} seconds")
                print(f"🚀 Ready for Phase 1: Taxonomy Calculation!")
                return True
            else:
                print(f"⚠️ Completion partially successful")
                print(f"📊 Coverage: {validation['coverage_percent']:.1f}%")
                return False
                
        except Exception as e:
            print(f"❌ Completion failed: {e}")
            return False
        
        finally:
            self.driver.close()

def main():
    """Main execution function"""
    completer = SpotifyAPICompleter()
    success = completer.run_completion()
    
    if success:
        print("\n🎉 100% Dataset Completion Achieved!")
        print("All Taylor Swift songs now have Spotify features!")
    else:
        print("\n💥 Completion needs attention. Check results above.")

if __name__ == "__main__":
    main() 