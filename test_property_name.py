#!/usr/bin/env python3
"""
Quick test to verify LyricLine property name
"""

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv("AURA_DB_URI")
username = os.getenv("AURA_DB_USERNAME", "neo4j")
password = os.getenv("AURA_DB_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(username, password))

try:
    with driver.session() as session:
        # Test with 'text' property
        result = session.run("""
            MATCH (l:LyricLine) 
            WHERE l.text IS NOT NULL AND l.text <> ''
            RETURN count(l) as count_with_text, 
                   l.text as sample_text 
            LIMIT 1
        """)
        
        for record in result:
            print(f"Lines with 'text' property: {record['count_with_text']}")
            print(f"Sample text: '{record['sample_text']}'")
            
        # Test simple word conversion
        test_result = session.run("""
            MATCH (l:LyricLine) 
            WHERE l.text IS NOT NULL AND l.text <> ''
            WITH l LIMIT 1
            WITH l, split(toLower(l.text), ' ') as words
            RETURN size(words) as word_count, words[0..3] as sample_words
        """)
        
        for record in test_result:
            print(f"Word count: {record['word_count']}")
            print(f"Sample words: {record['sample_words']}")

finally:
    driver.close() 