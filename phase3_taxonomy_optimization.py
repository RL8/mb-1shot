#!/usr/bin/env python3
"""
Phase 3: Performance Optimization + Music Taxonomy
Using proven AuraDB patterns from Phase 1 & 2
"""

from neo4j import GraphDatabase
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_phase3():
    """Execute Phase 3: Performance indexes + music taxonomy"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            logger.info("🔄 Phase 3: Creating performance indexes...")
            
            # Step 1: Create performance indexes
            indexes = [
                "CREATE INDEX word_id_index IF NOT EXISTS FOR (w:WordDictionary) ON (w.id)",
                "CREATE INDEX song_complexity_index IF NOT EXISTS FOR (s:Song) ON (s.vocabulary_complexity)",
                "CREATE INDEX song_energy_index IF NOT EXISTS FOR (s:Song) ON (s.energy)",
                "CREATE INDEX song_valence_index IF NOT EXISTS FOR (s:Song) ON (s.valence)"
            ]
            
            indexes_created = 0
            for index_query in indexes:
                try:
                    session.run(index_query)
                    indexes_created += 1
                    logger.info(f"✅ Created performance index")
                except Exception as e:
                    logger.warning(f"⚠️ Index may already exist")
            
            logger.info(f"📊 Performance indexes ready")
            
            # Step 2: Calculate music taxonomies
            logger.info("🔄 Calculating music taxonomies...")
            
            # Calculate taxonomies using AuraDB bulk operations
            taxonomy_query = """
            MATCH (s:Song)
            WHERE s.energy IS NOT NULL 
              AND s.valence IS NOT NULL
              AND s.vocabulary_complexity IS NOT NULL
              AND s.vocabulary_complexity > 0
            
            // Calculate enhanced taxonomies using word data
            SET s.taxonomy_energy_level = s.energy * 0.6 + (s.vocabulary_complexity * 0.4),
                s.taxonomy_emotional_valence = s.valence * 0.7 + ((1.0 - s.vocabulary_complexity) * 0.3),
                s.taxonomy_musical_complexity = (1 - s.acousticness) * 0.5 + s.vocabulary_complexity * 0.5,
                s.taxonomy_lyrical_intelligence = s.vocabulary_complexity * 0.6 + (s.unique_word_count / 100.0) * 0.4,
                s.taxonomy_singalong_potential = (1 - s.vocabulary_complexity) * 0.5 + s.valence * 0.5,
                s.taxonomy_calculated_at = datetime(),
                s.taxonomy_version = 'phase3_v1.0'
            
            RETURN count(s) as taxonomies_calculated
            """
            
            result = session.run(taxonomy_query)
            taxonomies_calculated = result.single()["taxonomies_calculated"]
            
            logger.info(f"✅ Calculated taxonomies for {taxonomies_calculated:,} songs")
            
            # Step 3: Final validation
            logger.info("🔄 Validating complete system...")
            
            validation_query = """
            MATCH (wd:WordDictionary)
            WITH count(wd) as total_words
            
            MATCH (s:Song) WHERE s.taxonomy_energy_level IS NOT NULL
            WITH total_words, count(s) as songs_with_taxonomies,
                 avg(s.vocabulary_complexity) as avg_complexity,
                 avg(s.taxonomy_energy_level) as avg_energy,
                 avg(s.taxonomy_lyrical_intelligence) as avg_intelligence
            
            MATCH (l:LyricLine) WHERE l.word_sequence IS NOT NULL
            WITH total_words, songs_with_taxonomies, avg_complexity,
                 avg_energy, avg_intelligence,
                 count(l) as converted_lines
            
            RETURN total_words, songs_with_taxonomies, converted_lines,
                   avg_complexity, avg_energy, avg_intelligence
            """
            
            val_result = session.run(validation_query)
            validation_stats = val_result.single()
            
            logger.info("📊 Complete System Validation:")
            logger.info(f"   WordDictionary entries: {validation_stats['total_words']:,}")
            logger.info(f"   Songs with taxonomies: {validation_stats['songs_with_taxonomies']:,}")
            logger.info(f"   Converted lyric lines: {validation_stats['converted_lines']:,}")
            logger.info(f"   Average vocabulary complexity: {validation_stats['avg_complexity']:.3f}")
            logger.info(f"   Average energy level: {validation_stats['avg_energy']:.3f}")
            logger.info(f"   Average lyrical intelligence: {validation_stats['avg_intelligence']:.3f}")
            
            return {
                'indexes_created': indexes_created,
                'taxonomies_calculated': taxonomies_calculated,
                'validation_stats': dict(validation_stats)
            }
            
    except Exception as e:
        logger.error(f"❌ Error in Phase 3: {e}")
        return None
    finally:
        driver.close()

if __name__ == "__main__":
    print("🚀 Starting Phase 3: Performance Optimization + Music Taxonomy")
    print("=" * 65)
    
    start_time = time.time()
    results = run_phase3()
    execution_time = time.time() - start_time
    
    if results:
        print(f"\n🎉 Phase 3 Complete!")
        print(f"   Performance Indexes: {results['indexes_created']}")
        print(f"   Taxonomies Calculated: {results['taxonomies_calculated']:,}")
        print(f"   Execution Time: {execution_time:.2f}s")
        print(f"\n✅ Complete Unified System Ready!")
    else:
        print(f"\n❌ Phase 3 failed - check logs") 