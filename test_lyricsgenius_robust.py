#!/usr/bin/env python3
"""
Robust LyricsGenius Test Script
Implements best practices for handling timeouts and connection issues
Tests functionality with incremental scaling approach
"""

import os
import re
import random
import time
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import lyricsgenius
from requests.exceptions import HTTPError, Timeout

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class RobustLyricsGeniusTestStudio:
    def __init__(self):
        """Initialize with robust configuration and error handling"""
        # Neo4j credentials
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        # Genius API credentials
        self.genius_token = os.getenv('GENIUS_API_TOKEN')
        
        if not self.genius_token:
            raise ValueError("❌ GENIUS_API_TOKEN not found in environment variables")
        
        print(f"🔑 Loaded Genius API token: {self.genius_token[:8]}...")
        print(f"🔗 AuraDB URI: {self.neo4j_uri[:20]}...")
        
        # Initialize connections
        self.driver = None
        self.genius = None
        
    def connect_to_auradb(self):
        """Connect to AuraDB with error handling"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            print("✅ Connected to AuraDB successfully")
            return True
        except Exception as e:
            print(f"❌ AuraDB connection failed: {e}")
            return False
    
    def test_genius_connection(self, config_level=1):
        """Test Genius API connection with different configuration levels"""
        configs = [
            {'timeout': 10, 'retries': 1, 'sleep_time': 0.5},  # Level 1: Basic
            {'timeout': 15, 'retries': 2, 'sleep_time': 0.8},  # Level 2: Moderate
            {'timeout': 20, 'retries': 3, 'sleep_time': 1.2}   # Level 3: Aggressive
        ]
        
        config = configs[config_level - 1]
        print(f"🔧 Testing connection with config level {config_level}: {config}")
        
        try:
            self.genius = lyricsgenius.Genius(
                access_token=self.genius_token,
                timeout=config['timeout'],
                retries=config['retries'],
                sleep_time=config['sleep_time'],
                verbose=True
            )
            
            # Simple connectivity test
            print("🔍 Testing basic search functionality...")
            result = self.genius.search_songs("test", per_page=1)
            
            if result and 'hits' in result:
                print(f"✅ Connection successful! Found {len(result['hits'])} result(s)")
                return True
            else:
                print("⚠️ Connection works but no results returned")
                return False
                
        except HTTPError as e:
            print(f"❌ HTTP Error: Status {e.args[0]} - {e.args[1]}")
            return False
        except Timeout:
            print("⏰ Request timed out")
            return False
        except Exception as e:
            print(f"🔄 Unexpected error: {e}")
            return False
    
    def robust_song_search(self, title, artist, max_attempts=3):
        """Search for a song with robust retry logic"""
        print(f"\n🎵 Searching for: '{title}' by {artist}")
        
        for attempt in range(max_attempts):
            try:
                song = self.genius.search_song(title, artist)
                
                if song:
                    # Show safe metadata (no lyrics content)
                    print(f"✅ Found song: {song.title}")
                    print(f"   Artist: {song.artist}")
                    print(f"   URL: {song.url}")
                    print(f"   Release Date: {getattr(song, 'release_date_for_display', 'Unknown')}")
                    stats = getattr(song, 'stats', None)
                    pageviews = getattr(stats, 'pageviews', 'Unknown') if stats else 'Unknown'
                    print(f"   Views: {pageviews}")
                    
                    # Structure analysis (safe)
                    lyrics_length = len(song.lyrics) if song.lyrics else 0
                    lines_count = song.lyrics.count('\n') if song.lyrics else 0
                    
                    print(f"   Lyrics: {lyrics_length} characters, {lines_count} lines")
                    print(f"   Structure: {'Available' if lyrics_length > 0 else 'Not available'}")
                    
                    return song
                else:
                    print(f"⚠️ No results found for '{title}' by {artist}")
                    return None
                    
            except HTTPError as e:
                print(f"❌ Attempt {attempt + 1} - HTTP Error: {e}")
                if attempt == max_attempts - 1:
                    print(f"💥 All {max_attempts} attempts failed")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Timeout:
                print(f"⏰ Attempt {attempt + 1} - Timeout")
                if attempt == max_attempts - 1:
                    print(f"💥 All {max_attempts} attempts timed out")
                    return None
                time.sleep(2 ** attempt)
                
            except Exception as e:
                print(f"🔄 Attempt {attempt + 1} - Unexpected error: {e}")
                if attempt == max_attempts - 1:
                    return None
                time.sleep(1)
        
        return None
    
    def get_random_taylor_songs(self, count=5):
        """Get random Taylor Swift songs from AuraDB for testing"""
        if not self.driver:
            return []
        
        query = """
        MATCH (s:Song)-[:PERFORMED_BY]->(a:Artist {name: 'Taylor Swift'})
        RETURN s.title as title, s.trackNumber as track
        ORDER BY rand()
        LIMIT $count
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, count=count)
                songs = [(record['title'], 'Taylor Swift') for record in result]
                print(f"🎲 Selected {len(songs)} random Taylor Swift songs from database")
                return songs
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            return []
    
    def run_small_test(self):
        """Run a small test with 2-3 songs"""
        print("\n" + "="*60)
        print("🧪 SMALL SCALE TEST (2-3 songs)")
        print("="*60)
        
        # Test songs - mix of common and less common
        test_songs = [
            ("Love Story", "Taylor Swift"),
            ("Anti-Hero", "Taylor Swift"),
        ]
        
        successful_tests = 0
        
        for title, artist in test_songs:
            song = self.robust_song_search(title, artist)
            if song:
                successful_tests += 1
            
            # Respectful delay between searches
            time.sleep(1)
        
        success_rate = (successful_tests / len(test_songs)) * 100
        print(f"\n📊 Small test results: {successful_tests}/{len(test_songs)} successful ({success_rate:.1f}%)")
        
        return success_rate >= 50  # Consider 50%+ success rate as "working"
    
    def run_medium_test(self):
        """Run a medium test with 5-7 random songs"""
        print("\n" + "="*60)
        print("🧪 MEDIUM SCALE TEST (5-7 songs)")
        print("="*60)
        
        # Get random songs from database
        test_songs = self.get_random_taylor_songs(6)
        
        if not test_songs:
            print("⚠️ Couldn't get songs from database, using fallback list")
            test_songs = [
                ("Shake It Off", "Taylor Swift"),
                ("Blank Space", "Taylor Swift"),
                ("Bad Blood", "Taylor Swift"),
                ("Look What You Made Me Do", "Taylor Swift"),
                ("Delicate", "Taylor Swift")
            ]
        
        successful_tests = 0
        
        for title, artist in test_songs:
            song = self.robust_song_search(title, artist)
            if song:
                successful_tests += 1
            
            # Respectful delay between searches
            time.sleep(1.5)
        
        success_rate = (successful_tests / len(test_songs)) * 100
        print(f"\n📊 Medium test results: {successful_tests}/{len(test_songs)} successful ({success_rate:.1f}%)")
        
        return success_rate >= 60  # Higher bar for medium test
    
    def run_full_test(self):
        """Run a comprehensive test with 10+ songs"""
        print("\n" + "="*60)
        print("🧪 FULL SCALE TEST (10+ songs)")
        print("="*60)
        
        # Get more random songs
        test_songs = self.get_random_taylor_songs(12)
        
        if len(test_songs) < 10:
            print("⚠️ Adding fallback songs to reach target count")
            fallback_songs = [
                ("We Are Never Ever Getting Back Together", "Taylor Swift"),
                ("I Knew You Were Trouble", "Taylor Swift"),
                ("22", "Taylor Swift"),
                ("Style", "Taylor Swift"),
                ("Wildest Dreams", "Taylor Swift")
            ]
            test_songs.extend(fallback_songs[:12 - len(test_songs)])
        
        successful_tests = 0
        
        for i, (title, artist) in enumerate(test_songs, 1):
            print(f"\n--- Test {i}/{len(test_songs)} ---")
            song = self.robust_song_search(title, artist)
            if song:
                successful_tests += 1
            
            # Longer delays for full test to be respectful
            time.sleep(2)
        
        success_rate = (successful_tests / len(test_songs)) * 100
        print(f"\n📊 Full test results: {successful_tests}/{len(test_songs)} successful ({success_rate:.1f}%)")
        
        return success_rate >= 70  # Highest bar for full test

