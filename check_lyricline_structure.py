#!/usr/bin/env python3
"""
Diagnostic: Check LyricLine Structure
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

def check_lyricline_structure():
    """Examine LyricLine node structure"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            print("🔍 Checking LyricLine structure...")
            
            # Check sample LyricLine properties
            sample_query = """
            MATCH (s:Song)-[:HAS_LYRIC]->(l:LyricLine)
            WITH l LIMIT 5
            RETURN l.lineText as text, 
                   l.lineNumber as number,
                   keys(l) as properties
            """
            
            print("\n📝 Sample LyricLine data:")
            result = session.run(sample_query)
            for i, record in enumerate(result):
                print(f"   Line {i+1}:")
                print(f"     Text: '{record['text']}'")
                print(f"     Number: {record['number']}")
                print(f"     Properties: {record['properties']}")
            
            # Check text content statistics
            content_query = """
            MATCH (l:LyricLine)
            WHERE l.lineText IS NOT NULL
            RETURN count(l) as total_with_text,
                   count(CASE WHEN l.lineText <> '' THEN 1 END) as non_empty,
                   avg(size(l.lineText)) as avg_length,
                   collect(l.lineText)[0..3] as samples
            """
            
            print("\n📊 LyricLine content analysis:")
            result = session.run(content_query)
            stats = result.single()
            print(f"   Total with text: {stats['total_with_text']:,}")
            print(f"   Non-empty: {stats['non_empty']:,}")
            print(f"   Average length: {stats['avg_length']:.1f}")
            print(f"   Samples: {stats['samples']}")
            
            # Test simple text splitting (without APOC)
            print("\n🧪 Testing simple text splitting:")
            test_query = """
            MATCH (l:LyricLine)
            WHERE l.lineText IS NOT NULL AND l.lineText <> ''
            WITH l LIMIT 1
            WITH l, split(toLower(l.lineText), ' ') as words
            RETURN l.lineText as original_text,
                   words,
                   size(words) as word_count
            """
            
            result = session.run(test_query)
            for record in result:
                print(f"   Original: '{record['original_text']}'")
                print(f"   Words: {record['words']}")
                print(f"   Count: {record['word_count']}")
            
            # Test APOC availability
            print("\n🔧 Testing APOC functions:")
            try:
                apoc_test = session.run("RETURN apoc.version() as version")
                version = apoc_test.single()["version"]
                print(f"   APOC version: {version}")
                
                # Test apoc.text.split specifically
                apoc_split_test = session.run("""
                    RETURN apoc.text.split('hello world test', ' ') as split_result
                """)
                split_result = apoc_split_test.single()["split_result"]
                print(f"   APOC split test: {split_result}")
                
            except Exception as e:
                print(f"   APOC error: {e}")
            
    except Exception as e:
        print(f"❌ Error checking structure: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    check_lyricline_structure() 