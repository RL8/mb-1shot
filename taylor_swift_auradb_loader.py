#!/usr/bin/env python3
"""
Taylor Swift AuraDB Loader
Completely replaces AuraDB content with Taylor Swift album-song-lyrics data
Optimized graph structure for lyrical analysis and song structure insights
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

class TaylorSwiftAuraDBLoader:
    def __init__(self):
        """Initialize connection to AuraDB"""
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        print(f" AURA_DB_URI found: {'Yes' if self.neo4j_uri else 'No'}")
        print(f" AURA_DB_USERNAME found: {'Yes' if self.neo4j_user else 'No'}")
        print(f" AURA_DB_PASSWORD found: {'Yes' if self.neo4j_password else 'No'}")
        
        if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
            raise ValueError(" Missing Neo4j credentials in .env file")
        
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
            print(" Connected to Neo4j AuraDB")
        except Exception as e:
            print(f" Failed to connect to Neo4j: {e}")
            raise e
    
    def clear_database(self):
        """Completely clear the AuraDB database"""
        print("\n  CLEARING AURADB DATABASE")
        print("=" * 50)
        
        with self.driver.session() as session:
            try:
                # Get initial stats
                node_result = session.run("MATCH (n) RETURN count(n) as count")
                initial_nodes = node_result.single()["count"]
                
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                initial_rels = rel_result.single()["count"]
                
                print(f" Current database: {initial_nodes} nodes, {initial_rels} relationships")
                
                if initial_nodes == 0 and initial_rels == 0:
                    print(" Database is already empty")
                    return
                
                # Use DETACH DELETE to remove nodes and relationships together
                print(" Deleting all nodes and relationships...")
                session.run("MATCH (n) DETACH DELETE n")
                
                # Verify cleanup
                final_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                final_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                print(f" Database cleared: {final_nodes} nodes, {final_rels} relationships remaining")
                
            except Exception as e:
                print(f" Error during cleanup: {e}")
                raise e
    
    def create_indexes(self):
        """Create indexes for optimal performance"""
        print("\n CREATING PERFORMANCE INDEXES")
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
                    print(f" Created index: {label}.{property_name}")
                except Exception as e:
                    print(f"  Index creation warning for {label}.{property_name}: {e}")
    
    def load_taylor_swift_data(self, json_file_path):
        """Load Taylor Swift data from JSON file"""
        print(f"\n LOADING DATA FROM {json_file_path}")
        print("=" * 50)
        
        # Load JSON data
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                albums_data = json.load(f)
            print(f" JSON loaded: {len(albums_data)} albums found")
        except Exception as e:
            print(f" Error loading JSON: {e}")
            raise e
        
        with self.driver.session() as session:
            # Create Taylor Swift artist node
            print("\n Creating Artist node...")
            session.run("""
                MERGE (artist:Artist {name: "Taylor Swift"})
                SET artist.genre = "Pop/Country",
                    artist.activeYears = "2006-Present",
                    artist.country = "United States",
                    artist.debutYear = 2006,
                    artist.grammyWins = 12,
                    artist.totalAlbums = $total_albums,
                    artist.totalSongs = $total_songs,
                    artist.lastUpdated = datetime()
            """, total_albums=len(albums_data), 
                 total_songs=sum(len(album['Songs']) for album in albums_data))
            print(" Taylor Swift artist node created")
            
            # Process each album
            total_songs = 0
            total_lyrics = 0
            song_parts = set()
            
            for album_idx, album in enumerate(albums_data, 1):
                print(f"\n Processing Album {album_idx}/{len(albums_data)}: {album['Title']}")
                
                # Create album node
                session.run("""
                    MATCH (artist:Artist {name: "Taylor Swift"})
                    MERGE (album:Album {code: $code})
                    SET album.title = $title,
                        album.subtitle = $subtitle,
                        album.year = $year,
                        album.songCount = $song_count,
                        album.createdAt = datetime()
                    MERGE (artist)-[:RELEASED]->(album)
                """, code=album['Code'], 
                     title=album['Title'],
                     subtitle=album.get('SubTitle', ''),
                     year=album.get('Year'),
                     song_count=len(album['Songs']))
                
                # Process songs in this album
                for song in album['Songs']:
                    total_songs += 1
                    
                    # Create song node
                    session.run("""
                        MATCH (album:Album {code: $album_code})
                        MERGE (song:Song {title: $title, albumCode: $album_code, trackNumber: $track_number})
                        SET song.fromTheVault = $from_the_vault,
                            song.featuredArtists = $featured_artists,
                            song.lyricCount = $lyric_count,
                            song.createdAt = datetime()
                        MERGE (album)-[:CONTAINS {trackNumber: $track_number}]->(song)
                    """, album_code=album['Code'],
                         title=song['Title'],
                         track_number=song['TrackNumber'],
                         from_the_vault=song.get('FromTheVault', False),
                         featured_artists=song.get('FeaturedArtists', []),
                         lyric_count=len(song.get('Lyrics', [])))
                    
                    # Process lyrics for this song
                    if 'Lyrics' in song:
                        for lyric in song['Lyrics']:
                            total_lyrics += 1
                            song_part = lyric.get('SongPart', 'Unknown')
                            song_parts.add(song_part)
                            
                            # Create lyric line node
                            session.run("""
                                MATCH (song:Song {title: $song_title, albumCode: $album_code})
                                MERGE (part:SongPart {name: $song_part})
                                CREATE (lyric:LyricLine {
                                    order: $order,
                                    text: $text,
                                    songPart: $song_part,
                                    createdAt: datetime()
                                })
                                MERGE (song)-[:HAS_LYRIC {order: $order}]->(lyric)
                                MERGE (lyric)-[:PART_OF]->(part)
                            """, song_title=song['Title'],
                                 album_code=album['Code'],
                                 order=lyric.get('Order', 0),
                                 text=lyric.get('Text', ''),
                                 song_part=song_part)
                
                print(f"    {album['Title']}: {len(album['Songs'])} songs loaded")
            
            print(f"\n DATA LOADING COMPLETE")
            print(f"    Albums: {len(albums_data)}")
            print(f"    Songs: {total_songs}")
            print(f"    Lyric Lines: {total_lyrics}")
            print(f"    Song Parts: {len(song_parts)} ({', '.join(sorted(song_parts))})")
    
    def verify_data_load(self):
        """Verify the data was loaded correctly"""
        print("\n VERIFYING DATA LOAD")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Basic counts
            artists = session.run("MATCH (a:Artist) RETURN count(a) as count").single()["count"]
            albums = session.run("MATCH (a:Album) RETURN count(a) as count").single()["count"]
            songs = session.run("MATCH (s:Song) RETURN count(s) as count").single()["count"]
            lyrics = session.run("MATCH (l:LyricLine) RETURN count(l) as count").single()["count"]
            song_parts = session.run("MATCH (p:SongPart) RETURN count(p) as count").single()["count"]
            
            print(f" Artists: {artists}")
            print(f" Albums: {albums}")
            print(f" Songs: {songs}")
            print(f" Lyric Lines: {lyrics}")
            print(f" Song Parts: {song_parts}")
            
            # Sample queries to verify relationships
            print("\n Sample Data Verification:")
            
            # Albums by year
            result = session.run("""
                MATCH (a:Album)
                WHERE a.year IS NOT NULL
                RETURN a.title, a.year
                ORDER BY a.year
                LIMIT 5
            """)
            print("    First 5 Albums by Year:")
            for record in result:
                print(f"       {record['a.year']}: {record['a.title']}")
            
            # Song parts breakdown
            result = session.run("""
                MATCH (p:SongPart)
                OPTIONAL MATCH (p)<-[:PART_OF]-(l:LyricLine)
                RETURN p.name as part, count(l) as lyric_count
                ORDER BY lyric_count DESC
                LIMIT 10
            """)
            print("    Song Parts by Frequency:")
            for record in result:
                print(f"       {record['part']}: {record['lyric_count']} lines")
            
            # Vault tracks
            result = session.run("""
                MATCH (s:Song)
                WHERE s.fromTheVault = true
                RETURN count(s) as vault_count
            """)
            vault_count = result.single()["vault_count"]
            print(f"    From The Vault Tracks: {vault_count}")
    
    def provide_sample_queries(self):
        """Provide sample queries for exploring the data"""
        print("\n SAMPLE EXPLORATION QUERIES")
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
                "name": "From The Vault Analysis",
                "query": """
                    MATCH (album:Album)-[:CONTAINS]->(song:Song)
                    WHERE song.fromTheVault = true
                    RETURN album.title, collect(song.title) as vault_tracks
                    ORDER BY album.year
                """
            },
            {
                "name": "Song Structure Analysis",
                "query": """
                    MATCH (song:Song)-[:HAS_LYRIC]->(lyric:LyricLine)-[:PART_OF]->(part:SongPart)
                    WITH song, part.name as partName, count(lyric) as partCount
                    RETURN song.title, collect([partName, partCount]) as structure
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
        """Execute the complete data replacement process"""
        start_time = time.time()
        
        print(" TAYLOR SWIFT AURADB LOADER")
        print("=" * 60)
        print("  This will COMPLETELY REPLACE all data in AuraDB")
        print("=" * 60)
        
        try:
            # Step 1: Clear existing data
            self.clear_database()
            
            # Step 2: Create performance indexes
            self.create_indexes()
            
            # Step 3: Load Taylor Swift data
            self.load_taylor_swift_data(json_file_path)
            
            # Step 4: Verify data load
            self.verify_data_load()
            
            # Step 5: Provide sample queries
            self.provide_sample_queries()
            
            end_time = time.time()
            print(f"\n LOAD COMPLETE!")
            print("=" * 60)
            print(f"  Total time: {end_time - start_time:.2f} seconds")
            print(" AuraDB now contains Taylor Swift's complete discography")
            print(" Use the sample queries above to explore the data")
            print(" Ready for your Music Besties application!")
            
        except Exception as e:
            print(f"\n Load failed: {e}")
            raise e
        finally:
            if self.driver:
                self.driver.close()
                print(" Database connection closed")

def main():
    """Main execution function"""
    json_file_path = "dev stuff/album-song-lyrics.json"
    
    if not Path(json_file_path).exists():
        print(f" JSON file not found: {json_file_path}")
        print("Please ensure the file exists and try again.")
        return 1
    
    try:
        loader = TaylorSwiftAuraDBLoader()
        loader.run_full_load(json_file_path)
        return 0
    except Exception as e:
        print(f" Script failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
