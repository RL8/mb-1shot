#!/usr/bin/env python3
"""
Natural Grouping Test Script
Test enhancement of one song with natural grouping properties
Shows before/after comparison to verify the improvements
"""

import os
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class NaturalGroupingTester:
    def __init__(self):
        """Initialize connection to AuraDB"""
        self.neo4j_uri = os.getenv('AURA_DB_URI')
        self.neo4j_user = os.getenv('AURA_DB_USERNAME')
        self.neo4j_password = os.getenv('AURA_DB_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
            raise ValueError("❌ Missing AuraDB credentials in environment variables")
        
        print(f"🔑 Connecting to AuraDB...")
        self.driver = GraphDatabase.driver(
            self.neo4j_uri, 
            auth=(self.neo4j_user, self.neo4j_password)
        )

    def show_before_state(self, song_title="Love Story"):
        """Show current structure before enhancement"""
        print(f"\n📊 BEFORE ENHANCEMENT - {song_title}")
        print("=" * 60)
        
        with self.driver.session() as session:
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = $song_title
            RETURN line.order, line.songPart, line.text
            ORDER BY line.order
            LIMIT 20
            """
            result = session.run(query, song_title=song_title)
            
            print(f"🎵 Current structure (showing first 20 lines):")
            for record in result:
                order = record['line.order']
                part = record['line.songPart']
                text = record['line.text'][:40] + "..." if len(record['line.text']) > 40 else record['line.text']
                print(f"   {order:2d}. [{part:10s}] {text}")

    def calculate_natural_grouping(self, song_title="Love Story"):
        """Calculate natural grouping data for one song"""
        print(f"\n🧮 CALCULATING NATURAL GROUPING - {song_title}")
        print("=" * 60)
        
        with self.driver.session() as session:
            # Get all lines for the song
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = $song_title
            RETURN line.order, line.songPart, line.text
            ORDER BY line.order
            """
            result = session.run(query, song_title=song_title)
            
            lines = []
            for record in result:
                lines.append({
                    'order': record['line.order'],
                    'songPart': record['line.songPart'],
                    'text': record['line.text']
                })
            
            print(f"📝 Processing {len(lines)} lyric lines...")
            
            # Calculate natural grouping
            enhanced_lines = []
            current_section = None
            section_counts = {}  # Track how many times each section type appears
            line_in_section = 0
            
            for i, line in enumerate(lines):
                part = line['songPart']
                
                # Detect section change
                if part != current_section:
                    current_section = part
                    line_in_section = 1
                    
                    # Count section occurrences
                    if part not in section_counts:
                        section_counts[part] = 1
                    else:
                        section_counts[part] += 1
                    
                    section_start = True
                else:
                    line_in_section += 1
                    section_start = False
                
                # Detect section end (look ahead)
                section_end = False
                if i < len(lines) - 1:  # Not last line
                    next_part = lines[i + 1]['songPart']
                    if next_part != part:
                        section_end = True
                else:  # Last line
                    section_end = True
                
                # Create enhanced line data
                enhanced_line = {
                    'order': line['order'],
                    'songPart': part,
                    'sectionNumber': section_counts[part],
                    'sectionId': f"{part.lower()}_{section_counts[part]}",
                    'lineInSection': line_in_section,
                    'sectionStart': section_start,
                    'sectionEnd': section_end,
                    'text': line['text']
                }
                enhanced_lines.append(enhanced_line)
            
            print(f"✅ Calculated natural grouping for {len(enhanced_lines)} lines")
            print(f"📊 Section summary: {section_counts}")
            return enhanced_lines

    def apply_enhancement(self, enhanced_lines, song_title="Love Story"):
        """Apply natural grouping enhancement to AuraDB"""
        print(f"\n🚀 APPLYING ENHANCEMENT - {song_title}")
        print("=" * 60)
        
        with self.driver.session() as session:
            # Update lines in batches
            batch_size = 50
            total_updated = 0
            
            for i in range(0, len(enhanced_lines), batch_size):
                batch = enhanced_lines[i:i + batch_size]
                
                # Create batch update query
                query = """
                UNWIND $batch as line_data
                MATCH (l:LyricLine)
                WHERE l.order = line_data.order
                SET l.sectionNumber = line_data.sectionNumber,
                    l.sectionId = line_data.sectionId,
                    l.lineInSection = line_data.lineInSection,
                    l.sectionStart = line_data.sectionStart,
                    l.sectionEnd = line_data.sectionEnd
                RETURN count(l) as updated_count
                """
                
                result = session.run(query, batch=batch)
                batch_updated = result.single()['updated_count']
                total_updated += batch_updated
                
                print(f"   📝 Updated batch {i//batch_size + 1}: {batch_updated} lines")
            
            print(f"✅ Total lines enhanced: {total_updated}")

    def show_after_state(self, song_title="Love Story"):
        """Show enhanced structure after enhancement"""
        print(f"\n🎉 AFTER ENHANCEMENT - {song_title}")
        print("=" * 60)
        
        with self.driver.session() as session:
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = $song_title
            RETURN line.order, line.songPart, line.sectionNumber, line.sectionId, 
                   line.lineInSection, line.sectionStart, line.sectionEnd, line.text
            ORDER BY line.order
            LIMIT 20
            """
            result = session.run(query, song_title=song_title)
            
            print(f"🎵 Enhanced structure (showing first 20 lines):")
            print(f"{'#':>2} {'Section':>12} {'Line':>4} {'S':>1} {'E':>1} {'Text':>40}")
            print("-" * 70)
            
            for record in result:
                order = record['line.order']
                section_id = record['line.sectionId'] or 'N/A'
                line_in_section = record['line.lineInSection'] or 0
                section_start = 'S' if record['line.sectionStart'] else ' '
                section_end = 'E' if record['line.sectionEnd'] else ' '
                text = record['line.text'][:35] + "..." if len(record['line.text']) > 35 else record['line.text']
                
                print(f"{order:2d} {section_id:>12} {line_in_section:>4} {section_start:>1} {section_end:>1} {text}")

    def verify_enhancement(self, song_title="Love Story"):
        """Verify the enhancement worked correctly"""
        print(f"\n✅ VERIFICATION - {song_title}")
        print("=" * 60)
        
        with self.driver.session() as session:
            # Check if new properties exist
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = $song_title AND line.sectionNumber IS NOT NULL
            RETURN count(line) as enhanced_lines,
                   count(DISTINCT line.sectionId) as unique_sections,
                   collect(DISTINCT line.songPart) as section_types
            """
            result = session.run(query, song_title=song_title)
            record = result.single()
            
            print(f"📊 Enhancement Results:")
            print(f"   • Enhanced lines: {record['enhanced_lines']}")
            print(f"   • Unique sections: {record['unique_sections']}")
            print(f"   • Section types: {record['section_types']}")
            
            # Show section summary
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = $song_title
            RETURN line.sectionId, count(*) as line_count,
                   min(line.order) as first_line, max(line.order) as last_line
            ORDER BY first_line
            """
            result = session.run(query, song_title=song_title)
            
            print(f"\n📋 Section Breakdown:")
            for record in result:
                section_id = record['line.sectionId']
                line_count = record['line_count']
                first_line = record['first_line']
                last_line = record['last_line']
                print(f"   • {section_id}: {line_count} lines (orders {first_line}-{last_line})")

    def run_test(self, song_title="Love Story"):
        """Run complete test for one song"""
        try:
            print(f"🧪 NATURAL GROUPING TEST - {song_title}")
            print("=" * 70)
            
            # Step 1: Show before state
            self.show_before_state(song_title)
            
            # Step 2: Calculate enhancement
            enhanced_lines = self.calculate_natural_grouping(song_title)
            
            # Step 3: Apply enhancement
            self.apply_enhancement(enhanced_lines, song_title)
            
            # Step 4: Show after state
            self.show_after_state(song_title)
            
            # Step 5: Verify enhancement
            self.verify_enhancement(song_title)
            
            print(f"\n🎉 TEST COMPLETE!")
            print(f"✅ Natural grouping successfully applied to '{song_title}'")
            
        except Exception as e:
            print(f"❌ Error during test: {e}")
        finally:
            self.driver.close()

if __name__ == "__main__":
    tester = NaturalGroupingTester()
    tester.run_test("Love Story")  # Test with Love Story 