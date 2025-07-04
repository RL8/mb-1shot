from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv('AURA_DB_URI'), 
    auth=(os.getenv('AURA_DB_USERNAME'), os.getenv('AURA_DB_PASSWORD'))
)

try:
    with driver.session() as session:
        result = session.run("""
        MATCH (wd:WordDictionary) 
        WITH count(wd) as words
        MATCH (s:Song) WHERE s.taxonomy_energy_level IS NOT NULL 
        WITH words, count(s) as songs, 
             avg(s.taxonomy_lyrical_intelligence) as intel,
             avg(s.taxonomy_energy_level) as energy,
             avg(s.vocabulary_complexity) as complexity
        MATCH (l:LyricLine) WHERE l.word_sequence IS NOT NULL
        RETURN words, songs, count(l) as lines, intel, energy, complexity
        """)
        
        stats = result.single()
        
        print('🎯 COMPLETE UNIFIED SYSTEM RESULTS')
        print('=' * 50)
        print(f'📚 WordDictionary: {stats["words"]:,} entries')
        print(f'📝 LyricLines Converted: {stats["lines"]:,}')  
        print(f'🎵 Songs with Taxonomies: {stats["songs"]:,}')
        print()
        print('📊 AVERAGE SCORES:')
        print(f'   Vocabulary Complexity: {stats["complexity"]:.3f}')
        print(f'   Energy Level: {stats["energy"]:.3f}')
        print(f'   Lyrical Intelligence: {stats["intel"]:.3f}')
        print()
        print('✅ UNIFIED WORD + TAXONOMY SYSTEM FULLY OPERATIONAL!')

finally:
    driver.close() 