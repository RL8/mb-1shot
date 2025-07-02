#!/usr/bin/env python3
"""
AuraDB Structure Checker
Examine current lyric data structure and assess natural grouping enhancement options
"""

import os
import json
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
load_dotenv(env_path)

class AuraDBStructureChecker:
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

    def check_current_structure(self):
        """Examine current lyric line structure"""
        print("\n📊 CURRENT AURADB LYRIC STRUCTURE")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Check lyric line properties
            query = """
            MATCH (line:LyricLine)
            RETURN DISTINCT keys(line) as properties
            LIMIT 1
            """
            result = session.run(query)
            properties = result.single()
            if properties:
                print(f"📝 Current LyricLine properties: {properties['properties']}")
            
            # Sample a few lyric lines to understand structure
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title CONTAINS "Love Story"
            RETURN song.title, line.order, line.text, line.songPart
            ORDER BY line.order
            LIMIT 10
            """
            result = session.run(query)
            
            print(f"\n🎵 Sample Lyric Lines (Love Story):")
            for record in result:
                print(f"   Order {record['line.order']}: [{record['line.songPart']}] {record['line.text'][:50]}...")

    def analyze_section_patterns(self):
        """Analyze how sections are currently organized"""
        print("\n🔍 SECTION PATTERN ANALYSIS")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Count sections by type
            query = """
            MATCH (line:LyricLine)
            RETURN line.songPart as section_type, count(*) as line_count
            ORDER BY line_count DESC
            """
            result = session.run(query)
            
            print("📊 Section Distribution:")
            for record in result:
                print(f"   {record['section_type']}: {record['line_count']} lines")
            
            # Analyze section transitions in one song
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = "Anti-Hero"
            RETURN line.order, line.songPart
            ORDER BY line.order
            """
            result = session.run(query)
            
            print(f"\n🎼 Section Flow Example (Anti-Hero):")
            prev_part = None
            section_count = {}
            
            for record in result:
                part = record['line.songPart']
                order = record['line.order']
                
                if part != prev_part:
                    if part not in section_count:
                        section_count[part] = 1
                    else:
                        section_count[part] += 1
                    
                    print(f"   Order {order}: {part} #{section_count[part]}")
                    prev_part = part

    def assess_enhancement_feasibility(self):
        """Assess if we can add natural grouping fields"""
        print("\n🔧 ENHANCEMENT FEASIBILITY ASSESSMENT")
        print("=" * 50)
        
        with self.driver.session() as session:
            # Count total lyric lines
            query = "MATCH (line:LyricLine) RETURN count(*) as total_lines"
            result = session.run(query)
            total_lines = result.single()['total_lines']
            
            print(f"📊 Total lyric lines to potentially update: {total_lines:,}")
            
            # Check if we can calculate section numbers from existing data
            query = """
            MATCH (song:Song)-[:HAS_LYRIC]->(line:LyricLine)
            WHERE song.title = "Love Story"
            WITH song, line
            ORDER BY line.order
            WITH song, collect({order: line.order, part: line.songPart}) as lines
            RETURN song.title, lines[0..15] as sample_lines
            """
            result = session.run(query)
            
            print(f"\n🧮 Section Grouping Calculation Test:")
            for record in result:
                lines = record['sample_lines']
                current_section = None
                section_number = 0
                
                print(f"   Song: {record['song.title']}")
                for line in lines:
                    if line['part'] != current_section:
                        current_section = line['part']
                        section_number += 1
                        print(f"   Order {line['order']}: {line['part']} → Could be {line['part']} #{section_number}")

    def propose_update_strategy(self):
        """Propose strategy for adding natural grouping"""
        print("\n🚀 PROPOSED UPDATE STRATEGY")
        print("=" * 50)
        
        print("✅ DIRECT DATABASE UPDATE APPROACH:")
        print("   1. Add new properties to existing LyricLine nodes")
        print("   2. Calculate values from existing order + songPart data")
        print("   3. Use Cypher queries to batch update in chunks")
        print("   4. No need to reload entire dataset")
        
        print("\n📋 New Properties to Add:")
        properties = [
            "sectionNumber (int): Verse 1, Verse 2, etc.",
            "sectionId (string): 'verse_1', 'chorus_1', etc.", 
            "lineInSection (int): Line position within section",
            "sectionStart (boolean): First line of section",
            "sectionEnd (boolean): Last line of section",
            "repeatInstance (int): 1st, 2nd occurrence of same section"
        ]
        for prop in properties:
            print(f"   • {prop}")
            
        print("\n⚡ Performance Estimate:")
        print("   • Batch size: 1,000 lines per transaction")
        print("   • Processing time: ~2-3 minutes for full dataset")
        print("   • Memory efficient: No data reload required")

    def run_full_analysis(self):
        """Run complete structure analysis"""
        try:
            self.check_current_structure()
            self.analyze_section_patterns()
            self.assess_enhancement_feasibility()
            self.propose_update_strategy()
            
            print(f"\n✅ ANALYSIS COMPLETE!")
            print(f"💡 Recommendation: Direct database enhancement is feasible and efficient")
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
        finally:
            self.driver.close()

if __name__ == "__main__":
    checker = AuraDBStructureChecker()
    checker.run_full_analysis() 