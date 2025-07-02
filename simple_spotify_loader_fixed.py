#!/usr/bin/env python3
"""
Simple Spotify Data Loader - Phase 1 (Fixed & Tested)
Query AuraDB for artists needing data and load raw Spotify catalog
No era processing, just: Artist -> Albums -> Tracks
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j import GraphDatabase
import os
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class SimpleSpotifyLoader:
    def __init__(self):
        # Spotify setup
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not self.spotify_client_id or not self.spotify_client_secret:
            raise ValueError("❌ Spotify credentials not found in .env")
        
        # Neo4j setup
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not self.neo4j_uri or not self.neo4j_password:
            raise ValueError("❌ Neo4j credentials not found in .env")
        
        # Initialize connections
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup Spotify and Neo4j connections"""
        try:
            # Spotify
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.spotify_client_id,
                client_secret=self.spotify_client_secret
            )
            self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            
            # Neo4j
            self.driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
            
            print("✅ Connected to Spotify API and Neo4j AuraDB")
            
        except Exception as e:
            raise Exception(f"❌ Connection failed: {e}")
    
    def get_artists_needing_data(self, limit=None):
        """Query AuraDB for artists that need Spotify data"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist) 
            WHERE a.consolidated = true 
              AND a.reddit_present = true 
              AND a.spotify_loaded = false 
            RETURN a.name, a.spotify_rank, a.reddit_score 
            ORDER BY a.reddit_score DESC
            """
            
            if limit:
                cypher += f" LIMIT {limit}"
            
            results = session.run(cypher)
            artists = []
            
            for record in results:
                artists.append({
                    'name': record['a.name'],
                    'rank': record['a.spotify_rank'],
                    'reddit_score': record['a.reddit_score']
                })
            
            return artists
    
    def get_failed_artists_needing_cleanup(self):
        """Get artists with empty catalogs that need cleanup"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist) 
            WHERE a.consolidated = true 
              AND a.albums_count = 0 
              AND EXISTS((a)-[:RELEASED]->()) 
            RETURN a.name
            """
            
            results = session.run(cypher)
            return [record['a.name'] for record in results]
    
    def cleanup_failed_artist(self, artist_name):
        """Remove existing empty album/track data for failed artist"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist {name: $name})-[:RELEASED]->(al:Album)
            OPTIONAL MATCH (al)-[:CONTAINS]->(t:Track)
            DETACH DELETE al, t
            """
            session.run(cypher, name=artist_name)
            print(f"🧹 Cleaned up empty data for: {artist_name}")
    
    def search_artist(self, artist_name):
        """Search for artist on Spotify"""
        try:
            results = self.spotify.search(q=artist_name, type='artist', limit=1)
            if results['artists']['items']:
                return results['artists']['items'][0]
            return None
        except Exception as e:
            print(f"❌ Error searching for {artist_name}: {e}")
            return None
    
    def get_artist_albums(self, artist_id, limit=50):
        """Get all albums for an artist"""
        try:
            albums = []
            offset = 0
            
            while True:
                results = self.spotify.artist_albums(
                    artist_id, 
                    album_type='album,single,compilation', 
                    limit=limit, 
                    offset=offset
                )
                
                if not results['items']:
                    break
                
                albums.extend(results['items'])
                
                if len(results['items']) < limit:
                    break
                
                offset += limit
                time.sleep(0.1)  # Rate limiting
            
            return albums
        except Exception as e:
            print(f"❌ Error getting albums: {e}")
            return []
    
    def get_album_tracks(self, album_id):
        """Get all tracks for an album"""
        try:
            tracks = []
            offset = 0
            limit = 50
            
            while True:
                results = self.spotify.album_tracks(album_id, limit=limit, offset=offset)
                
                if not results['items']:
                    break
                
                tracks.extend(results['items'])
                
                if len(results['items']) < limit:
                    break
                
                offset += limit
                time.sleep(0.05)  # Rate limiting
            
            return tracks
        except Exception as e:
            print(f"❌ Error getting tracks for album {album_id}: {e}")
            return []
    
    def create_album_node(self, album_data, artist_name):
        """Create simple album node - FIXED VERSION"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist {name: $artist_name})
            CREATE (al:Album {
                id: $album_id,
                name: $name,
                release_date: $release_date,
                album_type: $album_type,
                total_tracks: $total_tracks,
                created_date: datetime()
            })
            CREATE (a)-[:RELEASED]->(al)
            RETURN al.id as album_id
            """
            
            try:
                result = session.run(cypher,
                    artist_name=artist_name,
                    album_id=album_data['id'],
                    name=album_data['name'],
                    release_date=album_data.get('release_date', ''),
                    album_type=album_data.get('album_type', ''),
                    total_tracks=album_data.get('total_tracks', 0)
                )
                
                record = result.single()
                if record:
                    return record['album_id']
                else:
                    print(f"⚠️ No record returned for album: {album_data['name']}")
                    return None
                    
            except Exception as e:
                print(f"❌ Error creating album node: {e}")
                return None
    
    def create_track_node(self, track_data, album_id):
        """Create simple track node - FIXED VERSION"""
        with self.driver.session() as session:
            cypher = """
            MATCH (al:Album {id: $album_id})
            CREATE (t:Track {
                id: $track_id,
                name: $name,
                track_number: $track_number,
                duration_ms: $duration_ms,
                explicit: $explicit,
                created_date: datetime()
            })
            CREATE (al)-[:CONTAINS]->(t)
            RETURN t.id as track_id
            """
            
            try:
                result = session.run(cypher,
                    album_id=album_id,
                    track_id=track_data['id'],
                    name=track_data['name'],
                    track_number=track_data.get('track_number', 0),
                    duration_ms=track_data.get('duration_ms', 0),
                    explicit=track_data.get('explicit', False)
                )
                
                return result.single() is not None
                
            except Exception as e:
                print(f"❌ Error creating track node: {e}")
                return False
    
    def update_artist_status(self, artist_name, albums_count, tracks_count):
        """Update artist with loaded data status"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist {name: $name})
            SET a.spotify_loaded = true,
                a.albums_count = $albums_count,
                a.tracks_count = $tracks_count,
                a.last_spotify_update = datetime()
            """
            session.run(cypher, 
                name=artist_name, 
                albums_count=albums_count, 
                tracks_count=tracks_count
            )
    
    def process_artist(self, artist_name):
        """Process single artist - simple approach"""
        print(f"\n🎤 Processing: {artist_name}")
        print("-" * 40)
        
        # Search for artist
        artist_data = self.search_artist(artist_name)
        if not artist_data:
            print(f"❌ Artist not found on Spotify: {artist_name}")
            return False
        
        print(f"✅ Found artist: {artist_data['name']}")
        
        # Get albums
        print("📀 Fetching albums...")
        albums = self.get_artist_albums(artist_data['id'])
        
        if not albums:
            print("❌ No albums found")
            return False
        
        print(f"📊 Found {len(albums)} albums")
        
        # Process albums and tracks
        total_tracks = 0
        successful_albums = 0
        
        for i, album in enumerate(albums, 1):
            try:
                print(f"  📀 {i}/{len(albums)}: {album['name']}")
                
                # Create album node
                album_id = self.create_album_node(album, artist_name)
                if not album_id:
                    print(f"    ❌ Failed to create album node")
                    continue
                
                # Get tracks for this album
                tracks = self.get_album_tracks(album['id'])
                
                if not tracks:
                    print(f"    ⚠️ No tracks found for album")
                    continue
                
                # Create track nodes
                track_success_count = 0
                for track in tracks:
                    if self.create_track_node(track, album_id):
                        track_success_count += 1
                        total_tracks += 1
                
                successful_albums += 1
                print(f"    ✅ Added {track_success_count} tracks")
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"    ❌ Failed to process album: {e}")
                continue
        
        # Update artist status
        if successful_albums > 0:
            self.update_artist_status(artist_name, successful_albums, total_tracks)
            print(f"🎉 Complete: {successful_albums} albums, {total_tracks} tracks")
            return True
        else:
            print(f"❌ No albums processed successfully")
            return False
    
    def run_batch_processing(self, batch_size=3):
        """Run batch processing of artists needing data"""
        print("🎵 Simple Spotify Loader - Phase 1 (Fixed)")
        print("=" * 50)
        
        # First, clean up failed artists
        print("🧹 Cleaning up failed artists...")
        failed_artists = self.get_failed_artists_needing_cleanup()
        
        for artist in failed_artists:
            self.cleanup_failed_artist(artist)
        
        if failed_artists:
            print(f"✅ Cleaned up {len(failed_artists)} failed artists")
        
        # Get artists needing data
        artists_to_process = self.get_artists_needing_data(limit=batch_size)
        
        if not artists_to_process:
            print("✅ No artists need processing")
            return
        
        print(f"\n🎯 Processing {len(artists_to_process)} artists:")
        for artist in artists_to_process:
            print(f"  {artist['rank']:3d}. {artist['name']} (Reddit Score: {artist['reddit_score']})")
        
        # Process each artist
        successful = 0
        failed = 0
        
        for i, artist in enumerate(artists_to_process, 1):
            print(f"\n📊 Progress: {i}/{len(artists_to_process)}")
            
            try:
                if self.process_artist(artist['name']):
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Fatal error processing {artist['name']}: {e}")
                failed += 1
            
            # Rest between artists
            if i < len(artists_to_process):
                print("⏱️  Brief pause...")
                time.sleep(2)
        
        print(f"\n" + "=" * 50)
        print("🎉 BATCH PROCESSING COMPLETE!")
        print(f"✅ Successfully processed: {successful} artists")
        print(f"❌ Failed to process: {failed} artists")
        
        # Show next batch
        remaining = self.get_artists_needing_data(limit=3)
        if remaining:
            print(f"\n🔄 Next batch ready ({len(remaining)} artists)")
            for artist in remaining:
                print(f"  {artist['rank']:3d}. {artist['name']}")
        else:
            print(f"\n🎯 All Reddit artists processed!")
    
    def close(self):
        """Close connections"""
        if self.driver:
            self.driver.close()
            print("✅ Connections closed")

def main():
    try:
        loader = SimpleSpotifyLoader()
        
        # Process a small batch to start
        loader.run_batch_processing(batch_size=3)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'loader' in locals():
            loader.close()

if __name__ == "__main__":
    main() 