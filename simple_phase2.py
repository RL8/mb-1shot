#!/usr/bin/env python3
"""
Simple Phase 2: Working Lyric Conversion
Based on successful property testing
"""

from neo4j import GraphDatabase
import time
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_phase2():
    """Execute Phase 2: Lyric line conversion"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            logger.info("🔄 Phase 2: Converting LyricLines to word sequences...")
            
            # Convert LyricLines to word sequences
            conversion_query = """
            MATCH (s:Song)-[:HAS_LYRIC]->(l:LyricLine)
            WHERE l.text IS NOT NULL AND l.text <> ''
            
            WITH s, l, 
                 [word IN split(toLower(l.text), ' ') 
                  WHERE word <> '' |
                  'word_' + substring(apoc.util.md5([word]), 0, 8)
                 ] as word_ids
            
            SET l.word_sequence = word_ids,
                l.word_count = size(word_ids),
                l.unique_word_count = size(apoc.coll.toSet(word_ids)),
                l.conversion_timestamp = datetime(),
                l.system_version = 'phase2_v1.0'
            
            RETURN count(l) as lines_converted
            """
            
            result = session.run(conversion_query)
            lines_converted = result.single()["lines_converted"]
            logger.info(f"✅ Converted {lines_converted:,} lyric lines")
            
            # Calculate song statistics
            logger.info("🔄 Calculating song statistics...")
            
            stats_query = """
            MATCH (s:Song)-[:HAS_LYRIC]->(l:LyricLine)
            WHERE l.word_sequence IS NOT NULL
            
            WITH s, 
                 apoc.coll.flatten(collect(l.word_sequence)) as all_word_ids,
                 avg(l.word_count) as avg_words_per_line,
                 count(l) as total_lines
            
            SET s.total_word_count = size(all_word_ids),
                s.unique_word_count = size(apoc.coll.toSet(all_word_ids)),
                s.vocabulary_complexity = toFloat(size(apoc.coll.toSet(all_word_ids))) / size(all_word_ids),
                s.avg_words_per_line = avg_words_per_line,
                s.total_lyric_lines = total_lines,
                s.word_conversion_completed = datetime()
            
            RETURN count(s) as songs_updated
            """
            
            result = session.run(stats_query)
            songs_updated = result.single()["songs_updated"]
            logger.info(f"✅ Updated {songs_updated:,} songs with word statistics")
            
            # Validation
            validation_query = """
            MATCH (s:Song)
            WHERE s.vocabulary_complexity IS NOT NULL
            RETURN count(s) as total,
                   avg(s.vocabulary_complexity) as avg_complexity,
                   avg(s.unique_word_count) as avg_unique_words
            """
            
            val_result = session.run(validation_query)
            stats = val_result.single()
            
            logger.info("📊 Results:")
            logger.info(f"   Songs with statistics: {stats['total']:,}")
            logger.info(f"   Average vocabulary complexity: {stats['avg_complexity']:.3f}")
            logger.info(f"   Average unique words per song: {stats['avg_unique_words']:.1f}")
            
            return {
                'lines_converted': lines_converted,
                'songs_updated': songs_updated,
                'avg_complexity': stats['avg_complexity']
            }
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None
    finally:
        driver.close()

if __name__ == "__main__":
    print("🚀 Starting Simple Phase 2")
    print("=" * 40)
    
    start_time = time.time()
    results = run_phase2()
    execution_time = time.time() - start_time
    
    if results:
        print(f"\n🎉 Phase 2 Complete!")
        print(f"   Lines Converted: {results['lines_converted']:,}")
        print(f"   Songs Updated: {results['songs_updated']:,}")
        print(f"   Execution Time: {execution_time:.2f}s")
        print(f"   Avg Complexity: {results['avg_complexity']:.3f}")
    else:
        print("\n❌ Phase 2 failed") 