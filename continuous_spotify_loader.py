#!/usr/bin/env python3
"""
Continuous Spotify Data Loader
Process artists one by one, highest Reddit priority first
Continue until all Reddit artists are complete or error occurs
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

class ContinuousSpotifyLoader:
    def __init__(self):
        # Setup connections
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.spotify_client_id, self.spotify_client_secret, self.neo4j_uri, self.neo4j_password]):
            raise ValueError("❌ Missing credentials in .env")
        
        self._setup_connections()
    
    def _setup_connections(self):
        """Setup connections"""
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.spotify_client_id,
            client_secret=self.spotify_client_secret
        )
        self.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        self.driver = GraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
        print("✅ Connected to Spotify API and Neo4j AuraDB")
    
    def get_next_artist_to_process(self):
        """Get the highest priority artist that needs processing"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist) 
            WHERE a.consolidated = true 
              AND a.reddit_present = true 
              AND a.spotify_loaded = false 
            RETURN a.name, a.spotify_rank, a.reddit_score 
            ORDER BY a.reddit_score DESC 
            LIMIT 1
            """
            
            result = session.run(cypher)
            record = result.single()
            
            if record:
                return {
                    'name': record['a.name'],
                    'rank': record['a.spotify_rank'],
                    'reddit_score': record['a.reddit_score']
                }
            return None
    
    def get_processing_stats(self):
        """Get current processing statistics"""
        with self.driver.session() as session:
            cypher = """
            MATCH (a:Artist) 
            WHERE a.consolidated = true AND a.reddit_present = true
            RETURN a.spotify_loaded as loaded, count(*) as count
            """
            
            results = session.run(cypher)
            stats = {'loaded': 0, 'pending': 0}
            
            for record in results:
                if record['loaded']:
                    stats['loaded'] = record['count']
                else:
                    stats['pending'] = record['count']
            
            return stats
    
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
    
    def get_artist_albums(self, artist_id):
        """Get all albums for an artist"""
        try:
            albums = []
            offset = 0
            limit = 50
            
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
                time.sleep(0.1)
            
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
                time.sleep(0.05)
            
            return tracks
        except Exception as e:
            print(f"❌ Error getting tracks for album {album_id}: {e}")
            return []
    
    def create_album_node(self, album_data, artist_name):
        """Create album node"""
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
                return record['album_id'] if record else None
                
            except Exception as e:
                print(f"❌ Error creating album node: {e}")
                return None
    
    def create_track_node(self, track_data, album_id):
        """Create track node"""
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
            """
            
            try:
                session.run(cypher,
                    album_id=album_id,
                    track_id=track_data['id'],
                    name=track_data['name'],
                    track_number=track_data.get('track_number', 0),
                    duration_ms=track_data.get('duration_ms', 0),
                    explicit=track_data.get('explicit', False)
                )
                return True
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
    
    def process_single_artist(self, artist_info):
        """Process a single artist completely"""
        artist_name = artist_info['name']
        rank = artist_info['rank']
        reddit_score = artist_info['reddit_score']
        
        print(f"\n🎤 Processing: {artist_name}")
        print(f"📊 Rank: #{rank} | Reddit Score: {reddit_score}")
        print("-" * 50)
        
        # Search for artist
        artist_data = self.search_artist(artist_name)
        if not artist_data:
            print(f"❌ Artist not found on Spotify: {artist_name}")
            return False, "Artist not found on Spotify"
        
        print(f"✅ Found artist: {artist_data['name']} (ID: {artist_data['id']})")
        
        # Get albums
        print("📀 Fetching albums...")
        albums = self.get_artist_albums(artist_data['id'])
        
        if not albums:
            print("❌ No albums found")
            return False, "No albums found"
        
        print(f"📊 Found {len(albums)} albums")
        
        # Process albums and tracks
        total_tracks = 0
        successful_albums = 0
        
        for i, album in enumerate(albums, 1):
            try:
                album_name = album['name'][:50] + "..." if len(album['name']) > 50 else album['name']
                print(f"  📀 {i:2d}/{len(albums)}: {album_name}")
                
                # Create album node
                album_id = self.create_album_node(album, artist_name)
                if not album_id:
                    print(f"    ❌ Failed to create album node")
                    continue
                
                # Get tracks for this album
                tracks = self.get_album_tracks(album['id'])
                
                if not tracks:
                    print(f"    ⚠️ No tracks found")
                    continue
                
                # Create track nodes
                track_success_count = 0
                for track in tracks:
                    if self.create_track_node(track, album_id):
                        track_success_count += 1
                        total_tracks += 1
                
                successful_albums += 1
                print(f"    ✅ Added {track_success_count} tracks")
                
                # Brief pause to avoid overwhelming
                time.sleep(0.1)
                
            except Exception as e:
                print(f"    ❌ Failed to process album: {e}")
                continue
        
        if successful_albums > 0:
            # Update artist status
            self.update_artist_status(artist_name, successful_albums, total_tracks)
            print(f"\n🎉 SUCCESS: {successful_albums} albums, {total_tracks} tracks")
            return True, f"{successful_albums} albums, {total_tracks} tracks"
        else:
            print(f"\n❌ FAILED: No albums processed successfully")
            return False, "No albums processed successfully"
    
    def run_continuous_processing(self):
        """Run continuous processing until all Reddit artists are done"""
        print("🎵 Continuous Spotify Loader")
        print("🎯 Processing artists by Reddit priority until complete")
        print("=" * 60)
        
        # Initial stats
        stats = self.get_processing_stats()
        total_reddit_artists = stats['loaded'] + stats['pending']
        
        print(f"📊 Reddit Artists Status:")
        print(f"   ✅ Already loaded: {stats['loaded']}")
        print(f"   ⏳ Pending: {stats['pending']}")
        print(f"   📈 Total: {total_reddit_artists}")
        
        successful = 0
        failed = 0
        total_processed = 0
        
        while True:
            # Get next artist to process
            next_artist = self.get_next_artist_to_process()
            
            if not next_artist:
                print(f"\n🎉 ALL REDDIT ARTISTS COMPLETE!")
                break
            
            total_processed += 1
            
            print(f"\n📊 Progress: {stats['loaded'] + total_processed}/{total_reddit_artists} artists")
            
            try:
                success, message = self.process_single_artist(next_artist)
                
                if success:
                    successful += 1
                    print(f"✅ Artist #{total_processed} complete: {message}")
                else:
                    failed += 1
                    print(f"❌ Artist #{total_processed} failed: {message}")
                    
                    # Stop on errors as requested
                    print(f"\n⚠️ STOPPING due to error on {next_artist['name']}")
                    break
                
            except Exception as e:
                failed += 1
                print(f"❌ Fatal error processing {next_artist['name']}: {e}")
                print(f"\n⚠️ STOPPING due to fatal error")
                break
            
            # Brief pause between artists
            print("⏱️  Brief pause before next artist...")
            time.sleep(2)
        
        # Final summary
        print(f"\n" + "=" * 60)
        print("🎵 CONTINUOUS PROCESSING SUMMARY")
        print("=" * 60)
        print(f"✅ Successfully processed: {successful} artists")
        print(f"❌ Failed to process: {failed} artists")
        print(f"📊 Total processed this run: {total_processed} artists")
        
        # Final stats
        final_stats = self.get_processing_stats()
        print(f"\n📈 Final Status:")
        print(f"   ✅ Total loaded: {final_stats['loaded']} artists")
        print(f"   ⏳ Still pending: {final_stats['pending']} artists")
        
        if final_stats['pending'] == 0:
            print(f"\n🎉 ALL REDDIT ARTISTS COMPLETE!")
        else:
            print(f"\n🔄 {final_stats['pending']} artists remaining")
    
    def close(self):
        """Close connections"""
        if self.driver:
            self.driver.close()

def main():
    try:
        loader = ContinuousSpotifyLoader()
        loader.run_continuous_processing()
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
    finally:
        if 'loader' in locals():
            loader.close()

if __name__ == "__main__":
    main() 