def main():
    """Main execution function with incremental testing"""
    print("🚀 Starting Robust LyricsGenius Test Suite")
    print("This will test connection and scale up if successful")
    
    tester = RobustLyricsGeniusTestStudio()
    
    # Step 1: Connect to AuraDB
    if not tester.connect_to_auradb():
        print("⚠️ Continuing without AuraDB connection")
    
    # Step 2: Test Genius API connection
    connection_successful = False
    for config_level in [1, 2, 3]:
        print(f"\n🔧 Trying connection configuration level {config_level}...")
        if tester.test_genius_connection(config_level):
            connection_successful = True
            break
        else:
            print(f"❌ Configuration level {config_level} failed")
    
    if not connection_successful:
        print("💥 All connection attempts failed. Check network/credentials.")
        return
    
    # Step 3: Small test
    print("\n🎯 Starting incremental testing...")
    if tester.run_small_test():
        print("✅ Small test passed! Proceeding to medium test...")
        
        # Step 4: Medium test
        if tester.run_medium_test():
            print("✅ Medium test passed! Proceeding to full test...")
            
            # Step 5: Full test
            if tester.run_full_test():
                print("🎉 All tests passed! LyricsGenius is working robustly.")
            else:
                print("⚠️ Full test had issues, but basic functionality works.")
        else:
            print("⚠️ Medium test had issues, but small-scale functionality works.")
    else:
        print("❌ Small test failed. Check API credentials and network connectivity.")
    
    print("\n🏁 Test suite completed!")

if __name__ == "__main__":
    main() 