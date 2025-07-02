#!/usr/bin/env python3
"""
Week 2: Lyrics Structure Parser
Parses Genius API lyrics into structured sections and stores in AuraDB
Based on real analysis of Genius API formatting patterns
"""

import os
import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

@dataclass
class LyricSection:
    """Represents a structured section of a song"""
    section_type: str
    section_number: Optional[int]
    artists: List[str]
    lyrics_content: str
    order: int
    original_header: str

class GeniusLyricsParser:
    def __init__(self):
        """Initialize the lyrics parser with AuraDB connection"""
        # Database connection
        self.uri = os.getenv("AURA_DB_URI")
        self.username = os.getenv("AURA_DB_USERNAME", "neo4j")
        self.password = os.getenv("AURA_DB_PASSWORD")
        
        if not all([self.uri, self.password]):
            raise ValueError("❌ AuraDB credentials not found in .env file")
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
        
        # Section type mappings (based on real analysis + international support)
        self.section_mappings = {
            # English terms (from real data)
            'verse': 'verse',
            'chorus': 'chorus', 
            'pre-chorus': 'pre-chorus',
            'prechorus': 'pre-chorus',
            'bridge': 'bridge',
            'middle 8': 'bridge',
            'intro': 'intro',
            'introduction': 'intro',
            'outro': 'outro',
            'ending': 'outro',
            'hook': 'chorus',
            'refrain': 'chorus',
            'post-chorus': 'post-chorus',
            
            # International terms (discovered in analysis)
            'estribillo': 'chorus',  # Spanish
            'verso': 'verse',        # Spanish
            'puente': 'bridge',      # Spanish
            
            # Special sections
            'part': 'part',
            'interlude': 'interlude',
            'breakdown': 'breakdown'
        }
        
        # Regex pattern for section headers
        self.section_pattern = re.compile(r'\[([^\]]+)\]', re.IGNORECASE | re.MULTILINE)
        
        print("✅ Lyrics Structure Parser initialized")
        print(f"✅ Connected to AuraDB: {self.uri}")

    def parse_section_header(self, header: str) -> Tuple[str, Optional[int], List[str]]:
        """
        Parse a section header to extract type, number, and artists
        
        Real examples from analysis:
        '[Verse 1]' -> ('verse', 1, [])
        '[Chorus: Billie Eilish with Khalid]' -> ('chorus', None, ['Billie Eilish', 'Khalid'])
        '[Estribillo]' -> ('chorus', None, [])
        """
        header = header.strip()
        
        # Split by colon to separate section type from artists
        if ':' in header:
            section_part, artist_part = header.split(':', 1)
            section_part = section_part.strip()
            artist_part = artist_part.strip()
            artists = self.extract_artists(artist_part)
        else:
            section_part = header
            artists = []
        
        # Extract section type and number
        section_type, section_number = self.extract_section_type_and_number(section_part)
        
        return section_type, section_number, artists
    
    def extract_section_type_and_number(self, section_part: str) -> Tuple[str, Optional[int]]:
        """Extract section type and number from section part"""
        # Pattern for numbered sections (e.g., "Verse 1", "Chorus 2")
        numbered_match = re.match(r'(.+?)\s+(\d+)$', section_part.strip())
        if numbered_match:
            type_part = numbered_match.group(1).lower().strip()
            number = int(numbered_match.group(2))
        else:
            type_part = section_part.lower().strip()
            number = None
        
        # Normalize section type using our mappings
        normalized_type = self.section_mappings.get(type_part, type_part)
        
        return normalized_type, number
    
    def extract_artists(self, artist_part: str) -> List[str]:
        """Extract artist names from artist attribution"""
        if not artist_part:
            return []
        
        # Common separators found in real data
        separators = [' with ', ' & ', ' and ', ' feat. ', ' featuring ', ' ft. ', ', ']
        
        artists = [artist_part]
        
        # Split by separators
        for separator in separators:
            new_artists = []
            for artist in artists:
                new_artists.extend(artist.split(separator))
            artists = new_artists
        
        # Clean up artist names
        cleaned_artists = []
        for artist in artists:
            cleaned = artist.strip()
            if cleaned and len(cleaned) > 1:
                cleaned_artists.append(cleaned)
        
        return cleaned_artists
    
    def parse_lyrics_to_sections(self, lyrics: str, track_title: str = "") -> List[LyricSection]:
        """Parse full lyrics text into structured sections"""
        sections = []
        
        # Find all section headers and their positions
        headers_with_positions = []
        for match in self.section_pattern.finditer(lyrics):
            header_text = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            headers_with_positions.append((header_text, start_pos, end_pos))
        
        if not headers_with_positions:
            # No structure headers found - treat as single section
            print(f"⚠️  No structure headers found in '{track_title}' - treating as single section")
            return [LyricSection(
                section_type='unknown',
                section_number=None,
                artists=[],
                lyrics_content=lyrics.strip(),
                order=1,
                original_header='[Full Song]'
            )]
        
        # Extract content between headers
        for i, (header_text, start_pos, end_pos) in enumerate(headers_with_positions):
            # Get content after this header until next header (or end)
            content_start = end_pos
            if i + 1 < len(headers_with_positions):
                content_end = headers_with_positions[i + 1][1]
            else:
                content_end = len(lyrics)
            
            content = lyrics[content_start:content_end].strip()
            
            # Skip empty sections
            if not content:
                continue
            
            # Parse header
            section_type, section_number, artists = self.parse_section_header(header_text)
            
            # Create section object
            section = LyricSection(
                section_type=section_type,
                section_number=section_number,
                artists=artists,
                lyrics_content=content,
                order=i + 1,
                original_header=f'[{header_text}]'
            )
            
            sections.append(section)
        
        return sections
    
    def store_structured_lyrics_in_auradb(self, track_name: str, sections: List[LyricSection]) -> bool:
        """Store structured lyrics in AuraDB"""
        try:
            with self.driver.session() as session:
                # Update track with parsing metadata
                session.run("""
                    MATCH (t:Track {name: $track_name})
                    SET t.lyrics_parsed = true,
                        t.section_count = $section_count,
                        t.lyrics_parse_date = datetime()
                """, {
                    'track_name': track_name,
                    'section_count': len(sections)
                })
                
                # Create section nodes and relationships
                for section in sections:
                    section_result = session.run("""
                        MATCH (t:Track {name: $track_name})
                        CREATE (s:LyricSection {
                            section_type: $section_type,
                            section_number: $section_number,
                            lyrics_content: $lyrics_content,
                            order: $order,
                            original_header: $original_header,
                            word_count: $word_count,
                            created_date: datetime()
                        })
                        CREATE (t)-[:HAS_SECTION]->(s)
                        RETURN id(s) as section_id
                    """, {
                        'track_name': track_name,
                        'section_type': section.section_type,
                        'section_number': section.section_number,
                        'lyrics_content': section.lyrics_content,
                        'order': section.order,
                        'original_header': section.original_header,
                        'word_count': len(section.lyrics_content.split())
                    })
                    
                    section_id = section_result.single()['section_id']
                    
                    # Create artist attribution relationships if any
                    for artist_name in section.artists:
                        session.run("""
                            MATCH (s:LyricSection)
                            WHERE id(s) = $section_id
                            MERGE (a:Artist {name: $artist_name})
                            CREATE (s)-[:PERFORMED_BY]->(a)
                        """, {
                            'section_id': section_id,
                            'artist_name': artist_name
                        })
                
                return True
                
        except Exception as e:
            print(f"❌ Error storing structured lyrics for '{track_name}': {e}")
            return False
    
    def test_parser_with_sample(self):
        """Test the parser with sample data to verify it works"""
        print("🧪 Testing parser with sample Genius format...")
        
        # Sample lyrics in real Genius format (structure only, no copyrighted content)
        sample_lyrics = """[Verse 1]
Sample verse content here
More verse content

[Pre-Chorus]
Pre-chorus content

[Chorus: Artist Name]
Chorus content here
More chorus content

[Verse 2: Artist Name & Featured Artist]
Second verse content
Additional content

[Chorus]
Chorus repeat

[Bridge]
Bridge content

[Outro]
Outro content"""
        
        sections = self.parse_lyrics_to_sections(sample_lyrics, "Test Song")
        
        print(f"✅ Parsed {len(sections)} sections:")
        for section in sections:
            print(f"  • {section.section_type.title()}: {len(section.lyrics_content)} chars")
            if section.artists:
                print(f"    Artists: {', '.join(section.artists)}")
        
        return len(sections) > 0
    
    def process_tracks_from_auradb(self, limit: int = None) -> Dict[str, int]:
        """Process tracks with lyrics from AuraDB"""
        print("🎵 Processing tracks from AuraDB for structure parsing...")
        print("=" * 60)
        
        stats = {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
        
        try:
            with self.driver.session() as session:
                # Get tracks with lyrics that haven't been parsed
                query = """
                    MATCH (t:Track)
                    WHERE t.lyrics_full IS NOT NULL 
                    AND (t.lyrics_parsed IS NULL OR t.lyrics_parsed = false)
                    RETURN t.name as track_name, t.lyrics_full as lyrics
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                result = session.run(query)
                tracks = list(result)
                
                print(f"📊 Found {len(tracks)} tracks to process")
                
                for track in tracks:
                    track_name = track['track_name']
                    lyrics = track['lyrics']
                    
                    print(f"\n🎵 Processing: {track_name}")
                    
                    # Parse lyrics structure
                    sections = self.parse_lyrics_to_sections(lyrics, track_name)
                    
                    if sections:
                        # Store structured data
                        success = self.store_structured_lyrics_in_auradb(track_name, sections)
                        
                        if success:
                            stats['successful'] += 1
                            print(f"  ✅ Parsed {len(sections)} sections")
                        else:
                            stats['failed'] += 1
                            print(f"  ❌ Failed to store sections")
                    else:
                        stats['skipped'] += 1
                        print(f"  ⚠️  No parseable structure found")
                    
                    stats['processed'] += 1
                
        except Exception as e:
            print(f"❌ Error processing tracks: {e}")
        
        return stats
    
    def analyze_parsing_results(self):
        """Analyze the results of structure parsing"""
        print("\n📊 PARSING RESULTS ANALYSIS")
        print("=" * 60)
        
        try:
            with self.driver.session() as session:
                # Section type distribution
                result = session.run("""
                    MATCH (s:LyricSection)
                    RETURN s.section_type as section_type, count(s) as count
                    ORDER BY count DESC
                """)
                
                print(f"🎼 Section Type Distribution:")
                for record in result:
                    section_type = record['section_type']
                    count = record['count']
                    print(f"  • {section_type.title()}: {count} sections")
                
        except Exception as e:
            print(f"❌ Error analyzing results: {e}")
    
    def run_full_parsing(self, limit: int = None):
        """Run complete lyrics structure parsing pipeline"""
        try:
            print("🎵 Week 2: Lyrics Structure Parser")
            print("=" * 60)
            
            # Test parser first
            if self.test_parser_with_sample():
                print("✅ Parser test successful!")
            else:
                print("❌ Parser test failed!")
                return
            
            # Process tracks
            stats = self.process_tracks_from_auradb(limit)
            
            # Analyze results
            self.analyze_parsing_results()
            
            # Summary
            print(f"\n🎉 PARSING COMPLETE!")
            print("=" * 60)
            print(f"✅ Processed: {stats['processed']} tracks")
            print(f"✅ Successful: {stats['successful']} tracks")
            print(f"❌ Failed: {stats['failed']} tracks")
            print(f"⚠️  Skipped: {stats['skipped']} tracks")
            
            if stats['successful'] > 0:
                success_rate = stats['successful'] / stats['processed'] * 100 if stats['processed'] > 0 else 0
                print(f"📈 Success Rate: {success_rate:.1f}%")
                print("✅ Ready for Week 3: Thematic Analysis!")
            
        except Exception as e:
            print(f"❌ Parsing pipeline failed: {e}")
        finally:
            if self.driver:
                self.driver.close()
                print("✅ Database connection closed")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse lyrics structure from AuraDB')
    parser.add_argument('--limit', type=int, help='Limit number of tracks to process')
    parser.add_argument('--test', action='store_true', help='Run test only')
    args = parser.parse_args()
    
    try:
        lyrics_parser = GeniusLyricsParser()
        
        if args.test:
            # Test only
            lyrics_parser.test_parser_with_sample()
        else:
            # Full processing
            lyrics_parser.run_full_parsing(limit=args.limit)
            
    except Exception as e:
        print(f"❌ Failed to initialize parser: {e}")
        print("\n💡 Make sure you have:")
        print("  • AuraDB credentials in .env file")
        print("  • Tracks with lyrics in your database")

if __name__ == "__main__":
    main() 