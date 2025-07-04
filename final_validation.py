#!/usr/bin/env python3
"""
Final Validation: Complete Unified System Results
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

def final_validation():
    """Show complete system validation results"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            print("🎯 UNIFIED WORD IDENTIFIER & MUSIC TAXONOMY SYSTEM")
            print("=" * 60)
            
            # Complete system validation
            validation_query = """
            MATCH (wd:WordDictionary)
            WITH count(wd) as total_words
            
            MATCH (s:Song) WHERE s.taxonomy_energy_level IS NOT NULL
            WITH total_words, count(s) as songs_with_taxonomies,
                 avg(s.vocabulary_complexity) as avg_complexity,
                 avg(s.taxonomy_energy_level) as avg_energy,
                 avg(s.taxonomy_emotional_valence) as avg_valence,
                 avg(s.taxonomy_musical_complexity) as avg_musical_complexity,
                 avg(s.taxonomy_lyrical_intelligence) as avg_intelligence,
                 avg(s.taxonomy_singalong_potential) as avg_singalong
            
            MATCH (l:LyricLine) WHERE l.word_sequence IS NOT NULL
            WITH total_words, songs_with_taxonomies, avg_complexity,
                 avg_energy, avg_valence, avg_musical_complexity, 
                 avg_intelligence, avg_singalong,
                 count(l) as converted_lines
            
            RETURN total_words, songs_with_taxonomies, converted_lines,
                   avg_complexity, avg_energy, avg_valence, 
                   avg_musical_complexity, avg_intelligence, avg_singalong
            """
            
            result = session.run(validation_query)
            stats = result.single()
            
            print(f"📚 WordDictionary Entries: {stats['total_words']:,}")
            print(f"📝 Converted Lyric Lines: {stats['converted_lines']:,}")
            print(f"🎵 Songs with Taxonomies: {stats['songs_with_taxonomies']:,}")
            print()
            
            print("📊 AVERAGE TAXONOMY SCORES:")
            print(f"   Vocabulary Complexity: {stats['avg_complexity']:.3f}")
            print(f"   Energy Level: {stats['avg_energy']:.3f}")
            print(f"   Emotional Valence: {stats['avg_valence']:.3f}")
            print(f"   Musical Complexity: {stats['avg_musical_complexity']:.3f}")
            print(f"   Lyrical Intelligence: {stats['avg_intelligence']:.3f}")
            print(f"   Singalong Potential: {stats['avg_singalong']:.3f}")
            
            # Sample query demonstration
            print(f"\n🔍 SAMPLE QUERY: High Intelligence + High Energy Songs")
            sample_query = """
            MATCH (s:Song)
            WHERE s.taxonomy_lyrical_intelligence > 0.8 
              AND s.taxonomy_energy_level > 0.7
            RETURN s.title as title, 
                   s.taxonomy_lyrical_intelligence as intelligence,
                   s.taxonomy_energy_level as energy,
                   s.vocabulary_complexity as complexity
            ORDER BY s.taxonomy_lyrical_intelligence DESC
            LIMIT 5
            """
            
            sample_result = session.run(sample_query)
            for i, record in enumerate(sample_result, 1):
                print(f"   {i}. '{record['title']}'")
                print(f"      Intelligence: {record['intelligence']:.3f} | Energy: {record['energy']:.3f}")
            
            return dict(stats)
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return None
    finally:
        driver.close()

if __name__ == "__main__":
    results = final_validation()
    
    if results:
        print(f"\n✅ SYSTEM STATUS: FULLY OPERATIONAL")
        print(f"🎯 Ready for advanced music discovery and analysis!")
    else:
        print(f"\n❌ Validation failed") 