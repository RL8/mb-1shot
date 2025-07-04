#!/usr/bin/env python3
"""
Quick Implementation - Phase 1: Word Registry Creation
Adapted for actual database structure
"""

from neo4j import GraphDatabase
import hashlib
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_word_registry():
    """Create WordDictionary from existing Song->Word relationships"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            logger.info("🔄 Phase 1: Creating word registry from Song->Word relationships...")
            
            # Create WordDictionary nodes using proper AuraDB bulk pattern
            query = """
            // Step 1: Group by word text and aggregate data
            MATCH (s:Song)-[r:CONTAINS_WORD]->(w:Word)
            WITH w.text as word_text, 
                 sum(r.count) as total_frequency,
                 count(DISTINCT s) as song_count,
                 collect(DISTINCT s.albumCode) as albums
            
            // Step 2: Prepare data for bulk creation using APOC
            WITH collect({
                text: word_text,
                frequency: total_frequency,
                song_count: song_count,
                album_spread: size(apoc.coll.toSet(albums))
            }) as word_data_list
            
            // Step 3: Bulk create WordDictionary nodes
            UNWIND word_data_list as word_data
            CREATE (wd:WordDictionary {
                id: 'word_' + substring(apoc.util.md5([word_data.text]), 0, 8),
                text: word_data.text,
                frequency: word_data.frequency,
                song_usage_count: word_data.song_count,
                album_spread: word_data.album_spread,
                created_at: datetime(),
                system_version: 'adapted_v1.0'
            })
            
            RETURN count(wd) as words_created
            """
            
            result = session.run(query)
            words_created = result.single()["words_created"]
            
            logger.info(f"✅ Created {words_created} WordDictionary entries")
            
            # Validation check
            validation_query = """
            MATCH (wd:WordDictionary)
            RETURN count(wd) as total,
                   avg(wd.frequency) as avg_frequency,
                   max(wd.frequency) as max_frequency,
                   min(wd.frequency) as min_frequency
            """
            
            val_result = session.run(validation_query)
            stats = val_result.single()
            
            logger.info("📊 WordDictionary Statistics:")
            logger.info(f"   Total entries: {stats['total']:,}")
            logger.info(f"   Average frequency: {stats['avg_frequency']:.1f}")
            logger.info(f"   Max frequency: {stats['max_frequency']:,}")
            logger.info(f"   Min frequency: {stats['min_frequency']:,}")
            
            return words_created
            
    except Exception as e:
        logger.error(f"❌ Error creating word registry: {e}")
        return 0
    finally:
        driver.close()

if __name__ == "__main__":
    print("🚀 Starting Phase 1: Word Registry Creation")
    print("=" * 50)
    
    start_time = time.time()
    words_created = create_word_registry()
    execution_time = time.time() - start_time
    
    print(f"\n🎉 Phase 1 Complete!")
    print(f"   Words Created: {words_created:,}")
    print(f"   Execution Time: {execution_time:.2f}s")
    
    if words_created > 0:
        print("\n✅ Ready for Phase 2: Lyric Line Conversion")
    else:
        print("\n❌ Phase 1 failed - check logs") 