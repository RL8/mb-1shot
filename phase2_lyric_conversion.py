#!/usr/bin/env python3
"""
Phase 2: Lyric Line to Word Sequence Conversion
Using proven AuraDB patterns from Phase 1
"""

from neo4j import GraphDatabase
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_lyric_lines_to_sequences():
    """Convert LyricLine nodes to word ID sequences using WordDictionary"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            logger.info("🔄 Phase 2: Converting LyricLines to word sequences...")
            
            # Step 1: Get total count for progress tracking
            total_query = "MATCH (l:LyricLine) RETURN count(l) as total"
            total_lines = session.run(total_query).single()["total"]
            logger.info(f"📊 Processing {total_lines:,} lyric lines...")
            
            # Step 2: Convert LyricLines to word sequences using corrected property
            conversion_query = """
            // Process LyricLine nodes using correct property name 'text'
            MATCH (s:Song)-[:HAS_LYRIC]->(l:LyricLine)
            WHERE l.text IS NOT NULL AND l.text <> ''
            
            // Convert text to word IDs using standard split function
            WITH s, l, 
                 [word IN split(toLower(l.text), ' ') 
                  WHERE word <> '' AND word IS NOT NULL |
                  'word_' + substring(apoc.util.md5([word]), 0, 8)
                 ] as word_ids
            
            // Set word sequence properties
            SET l.word_sequence = word_ids,
                l.conversion_timestamp = datetime(),
                l.word_count = size(word_ids),
                l.unique_word_count = size(apoc.coll.toSet(word_ids)),
                l.system_version = 'phase2_v1.0'
            
            RETURN count(l) as lines_converted
            """
            
            result = session.run(conversion_query)
            lines_converted = result.single()["lines_converted"]
            
            logger.info(f"✅ Converted {lines_converted:,} lyric lines to word sequences")
            
            # Step 3: Calculate song-level word statistics
            logger.info("🔄 Calculating song-level word statistics...")
            
            stats_query = """
            // Aggregate word data from LyricLines per song using APOC
            MATCH (s:Song)-[:HAS_LYRIC]->(l:LyricLine)
            WHERE l.word_sequence IS NOT NULL
            
            // Calculate comprehensive word statistics
            WITH s, 
                 apoc.coll.flatten(collect(l.word_sequence)) as all_word_ids,
                 avg(l.word_count) as avg_words_per_line,
                 count(l) as total_lines
            
            // Set enhanced word statistics using AuraDB bulk update
            SET s.total_word_count = size(all_word_ids),
                s.unique_word_count = size(apoc.coll.toSet(all_word_ids)),
                s.vocabulary_complexity = toFloat(size(apoc.coll.toSet(all_word_ids))) / size(all_word_ids),
                s.avg_words_per_line = avg_words_per_line,
                s.total_lyric_lines = total_lines,
                s.word_conversion_completed = datetime(),
                s.word_system_version = 'phase2_v1.0'
            
            RETURN count(s) as songs_updated
            """
            
            result = session.run(stats_query)
            songs_updated = result.single()["songs_updated"]
            
            logger.info(f"✅ Updated word statistics for {songs_updated:,} songs")
            
            # Step 4: Validation check
            validation_query = """
            MATCH (s:Song)
            WHERE s.vocabulary_complexity IS NOT NULL
            RETURN count(s) as songs_with_stats,
                   avg(s.vocabulary_complexity) as avg_complexity,
                   avg(s.unique_word_count) as avg_unique_words,
                   avg(s.total_word_count) as avg_total_words
            """
            
            val_result = session.run(validation_query)
            stats = val_result.single()
            
            logger.info("📊 Phase 2 Statistics:")
            logger.info(f"   Songs with word stats: {stats['songs_with_stats']:,}")
            logger.info(f"   Average vocabulary complexity: {stats['avg_complexity']:.3f}")
            logger.info(f"   Average unique words: {stats['avg_unique_words']:.1f}")
            logger.info(f"   Average total words: {stats['avg_total_words']:.1f}")
            
            return {
                'lines_converted': lines_converted,
                'songs_updated': songs_updated,
                'validation_stats': dict(stats)
            }
            
    except Exception as e:
        logger.error(f"❌ Error in Phase 2: {e}")
        return None
    finally:
        driver.close()

if __name__ == "__main__":
    print("🚀 Starting Phase 2: Lyric Line to Word Sequence Conversion")
    print("=" * 60)
    
    start_time = time.time()
    results = convert_lyric_lines_to_sequences()
    execution_time = time.time() - start_time
    
    if results:
        print(f"\n🎉 Phase 2 Complete!")
        print(f"   Lyric Lines Converted: {results['lines_converted']:,}")
        print(f"   Songs Updated: {results['songs_updated']:,}")
        print(f"   Execution Time: {execution_time:.2f}s")
        print("\n✅ Ready for Phase 3: Music Taxonomy Calculation")
    else:
        print("\n❌ Phase 2 failed - check logs") 