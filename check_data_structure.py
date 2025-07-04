#!/usr/bin/env python3
"""
Check Current Database Structure
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

def check_data_structure():
    """Examine current database structure"""
    
    uri = os.getenv("AURA_DB_URI")
    username = os.getenv("AURA_DB_USERNAME", "neo4j")
    password = os.getenv("AURA_DB_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    try:
        with driver.session() as session:
            print("🔍 Checking database structure...")
            
            # Check node types and relationships
            structure_check = session.run("""
                CALL db.schema.visualization()
            """)
            
            # Check sample song structure
            print("\n📀 Sample Song structure:")
            song_sample = session.run("""
                MATCH (s:Song)
                WITH s LIMIT 1
                OPTIONAL MATCH (s)-[r1]->(connected1)
                OPTIONAL MATCH (connected1)-[r2]->(connected2)
                RETURN s, labels(s) as song_labels, 
                       collect(DISTINCT type(r1)) as direct_relationships,
                       collect(DISTINCT labels(connected1)) as connected_labels
            """)
            
            for record in song_sample:
                print(f"   Song labels: {record['song_labels']}")
                print(f"   Direct relationships: {record['direct_relationships']}")
                print(f"   Connected node types: {record['connected_labels']}")
            
            # Check if there are Lyric nodes vs LyricLine nodes
            print("\n📝 Checking lyric storage:")
            lyric_checks = [
                ("Lyric nodes", "MATCH (l:Lyric) RETURN count(l) as count"),
                ("LyricLine nodes", "MATCH (l:LyricLine) RETURN count(l) as count"),
                ("Verse nodes", "MATCH (v:Verse) RETURN count(v) as count")
            ]
            
            for name, query in lyric_checks:
                try:
                    result = session.run(query)
                    count = result.single()["count"]
                    print(f"   {name}: {count:,}")
                except:
                    print(f"   {name}: 0 (not found)")
            
            # Check relationships from Song to lyrics/words
            print("\n🔗 Checking Song relationships:")
            song_rels = session.run("""
                MATCH (s:Song)-[r]->(target)
                RETURN type(r) as relationship_type, 
                       labels(target)[0] as target_type,
                       count(*) as count
                ORDER BY count DESC
            """)
            
            for record in song_rels:
                print(f"   {record['relationship_type']} -> {record['target_type']}: {record['count']:,}")
            
            # Check word relationships structure
            print("\n📚 Sample Word structure:")
            word_sample = session.run("""
                MATCH (w:Word)
                WITH w LIMIT 1
                MATCH (source)-[r]->(w)
                RETURN w.text as word, 
                       labels(source)[0] as source_type,
                       type(r) as relationship_type
            """)
            
            for record in word_sample:
                print(f"   Word: '{record['word']}'")
                print(f"   Source: {record['source_type']} -[{record['relationship_type']}]-> Word")
                
    except Exception as e:
        print(f"❌ Error checking structure: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    check_data_structure() 