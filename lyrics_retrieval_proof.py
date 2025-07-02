#!/usr/bin/env python3
"""
Lyrics Retrieval Proof Script
Retrieves complete lyrics for one song and saves to file
Shows proof of successful retrieval through metadata
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
import lyricsgenius
from requests.exceptions import HTTPError, Timeout

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class LyricsRetrievalProof:
    def __init__(self):
        """Initialize with robust configuration"""
        self.genius_token = os.getenv('GENIUS_API_TOKEN')
        
        if not self.genius_token:
            raise ValueError("❌ GENIUS_API_TOKEN not found in environment variables")
        
        # Initialize with robust settings
        self.genius = lyricsgenius.Genius(
            access_token=self.genius_token,
            timeout=15,
            retries=2,
            sleep_time=0.8,
            verbose=True,
            remove_section_headers=False  # Keep section headers for structure
        )
        
        print(f"🔑 Initialized Genius API client")
    
    def retrieve_and_save_lyrics(self, title, artist, filename=None):
        """Retrieve complete lyrics and save to file"""
        print(f"\n🎵 Retrieving lyrics for: '{title}' by {artist}")
        
        try:
            # Search for the song
            song = self.genius.search_song(title, artist)
            
            if not song:
                print(f"❌ Song not found: '{title}' by {artist}")
                return None
            
            # Get complete song data
            song_data = {
                'title': song.title,
                'artist': song.artist,
                'url': song.url,
                'release_date': getattr(song, 'release_date_for_display', 'Unknown'),
                'lyrics': song.lyrics,
                'retrieval_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'genius_id': song.id
            }
            
            # Add stats if available
            stats = getattr(song, 'stats', None)
            if stats:
                song_data['pageviews'] = getattr(stats, 'pageviews', 'Unknown')
            
            # Create filename if not provided
            if not filename:
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_')).strip()
                filename = f"lyrics_{safe_artist}_{safe_title}.json".replace(' ', '_')
            
            # Save to file
            filepath = Path(filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(song_data, f, indent=2, ensure_ascii=False)
            
            # Verify file was created and get stats
            if filepath.exists():
                file_size = filepath.stat().st_size
                
                # Analyze lyrics content
                lyrics = song_data['lyrics']
                lyrics_stats = self.analyze_lyrics(lyrics)
                
                print(f"✅ Successfully retrieved and saved lyrics!")
                print(f"📁 File: {filepath}")
                print(f"📊 File size: {file_size:,} bytes")
                print(f"🎤 Song: {song.title}")
                print(f"🎨 Artist: {song.artist}")
                print(f"🔗 Genius URL: {song.url}")
                print(f"📈 Views: {song_data.get('pageviews', 'Unknown')}")
                print(f"\n📝 Lyrics Analysis:")
                print(f"   Characters: {lyrics_stats['char_count']:,}")
                print(f"   Lines: {lyrics_stats['line_count']:,}")
                print(f"   Words: {lyrics_stats['word_count']:,}")
                print(f"   Sections: {lyrics_stats['section_count']}")
                
                # Show first and last lines as proof (small excerpts)
                lines = lyrics.strip().split('\n')
                if len(lines) >= 2:
                    print(f"\n🔍 Content Verification:")
                    print(f"   First line: \"{lines[0][:50]}{'...' if len(lines[0]) > 50 else ''}\"")
                    print(f"   Last line: \"{lines[-1][:50]}{'...' if len(lines[-1]) > 50 else ''}\"")
                
                return filepath
            else:
                print(f"❌ Failed to create file: {filepath}")
                return None
                
        except HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            return None
        except Timeout:
            print(f"⏰ Request timed out")
            return None
        except Exception as e:
            print(f"🔄 Unexpected error: {e}")
            return None
    
    def analyze_lyrics(self, lyrics):
        """Analyze lyrics structure and content"""
        if not lyrics:
            return {'char_count': 0, 'line_count': 0, 'word_count': 0, 'section_count': 0}
        
        lines = lyrics.split('\n')
        words = lyrics.split()
        
        # Count section headers (like [Verse 1], [Chorus], etc.)
        section_count = sum(1 for line in lines if line.strip().startswith('[') and line.strip().endswith(']'))
        
        return {
            'char_count': len(lyrics),
            'line_count': len(lines),
            'word_count': len(words),
            'section_count': section_count
        }
    
    def verify_file_contents(self, filepath):
        """Verify the saved file contains complete lyrics"""
        if not filepath or not Path(filepath).exists():
            print("❌ File does not exist")
            return False
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            required_fields = ['title', 'artist', 'lyrics', 'url']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            lyrics = data['lyrics']
            if not lyrics or len(lyrics) < 100:  # Reasonable minimum for song lyrics
                print("❌ Lyrics appear incomplete or missing")
                return False
            
            print(f"✅ File verification successful:")
            print(f"   Contains all required fields")
            print(f"   Lyrics present: {len(lyrics):,} characters")
            return True
            
        except Exception as e:
            print(f"❌ File verification failed: {e}")
            return False

def main():
    """Main execution function"""
    print("🎯 Lyrics Retrieval Proof Test")
    print("This will retrieve complete lyrics for one song and save to file")
    
    retriever = LyricsRetrievalProof()
    
    # Test song - using a popular, well-known song
    test_title = "Anti-Hero"
    test_artist = "Taylor Swift"
    
    # Retrieve and save lyrics
    filepath = retriever.retrieve_and_save_lyrics(test_title, test_artist)
    
    if filepath:
        print(f"\n🔍 Verifying saved file...")
        if retriever.verify_file_contents(filepath):
            print(f"\n🎉 SUCCESS! Complete lyrics successfully retrieved and saved.")
            print(f"📁 File location: {filepath.absolute()}")
            print(f"\n💡 You can now open {filepath} to view the complete lyrics.")
        else:
            print(f"\n❌ File verification failed")
    else:
        print(f"\n❌ Failed to retrieve and save lyrics")

if __name__ == "__main__":
    main() 