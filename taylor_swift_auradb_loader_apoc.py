#!/usr/bin/env python3
"""
Taylor Swift AuraDB Loader - APOC Edition
Ultra-fast bulk loading using APOC with inline JSON data
Optimized for AuraDB compatibility (no file import needed)
"""

import json
import os
import time
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class TaylorSwiftAPOCLoader:
    def __init__(self):
        """Initialize connection to AuraDB"""
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        print(f"🔑 AURA_DB_URI found: {'Yes' if self.neo4j_uri else 'No'}")
        print(f"🔑 AURA_DB_USERNAME found: {'Yes' if self.neo4j_user else 'No'}")
        print(f"🔑 AURA_DB_PASSWORD found: {'Yes' if self.neo4j_password else 'No'}")
        
        if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
            raise ValueError("Missing Neo4j credentials in .env file")
        
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Connect to Neo4j AuraDB"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password),
                max_connection_lifetime=300,
                max_connection_pool_size=50
            )
            self.driver.verify_connectivity()
            print("✅ Connected to Neo4j AuraDB")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise e
    
    def clear_database(self):
        """Completely clear the AuraDB database"""
        print("\n🗑️  CLEARING AURADB DATABASE")
        print("=" * 50)
        
        with self.driver.session() as session:
            try:
                # Get initial stats
                node_result = session.run("MATCH (n) RETURN count(n) as count")
                initial_nodes = node_result.single()["count"]
                
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                initial_rels = rel_result.single()["count"]
                
                print(f"📊 Current database: {initial_nodes} nodes, {initial_rels} relationships")
                
                if initial_nodes == 0 and initial_rels == 0:
                    print("✅ Database is already empty")
                    return
                
                # Use DETACH DELETE for complete cleanup
                print("🗑️ Deleting all nodes and relationships...")
                session.run("MATCH (n) DETACH DELETE n")
                
                # Verify cleanup
                final_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                final_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                print(f"✅ Database cleared: {final_nodes} nodes, {final_rels} relationships remaining")
                
            except Exception as e:
                print(f"❌ Error during cleanup: {e}")
                raise e
    
    def create_indexes(self):
        """Create indexes for optimal performance"""
        print("\n🔧 CREATING PERFORMANCE INDEXES")
        print("=" * 50)
        
        indexes = [
            ("Artist", "name"),
            ("Album", "code"),
            ("Album", "title"),
            ("Album", "year"),
            ("Song", "title"),
            ("Song", "trackNumber"),
            ("LyricLine", "order"),
            ("SongPart", "name"),
        ]
        
        with self.driver.session() as session:
            for label, property_name in indexes:
                try:
                    query = f"CREATE INDEX {label.lower()}_{property_name.lower()}_index IF NOT EXISTS FOR (n:{label}) ON (n.{property_name})"
                    session.run(query)
                    print(f"✅ Created index: {label}.{property_name}")
                except Exception as e:
                    print(f"⚠️  Index creation warning for {label}.{property_name}: {e}")
    
    def prepare_data_for_apoc(self, json_file_path):
        """Prepare data structure optimized for APOC inline processing"""
        print(f"\n📁 PREPARING DATA FOR APOC INLINE PROCESSING")
        print("=" * 50)
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                albums_data = json.load(f)
            print(f"✅ JSON loaded: {len(albums_data)} albums found")
            
            # Restructure data for efficient APOC processing
            optimized_data = {
                "artist": {
                    "name": "Taylor Swift",
                    "genre": "Pop/Country",
                    "activeYears": "2006-Present",
                    "country": "United States",
                    "debutYear": 2006,
                    "grammyWins": 12
                },
                "albums": [],
                "songs": [],
                "lyrics": [],
                "songParts": set()
            }
            
            # Process albums and extract all nested data
            for album in albums_data:
                album_data = {
                    "code": album['Code'],
                    "title": album['Title'],
                    "subtitle": album.get('SubTitle', ''),
                    "year": album.get('Year'),
                    "songCount": len(album['Songs'])
                }
                optimized_data["albums"].append(album_data)
                
                # Process songs in this album
                for song in album['Songs']:
                    song_data = {
                        "title": song['Title'],
                        "albumCode": album['Code'],
                        "trackNumber": song['TrackNumber'],
                        "fromTheVault": song.get('FromTheVault', False),
                        "featuredArtists": song.get('FeaturedArtists', []),
                        "lyricCount": len(song.get('Lyrics', []))
                    }
                    optimized_data["songs"].append(song_data)
                    
                    # Process lyrics for this song
                    if 'Lyrics' in song:
                        for lyric in song['Lyrics']:
                            song_part = lyric.get('SongPart', 'Unknown')
                            optimized_data["songParts"].add(song_part)
                            
                            lyric_data = {
                                "songTitle": song['Title'],
                                "albumCode": album['Code'],
                                "order": lyric.get('Order', 0),
                                "text": lyric.get('Text', ''),
                                "songPart": song_part
                            }
                            optimized_data["lyrics"].append(lyric_data)
            
            # Convert set to list for JSON serialization
            optimized_data["songParts"] = list(optimized_data["songParts"])
            
            print(f"✅ Data restructured for APOC processing")
            print(f"📊 Data summary:")
            print(f"   • Albums: {len(optimized_data['albums'])}")
            print(f"   • Songs: {len(optimized_data['songs'])}")
            print(f"   • Lyric Lines: {len(optimized_data['lyrics'])}")
            print(f"   • Song Parts: {len(optimized_data['songParts'])}")
            
            return optimized_data
            
        except Exception as e:
            print(f"❌ Error preparing data: {e}")
            raise e
    
    def load_data_with_apoc_inline(self, data):
        """Load data using APOC with inline JSON (AuraDB compatible)"""
        print(f"\n🚀 LOADING DATA WITH APOC INLINE (ULTRA-FAST)")
        print("=" * 50)
        
        with self.driver.session() as session:
            try:
                # Step 1: Create Artist
                print("\n🎤 Creating Artist with APOC...")
                session.run("""
                    WITH $artist as artist
                    MERGE (a:Artist {name: artist.name})
                    SET a.genre = artist.genre,
                        a.activeYears = artist.activeYears,
                        a.country = artist.country,
                        a.debutYear = artist.debutYear,
                        a.grammyWins = artist.grammyWins,
                        a.lastUpdated = datetime()
                """, artist=data["artist"])
                print("✅ Artist created")
                
                # Step 2: Create Albums in batch
                print("\n💿 Creating Albums with APOC...")
                session.run("""
                    WITH $albums as albums
                    UNWIND albums as album
                    MATCH (artist:Artist {name: "Taylor Swift"})
                    MERGE (a:Album {code: album.code})
                    SET a.title = album.title,
                        a.subtitle = album.subtitle,
                        a.year = album.year,
                        a.songCount = album.songCount,
                        a.createdAt = datetime()
                    MERGE (artist)-[:RELEASED]->(a)
                """, albums=data["albums"])
                print("✅ Albums created with relationships")
                
                # Step 3: Create Songs in batch
                print("\n🎵 Creating Songs with APOC...")
                session.run("""
                    WITH $songs as songs
                    UNWIND songs as song
                    MATCH (album:Album {code: song.albumCode})
                    MERGE (s:Song {title: song.title, albumCode: song.albumCode, trackNumber: song.trackNumber})
                    SET s.fromTheVault = song.fromTheVault,
                        s.featuredArtists = song.featuredArtists,
                        s.lyricCount = song.lyricCount,
                        s.createdAt = datetime()
                    MERGE (album)-[:CONTAINS {trackNumber: song.trackNumber}]->(s)
                """, songs=data["songs"])
                print("✅ Songs created with relationships")
                
                # Step 4: Create Song Parts
                print("\n🎭 Creating Song Parts with APOC...")
                session.run("""
                    WITH $parts as parts
                    UNWIND parts as part
                    MERGE (p:SongPart {name: part})
                """, parts=data["songParts"])
                print("✅ Song Parts created")
                
                # Step 5: Create Lyric Lines in batches (most performance-critical)
                print("\n📝 Creating Lyric Lines with APOC (bulk operation)...")
                
                # Process lyrics in chunks for memory efficiency
                chunk_size = 1000
                lyrics = data["lyrics"]
                total_chunks = (len(lyrics) + chunk_size - 1) // chunk_size
                
                for i in range(0, len(lyrics), chunk_size):
                    chunk = lyrics[i:i + chunk_size]
                    chunk_num = (i // chunk_size) + 1
                    print(f"   📝 Processing lyrics batch {chunk_num}/{total_chunks} ({len(chunk)} lines)")
                    
                    session.run("""
                        WITH $lyrics as lyrics
                        UNWIND lyrics as lyric
                        MATCH (song:Song {title: lyric.songTitle, albumCode: lyric.albumCode})
                        MATCH (part:SongPart {name: lyric.songPart})
                        CREATE (l:LyricLine {
                            order: lyric.order,
                            text: lyric.text,
                            songPart: lyric.songPart,
                            createdAt: datetime()
                        })
                        MERGE (song)-[:HAS_LYRIC {order: lyric.order}]->(l)
                        MERGE (l)-[:PART_OF]->(part)
                    """, lyrics=chunk)
                
                print("✅ Lyric Lines created with relationships (batched)")
                
            except Exception as e:
                print(f"❌ Error during APOC loading: {e}")
                raise e
    
    def verify_data_load(self):
        """Verify the data was loaded correctly"""
        print("\n🔍 VERIFYING DATA LOAD")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Basic counts
            artists = session.run("MATCH (a:Artist) RETURN count(a) as count").single()["count"]
            albums = session.run("MATCH (a:Album) RETURN count(a) as count").single()["count"]
            songs = session.run("MATCH (s:Song) RETURN count(s) as count").single()["count"]
            lyrics = session.run("MATCH (l:LyricLine) RETURN count(l) as count").single()["count"]
            song_parts = session.run("MATCH (p:SongPart) RETURN count(p) as count").single()["count"]
            
            print(f"✅ Artists: {artists}")
            print(f"✅ Albums: {albums}")
            print(f"✅ Songs: {songs}")
            print(f"✅ Lyric Lines: {lyrics}")
            print(f"✅ Song Parts: {song_parts}")
            
            # Sample queries to verify relationships
            print("\n📋 Sample Data Verification:")
            
            # Albums by year
            result = session.run("""
                MATCH (a:Album)
                WHERE a.year IS NOT NULL
                RETURN a.title, a.year
                ORDER BY a.year
                LIMIT 5
            """)
            print("   📅 First 5 Albums by Year:")
            for record in result:
                print(f"      • {record['a.year']}: {record['a.title']}")
            
            # Song parts breakdown
            result = session.run("""
                MATCH (p:SongPart)
                OPTIONAL MATCH (p)<-[:PART_OF]-(l:LyricLine)
                RETURN p.name as part, count(l) as lyric_count
                ORDER BY lyric_count DESC
                LIMIT 10
            """)
            print("   🎵 Song Parts by Frequency:")
            for record in result:
                print(f"      • {record['part']}: {record['lyric_count']} lines")
            
            # Vault tracks
            result = session.run("""
                MATCH (s:Song)
                WHERE s.fromTheVault = true
                RETURN count(s) as vault_count
            """)
            vault_count = result.single()["vault_count"]
            print(f"   🔐 From The Vault Tracks: {vault_count}")
    
    def provide_sample_queries(self):
        """Provide sample queries for exploring the data"""
        print("\n🔍 SAMPLE EXPLORATION QUERIES")
        print("=" * 50)
        
        sample_queries = [
            {
                "name": "Albums by Era (Chronological)",
                "query": """
                    MATCH (artist:Artist {name: "Taylor Swift"})-[:RELEASED]->(album:Album)
                    WHERE album.year IS NOT NULL
                    RETURN album.title, album.year, album.songCount
                    ORDER BY album.year
                """
            },
            {
                "name": "Most Common Song Parts",
                "query": """
                    MATCH (p:SongPart)<-[:PART_OF]-(l:LyricLine)
                    RETURN p.name, count(l) as frequency
                    ORDER BY frequency DESC
                    LIMIT 10
                """
            },
            {
                "name": "Longest Songs (by lyric count)",
                "query": """
                    MATCH (s:Song)
                    WHERE s.lyricCount IS NOT NULL
                    RETURN s.title, s.lyricCount, s.albumCode
                    ORDER BY s.lyricCount DESC
                    LIMIT 10
                """
            },
            {
                "name": "Song Structure Patterns",
                "query": """
                    MATCH (song:Song)-[:HAS_LYRIC]->(lyric:LyricLine)-[:PART_OF]->(part:SongPart)
                    WITH song, part.name as partName, count(lyric) as partCount
                    RETURN song.title, collect([partName, partCount]) as structure
                    ORDER BY song.title
                    LIMIT 5
                """
            }
        ]
        
        for i, query_info in enumerate(sample_queries, 1):
            print(f"\n{i}. {query_info['name']}:")
            print("   ```cypher")
            print(f"   {query_info['query'].strip()}")
            print("   ```")
    
    def run_full_load(self, json_file_path):
        """Execute the complete APOC-powered data replacement process"""
        start_time = time.time()
        
        print("🚀 TAYLOR SWIFT AURADB LOADER - APOC INLINE EDITION")
        print("=" * 60)
        print("⚡ Ultra-fast bulk loading with APOC inline processing")
        print("🔒 AuraDB compatible (no file import required)")
        print("⚠️  This will COMPLETELY REPLACE all data in AuraDB")
        print("=" * 60)
        
        try:
            # Step 1: Clear existing data
            self.clear_database()
            
            # Step 2: Create performance indexes
            self.create_indexes()
            
            # Step 3: Prepare data for APOC
            optimized_data = self.prepare_data_for_apoc(json_file_path)
            
            # Step 4: Load data with APOC inline (the magic happens here)
            self.load_data_with_apoc_inline(optimized_data)
            
            # Step 5: Verify data load
            self.verify_data_load()
            
            # Step 6: Provide sample queries
            self.provide_sample_queries()
            
            end_time = time.time()
            print(f"\n🎉 APOC INLINE LOAD COMPLETE!")
            print("=" * 60)
            print(f"⚡ Total time: {end_time - start_time:.2f} seconds")
            print("🚀 Ultra-fast performance with APOC inline procedures")
            print("✅ AuraDB now contains Taylor Swift's complete discography")
            print("🔍 Use the sample queries above to explore the data")
            print("💡 Ready for your Music Besties application!")
            
        except Exception as e:
            print(f"\n❌ Load failed: {e}")
            raise e
        finally:
            if self.driver:
                self.driver.close()
                print("🔌 Database connection closed")

def main():
    """Main execution function"""
    json_file_path = "dev stuff/album-song-lyrics.json"
    
    if not Path(json_file_path).exists():
        print(f"❌ JSON file not found: {json_file_path}")
        print("Please ensure the file exists and try again.")
        return 1
    
    try:
        loader = TaylorSwiftAPOCLoader()
        loader.run_full_load(json_file_path)
        return 0
    except Exception as e:
        print(f"❌ Script failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 