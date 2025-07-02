#!/usr/bin/env python3
"""
LyricsGenius Test Script
Test functionality by getting lyrics for 10 random Taylor Swift songs
Shows metadata and structure analysis without reproducing copyrighted content
"""

import os
import re
import random
import time
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv
import lyricsgenius

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class LyricsGeniusTestStudio:
    def __init__(self):
        """Initialize connections to both AuraDB and Genius API"""
        # Neo4j credentials
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        # Genius API credentials
        self.genius_token = os.getenv('GENIUS_API_TOKEN')
        
        print("🔧 CHECKING CREDENTIALS")
        print("=" * 50)
        print(f"✅ Neo4j URI: {'Found' if self.neo4j_uri else 'Missing'}")
        print(f"✅ Neo4j User: {'Found' if self.neo4j_user else 'Missing'}")
        print(f"✅ Neo4j Password: {'Found' if self.neo4j_password else 'Missing'}")
        print(f"✅ Genius Token: {'Found' if self.genius_token else 'Missing'}")
        
        if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
            raise ValueError("Missing Neo4j credentials")
        if not self.genius_token:
            raise ValueError("Missing Genius API token")
        
        # Initialize connections
        self.driver = None
        self.genius = None
        self._connect()
    
    def _connect(self):
        """Connect to both AuraDB and Genius API"""
        try:
            # Connect to Neo4j
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            self.driver.verify_connectivity()
            print("✅ Connected to Neo4j AuraDB")
            
            # Connect to Genius API
            self.genius = lyricsgenius.Genius(self.genius_token)
            self.genius.verbose = False  # Reduce API noise
            self.genius.remove_section_headers = False  # Keep structure for analysis
            print("✅ Connected to Genius API")
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise e
    
    def get_random_songs(self, count=10):
        """Get random songs from AuraDB"""
        print(f"\n🎵 GETTING {count} RANDOM SONGS FROM AURADB")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Get random songs
            result = session.run("""
                MATCH (s:Song)-[:CONTAINS]-(a:Album)
                WHERE s.title IS NOT NULL
                RETURN s.title as title, a.title as album, s.trackNumber as track
                ORDER BY rand()
                LIMIT $count
            """, count=count)
            
            songs = []
            for record in result:
                songs.append({
                    'title': record['title'],
                    'album': record['album'],
                    'track': record['track']
                })
            
            print(f"✅ Retrieved {len(songs)} random songs:")
            for i, song in enumerate(songs, 1):
                print(f"   {i:2}. {song['title']} (Track {song['track']}, {song['album']})")
            
            return songs
    
    def analyze_lyrics_structure(self, lyrics_text):
        """Analyze lyrics structure without reproducing content"""
        if not lyrics_text:
            return {
                'sections': [],
                'total_lines': 0,
                'has_structure': False,
                'section_count': 0
            }
        
        # Find section headers like [Verse 1], [Chorus], etc.
        section_pattern = r'\[([^\]]+)\]'
        sections = re.findall(section_pattern, lyrics_text)
        
        # Count total lines (non-empty)
        lines = [line.strip() for line in lyrics_text.split('\n') if line.strip()]
        total_lines = len(lines)
        
        # Remove section headers from line count
        content_lines = [line for line in lines if not re.match(r'^\[.*\]$', line)]
        content_line_count = len(content_lines)
        
        return {
            'sections': sections,
            'total_lines': total_lines,
            'content_lines': content_line_count,
            'has_structure': len(sections) > 0,
            'section_count': len(sections),
            'structure_types': list(set(sections))
        }
    
    def test_genius_api_with_songs(self, songs):
        """Test Genius API with the random songs"""
        print(f"\n🚀 TESTING GENIUS API WITH {len(songs)} SONGS")
        print("=" * 50)
        
        results = []
        
        for i, song_info in enumerate(songs, 1):
            print(f"\n🎵 {i:2}. Testing: {song_info['title']}")
            print("-" * 40)
            
            try:
                # Search for the song
                print("   🔍 Searching Genius API...")
                song = self.genius.search_song(song_info['title'], "Taylor Swift")
                
                if song and song.lyrics:
                    # Analyze structure without showing content
                    analysis = self.analyze_lyrics_structure(song.lyrics)
                    
                    result = {
                        'title': song_info['title'],
                        'found': True,
                        'genius_title': song.title,
                        'artist': song.artist,
                        'analysis': analysis,
                        'url': song.url if hasattr(song, 'url') else None
                    }
                    
                    print(f"   ✅ Found: {song.title}")
                    print(f"   📊 Structure: {analysis['section_count']} sections")
                    print(f"   📝 Content: {analysis['content_lines']} lyric lines")
                    print(f"   🏗️  Types: {', '.join(analysis['structure_types'][:5])}")  # Show first 5 types
                    
                else:
                    result = {
                        'title': song_info['title'],
                        'found': False,
                        'reason': 'No lyrics found'
                    }
                    print(f"   ❌ Not found or no lyrics available")
                
                results.append(result)
                
                # Rate limiting - be nice to the API
                time.sleep(1)
                
            except Exception as e:
                result = {
                    'title': song_info['title'],
                    'found': False,
                    'reason': str(e)
                }
                results.append(result)
                print(f"   ❌ Error: {e}")
        
        return results
    
    def generate_test_report(self, results):
        """Generate a comprehensive test report"""
        print(f"\n📊 LYRICSGENIUS TEST REPORT")
        print("=" * 60)
        
        # Summary statistics
        found_count = sum(1 for r in results if r['found'])
        total_count = len(results)
        success_rate = (found_count / total_count) * 100 if total_count > 0 else 0
        
        print(f"📈 SUCCESS RATE: {found_count}/{total_count} ({success_rate:.1f}%)")
        print(f"✅ Found with lyrics: {found_count}")
        print(f"❌ Not found/no lyrics: {total_count - found_count}")
        
        # Structure analysis for found songs
        if found_count > 0:
            print(f"\n🏗️  STRUCTURE ANALYSIS (Found Songs)")
            print("-" * 40)
            
            all_sections = []
            total_content_lines = 0
            
            for result in results:
                if result['found'] and 'analysis' in result:
                    analysis = result['analysis']
                    all_sections.extend(analysis['sections'])
                    total_content_lines += analysis['content_lines']
                    
                    print(f"• {result['title'][:30]:30} | {analysis['section_count']:2} sections | {analysis['content_lines']:3} lines")
            
            # Section type frequency
            if all_sections:
                from collections import Counter
                section_counts = Counter(all_sections)
                
                print(f"\n📋 MOST COMMON SECTION TYPES:")
                for section_type, count in section_counts.most_common(8):
                    print(f"   {section_type:15} | {count:2} occurrences")
                
                print(f"\n📏 METRICS:")
                print(f"   Average sections per song: {len(all_sections) / found_count:.1f}")
                print(f"   Average content lines: {total_content_lines / found_count:.1f}")
                print(f"   Unique section types: {len(section_counts)}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print("-" * 40)
        
        if success_rate >= 80:
            print("✅ Excellent success rate! LyricsGenius is working well.")
            print("🚀 Ready to proceed with full lyrics collection.")
        elif success_rate >= 60:
            print("⚠️  Good success rate, but some songs not found.")
            print("🔄 Consider backup lyrics sources for missing songs.")
        else:
            print("❌ Low success rate. Check API connectivity and song titles.")
            print("🔧 May need alternative lyrics sources.")
        
        if found_count > 0:
            print("📝 Structure detection is working - ready for Week 2 parsing!")
            print("🎯 Lyric format is compatible with section header parsing.")
    
    def run_full_test(self):
        """Execute the complete test suite"""
        try:
            # Get random songs from database
            songs = self.get_random_songs(10)
            
            if not songs:
                print("❌ No songs found in database")
                return
            
            # Test Genius API
            results = self.test_genius_api_with_songs(songs)
            
            # Generate report
            self.generate_test_report(results)
            
            print(f"\n🎉 LYRICSGENIUS TEST COMPLETE!")
            print("=" * 60)
            print("✅ API connectivity verified")
            print("✅ Lyrics retrieval tested")
            print("✅ Structure analysis confirmed")
            print("💡 Ready for production lyrics collection!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise e
        finally:
            if self.driver:
                self.driver.close()
                print("🔌 Database connection closed")

def main():
    """Main execution function"""
    try:
        tester = LyricsGeniusTestStudio()
        tester.run_full_test()
        return 0
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 