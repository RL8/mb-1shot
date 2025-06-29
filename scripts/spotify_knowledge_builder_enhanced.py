#!/usr/bin/env python3
"""
Enhanced Spotify Knowledge Graph Builder
Builds a comprehensive music knowledge graph using Spotify API
"""

import os
import requests
import base64
import json
import time
from neo4j import GraphDatabase
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SpotifyKnowledgeGraphBuilder:
    def __init__(self):
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        # Comprehensive list of 20 popular artists
        self.target_artists = [
            "Taylor Swift", "Ed Sheeran", "Billie Eilish", "The Weeknd",
            "Ariana Grande", "Drake", "Post Malone", "Olivia Rodrigo",
            "Harry Styles", "Dua Lipa", "Bad Bunny", "BTS",
            "Adele", "Justin Bieber", "Kanye West", "Eminem",
            "Beyoncé", "Rihanna", "Bruno Mars", "Lady Gaga"
        ]
        
        self.access_token = None
        self.driver = None
        
    def authenticate_spotify(self) -> bool:
        """Get Spotify access token using Client Credentials flow"""
        try:
            auth_string = f"{self.client_id}:{self.client_secret}"
            auth_bytes = auth_string.encode('utf-8')
            auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            url = "https://accounts.spotify.com/api/token"
            headers = {
                "Authorization": f"Basic {auth_base64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            print("✅ Spotify authentication successful")
            return True
            
        except Exception as e:
            print(f"❌ Spotify authentication failed: {e}")
            return False
    
    def connect_neo4j(self) -> bool:
        """Connect to Neo4j AuraDB"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✅ Neo4j connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            return False
    
    def search_artist(self, artist_name: str) -> Optional[Dict]:
        """Search for artist on Spotify"""
        try:
            url = "https://api.spotify.com/v1/search"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "q": artist_name,
                "type": "artist",
                "limit": 1
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            artists = data.get('artists', {}).get('items', [])
            
            if artists:
                return artists[0]
            return None
            
        except Exception as e:
            print(f"❌ Error searching for artist {artist_name}: {e}")
            return None
    
    def get_artist_albums(self, artist_id: str, limit: int = 20) -> List[Dict]:
        """Get albums for an artist"""
        try:
            url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "include_groups": "album,single",
                "limit": limit,
                "market": "US"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            print(f"❌ Error getting albums for artist {artist_id}: {e}")
            return []
    
    def get_album_tracks(self, album_id: str, limit: int = 50) -> List[Dict]:
        """Get tracks for an album"""
        try:
            url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {"limit": limit}
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            print(f"❌ Error getting tracks for album {album_id}: {e}")
            return []
    
    def create_artist_node(self, artist_data: Dict) -> bool:
        """Create artist node in Neo4j"""
        try:
            with self.driver.session() as session:
                query = """
                MERGE (a:Artist {spotify_id: $spotify_id})
                SET a.name = $name,
                    a.popularity = $popularity,
                    a.followers = $followers,
                    a.genres = $genres,
                    a.external_urls = $external_urls,
                    a.updated_at = datetime()
                RETURN a
                """
                
                session.run(query, {
                    'spotify_id': artist_data['id'],
                    'name': artist_data['name'],
                    'popularity': artist_data.get('popularity', 0),
                    'followers': artist_data.get('followers', {}).get('total', 0),
                    'genres': artist_data.get('genres', []),
                    'external_urls': json.dumps(artist_data.get('external_urls', {}))
                })
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating artist node: {e}")
            return False
    
    def create_album_node(self, album_data: Dict, artist_id: str) -> bool:
        """Create album node and link to artist"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (a:Artist {spotify_id: $artist_id})
                MERGE (al:Album {spotify_id: $album_id})
                SET al.name = $name,
                    al.release_date = $release_date,
                    al.total_tracks = $total_tracks,
                    al.album_type = $album_type,
                    al.external_urls = $external_urls,
                    al.updated_at = datetime()
                MERGE (a)-[:HAS_ALBUM]->(al)
                RETURN al
                """
                
                session.run(query, {
                    'artist_id': artist_id,
                    'album_id': album_data['id'],
                    'name': album_data['name'],
                    'release_date': album_data.get('release_date', ''),
                    'total_tracks': album_data.get('total_tracks', 0),
                    'album_type': album_data.get('album_type', ''),
                    'external_urls': json.dumps(album_data.get('external_urls', {}))
                })
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating album node: {e}")
            return False
    
    def create_track_node(self, track_data: Dict, album_id: str) -> bool:
        """Create track node and link to album"""
        try:
            with self.driver.session() as session:
                query = """
                MATCH (al:Album {spotify_id: $album_id})
                MERGE (t:Track {spotify_id: $track_id})
                SET t.name = $name,
                    t.track_number = $track_number,
                    t.duration_ms = $duration_ms,
                    t.explicit = $explicit,
                    t.preview_url = $preview_url,
                    t.external_urls = $external_urls,
                    t.updated_at = datetime()
                MERGE (al)-[:HAS_TRACK]->(t)
                RETURN t
                """
                
                session.run(query, {
                    'album_id': album_id,
                    'track_id': track_data['id'],
                    'name': track_data['name'],
                    'track_number': track_data.get('track_number', 0),
                    'duration_ms': track_data.get('duration_ms', 0),
                    'explicit': track_data.get('explicit', False),
                    'preview_url': track_data.get('preview_url', ''),
                    'external_urls': json.dumps(track_data.get('external_urls', {}))
                })
                
            return True
            
        except Exception as e:
            print(f"❌ Error creating track node: {e}")
            return False
    
    def process_artist(self, artist_name: str) -> Dict[str, int]:
        """Process a single artist and all their data"""
        stats = {'artists': 0, 'albums': 0, 'tracks': 0}
        
        print(f"\n🎵 Processing: {artist_name}")
        
        # Search for artist
        artist_data = self.search_artist(artist_name)
        if not artist_data:
            print(f"❌ Artist not found: {artist_name}")
            return stats
        
        print(f"✅ Found: {artist_data['name']} (Popularity: {artist_data.get('popularity', 'N/A')})")
        
        # Create artist node
        if self.create_artist_node(artist_data):
            stats['artists'] += 1
            print(f"✅ Created artist node")
        
        # Get and process albums
        albums = self.get_artist_albums(artist_data['id'])
        print(f"📀 Found {len(albums)} albums")
        
        for album in albums[:10]:  # Limit to first 10 albums to avoid rate limits
            if self.create_album_node(album, artist_data['id']):
                stats['albums'] += 1
                
                # Get and process tracks for each album
                tracks = self.get_album_tracks(album['id'])
                track_count = 0
                
                for track in tracks[:5]:  # Limit to first 5 tracks per album
                    if self.create_track_node(track, album['id']):
                        stats['tracks'] += 1
                        track_count += 1
                
                print(f"   📀 {album['name']} ({album.get('release_date', 'N/A')}) - {track_count} tracks")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        return stats
    
    def build_knowledge_graph(self):
        """Build the complete music knowledge graph"""
        print("🚀 Starting Enhanced Spotify Knowledge Graph Build")
        print("="*60)
        
        # Initialize connections
        if not self.authenticate_spotify():
            return False
        
        if not self.connect_neo4j():
            return False
        
        # Initialize Neo4j schema
        self.initialize_schema()
        
        # Process all artists
        total_stats = {'artists': 0, 'albums': 0, 'tracks': 0}
        
        for i, artist_name in enumerate(self.target_artists, 1):
            print(f"\n📊 Progress: {i}/{len(self.target_artists)} artists")
            
            try:
                stats = self.process_artist(artist_name)
                
                # Update totals
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                # Rate limiting - wait between artists
                if i < len(self.target_artists):
                    print("⏳ Waiting to avoid rate limits...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error processing {artist_name}: {e}")
                continue
        
        # Final summary
        print("\n" + "="*60)
        print("🎉 KNOWLEDGE GRAPH BUILD COMPLETE!")
        print("="*60)
        print(f"✅ Artists Created: {total_stats['artists']}")
        print(f"✅ Albums Created: {total_stats['albums']}")
        print(f"✅ Tracks Created: {total_stats['tracks']}")
        print(f"✅ Total Nodes: {sum(total_stats.values())}")
        
        # Close Neo4j connection
        if self.driver:
            self.driver.close()
        
        return True
    
    def initialize_schema(self):
        """Create indexes and constraints for better performance"""
        try:
            with self.driver.session() as session:
                # Create constraints and indexes
                constraints = [
                    "CREATE CONSTRAINT artist_spotify_id IF NOT EXISTS FOR (a:Artist) REQUIRE a.spotify_id IS UNIQUE",
                    "CREATE CONSTRAINT album_spotify_id IF NOT EXISTS FOR (al:Album) REQUIRE al.spotify_id IS UNIQUE", 
                    "CREATE CONSTRAINT track_spotify_id IF NOT EXISTS FOR (t:Track) REQUIRE t.spotify_id IS UNIQUE"
                ]
                
                for constraint in constraints:
                    try:
                        session.run(constraint)
                    except Exception:
                        pass  # Constraint might already exist
                        
            print("✅ Database schema initialized")
            
        except Exception as e:
            print(f"⚠️ Schema initialization warning: {e}")

def main():
    builder = SpotifyKnowledgeGraphBuilder()
    success = builder.build_knowledge_graph()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Check your Neo4j database for the new nodes")
        print("2. Run frontend integration to display the data")
        print("3. Add more sophisticated music recommendations")
        return 0
    else:
        print("\n❌ Knowledge graph build failed")
        return 1

if __name__ == "__main__":
    exit(main()) 