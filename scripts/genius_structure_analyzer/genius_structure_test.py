#!/usr/bin/env python3
"""
Genius API Structure Analysis Tool
Fetches sample lyrics to understand Genius formatting patterns
"""

import os
import re
import json
import time
from collections import Counter
import lyricsgenius
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class GeniusStructureAnalyzer:
    def __init__(self):
        self.genius_token = os.getenv('GENIUS_API_TOKEN')
        if not self.genius_token:
            raise ValueError("❌ GENIUS_API_TOKEN not found in .env file")
        
        self.genius = lyricsgenius.Genius(self.genius_token)
        self.genius.verbose = False  # Reduce API output noise
        self.genius.remove_section_headers = False  # Keep headers for analysis
        
        # Artists from your AuraDB for diverse sample
        self.test_artists = [
            "Taylor Swift", "Billie Eilish", "Ariana Grande", "Kanye West", 
            "Eminem", "BTS", "BLACKPINK", "Arctic Monkeys", "Beyoncé",
            "Drake", "The Weeknd", "Bad Bunny", "Doja Cat", "Harry Styles",
            "Kendrick Lamar", "Travis Scott", "Post Malone", "Olivia Rodrigo",
            "Dua Lipa", "Ed Sheeran"
        ]
        
        self.structure_patterns = []
        self.section_types = Counter()
        
    def fetch_sample_lyrics(self, max_songs=100):
        """Fetch one song per artist for structure analysis"""
        print("🎵 Fetching sample lyrics from Genius API...")
        print("=" * 60)
        
        songs_data = []
        songs_fetched = 0
        
        for artist_name in self.test_artists:
            if songs_fetched >= max_songs:
                break
                
            try:
                print(f"🎤 Searching for {artist_name}...")
                
                # Search for artist's most popular song
                artist = self.genius.search_artist(artist_name, max_songs=1, sort="popularity")
                
                if artist and artist.songs:
                    song = artist.songs[0]
                    
                    # Fetch full lyrics
                    song_data = {
                        'artist': artist_name,
                        'title': song.title,
                        'genius_id': song.id,
                        'lyrics': song.lyrics,
                        'url': song.url
                    }
                    
                    songs_data.append(song_data)
                    songs_fetched += 1
                    
                    print(f"✅ Got: {song.title}")
                    
                    # Analyze structure immediately
                    self.analyze_song_structure(song_data)
                    
                else:
                    print(f"❌ No songs found for {artist_name}")
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error fetching {artist_name}: {e}")
                continue
        
        print(f"\n📊 Successfully fetched {songs_fetched} songs")
        return songs_data
    
    def analyze_song_structure(self, song_data):
        """Analyze the structure of a single song"""
        lyrics = song_data['lyrics']
        
        # Find all section headers
        section_headers = re.findall(r'\[([^\]]+)\]', lyrics)
        
        # Count section types
        for header in section_headers:
            # Normalize section names
            normalized = self.normalize_section_name(header)
            self.section_types[normalized] += 1
        
        # Store pattern for this song
        pattern = {
            'artist': song_data['artist'],
            'title': song_data['title'],
            'sections': section_headers,
            'section_count': len(section_headers),
            'has_structure': len(section_headers) > 0
        }
        
        self.structure_patterns.append(pattern)
    
    def normalize_section_name(self, section_name):
        """Normalize section names for analysis"""
        # Convert to lowercase
        normalized = section_name.lower().strip()
        
        # Common normalizations
        normalizations = {
            # Verses
            r'verse \d+': 'verse',
            r'verse\d+': 'verse',
            r'vers \d+': 'verse',
            
            # Choruses
            r'chorus \d+': 'chorus',
            r'hook \d+': 'chorus',
            r'refrain \d+': 'chorus',
            
            # Pre-elements
            r'pre-chorus \d+': 'pre-chorus',
            r'prechorus \d+': 'pre-chorus',
            
            # Bridges
            r'bridge \d+': 'bridge',
            r'middle 8': 'bridge',
            
            # Outros
            r'outro \d+': 'outro',
            r'ending': 'outro',
            
            # Intros
            r'intro \d+': 'intro',
            r'introduction': 'intro'
        }
        
        for pattern, replacement in normalizations.items():
            if re.match(pattern, normalized):
                return replacement
        
        return normalized
    
    def analyze_patterns(self):
        """Analyze all collected patterns"""
        print("\n🔍 STRUCTURE ANALYSIS RESULTS")
        print("=" * 60)
        
        # Overall statistics
        total_songs = len(self.structure_patterns)
        structured_songs = sum(1 for p in self.structure_patterns if p['has_structure'])
        
        print(f"📊 Total Songs Analyzed: {total_songs}")
        print(f"📊 Songs with Structure Headers: {structured_songs} ({structured_songs/total_songs*100:.1f}%)")
        print(f"📊 Songs without Structure: {total_songs - structured_songs}")
        
        # Most common section types
        print(f"\n🎼 Most Common Section Types:")
        for section, count in self.section_types.most_common(15):
            percentage = count / sum(self.section_types.values()) * 100
            print(f"  • {section.title()}: {count} times ({percentage:.1f}%)")
        
        # Examples of different structures
        print(f"\n📝 Sample Song Structures:")
        for pattern in self.structure_patterns[:10]:
            if pattern['has_structure']:
                sections_str = " → ".join(pattern['sections'][:6])  # First 6 sections
                if len(pattern['sections']) > 6:
                    sections_str += "..."
                print(f"  • {pattern['artist']} - {pattern['title']}")
                print(f"    {sections_str}")
                print()
    
    def generate_parsing_recommendations(self):
        """Generate recommendations for Week 2 parsing script"""
        print("\n💡 WEEK 2 PARSING RECOMMENDATIONS")
        print("=" * 60)
        
        # Calculate coverage of regex patterns
        common_patterns = [
            r'\[Verse \d*\]',
            r'\[Chorus\]',
            r'\[Pre-Chorus\]', 
            r'\[Bridge\]',
            r'\[Outro\]',
            r'\[Intro\]',
            r'\[Hook\]'
        ]
        
        print("🎯 Recommended Regex Patterns:")
        for pattern in common_patterns:
            print(f"  • {pattern}")
        
        # Edge cases to handle
        edge_cases = []
        for pattern in self.structure_patterns:
            for section in pattern['sections']:
                if not any(re.match(p.replace(r'\[', '').replace(r'\]', ''), section, re.IGNORECASE) 
                          for p in common_patterns):
                    edge_cases.append(section)
        
        if edge_cases:
            unique_edge_cases = list(set(edge_cases))[:10]
            print(f"\n⚠️  Edge Cases to Handle:")
            for case in unique_edge_cases:
                print(f"  • [{case}]")
        
        # Success rate estimation
        structured_rate = sum(1 for p in self.structure_patterns if p['has_structure']) / len(self.structure_patterns)
        print(f"\n📈 Expected Success Rate:")
        print(f"  • Songs with clear structure: {structured_rate*100:.1f}%")
        print(f"  • Songs needing special handling: {(1-structured_rate)*100:.1f}%")
    
    def save_results(self, filename="genius_structure_analysis.json"):
        """Save analysis results to file"""
        results = {
            'total_songs': len(self.structure_patterns),
            'section_types': dict(self.section_types),
            'patterns': self.structure_patterns,
            'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
    
    def run_full_analysis(self, max_songs=100):
        """Run complete structure analysis"""
        try:
            # Fetch samples
            songs_data = self.fetch_sample_lyrics(max_songs)
            
            # Analyze patterns
            self.analyze_patterns()
            
            # Generate recommendations  
            self.generate_parsing_recommendations()
            
            # Save results
            self.save_results()
            
            print(f"\n🎉 ANALYSIS COMPLETE!")
            print("✅ Ready to build Week 2 parsing script based on these patterns")
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")

def main():
    """Main execution function"""
    print("🎵 Genius API Structure Analysis Tool")
    print("=" * 60)
    
    try:
        analyzer = GeniusStructureAnalyzer()
        analyzer.run_full_analysis(max_songs=100)
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("\n💡 Make sure you have:")
        print("  • GENIUS_API_TOKEN in your .env file")
        print("  • lyricsgenius package installed: pip install lyricsgenius")

if __name__ == "__main__":
    main() 