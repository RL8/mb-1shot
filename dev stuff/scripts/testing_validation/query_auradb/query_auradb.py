#!/usr/bin/env python3
"""
Simple CLI for querying AuraDB - Music Besties
Usage: python query_auradb.py [query]
"""

import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../../../../.env.development')

def run_query(query, params=None):
    """Run any Cypher query against AuraDB"""
    uri = os.getenv('AURA_DB_URI')
    username = os.getenv('AURA_DB_USERNAME')
    password = os.getenv('AURA_DB_PASSWORD')
    
    if not all([uri, username, password]):
        print("❌ Missing AuraDB credentials in .env.development")
        return None
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        
        with driver.session() as session:
            result = session.run(query, params or {})
            records = []
            for record in result:
                records.append(dict(record))
            
        driver.close()
        return records
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def print_results(records, limit=20):
    """Pretty print query results"""
    if not records:
        print("No results found.")
        return
    
    print(f"📊 Found {len(records)} records")
    if len(records) > limit:
        print(f"Showing first {limit} records...")
        records = records[:limit]
    
    print("-" * 50)
    for i, record in enumerate(records, 1):
        print(f"{i:2d}. {record}")
    print("-" * 50)

def main():
    """Main CLI interface"""
    
    # Predefined useful queries
    preset_queries = {
        "artists": "MATCH (a:Artist) RETURN a.name as name ORDER BY a.name",
        "albums": "MATCH (al:Album) RETURN al.name as album, al.release_date as year ORDER BY al.name",
        "tracks": "MATCH (t:Track) RETURN t.name as track ORDER BY rand() LIMIT 20",
        "stats": "MATCH (n) RETURN distinct labels(n) as type, count(n) as count ORDER BY count DESC",
        "taylor": "MATCH (taylor:Artist {name: 'Taylor Swift'})-[:HAS_ALBUM]->(album:Album) OPTIONAL MATCH (album)-[:HAS_TRACK]->(track:Track) RETURN album.name as album, count(track) as tracks ORDER BY album.name",
        "recent": "MATCH (al:Album) WHERE al.release_date IS NOT NULL RETURN al.name as album, al.release_date as date ORDER BY al.release_date DESC LIMIT 15"
    }
    
    if len(sys.argv) == 1:
        # No arguments - show menu
        print("🎵 Music Besties - AuraDB Query Tool")
        print("=" * 50)
        print("Usage:")
        print("  python query_auradb.py [preset_name]")
        print("  python query_auradb.py 'CUSTOM CYPHER QUERY'")
        print()
        print("Available presets:")
        for name, query in preset_queries.items():
            print(f"  {name:10} - {query[:60]}...")
        print()
        print("Examples:")
        print("  python query_auradb.py artists")
        print("  python query_auradb.py taylor")
        print("  python query_auradb.py \"MATCH (a:Artist) RETURN count(a)\"")
        return
    
    query_input = sys.argv[1]
    
    # Check if it's a preset
    if query_input in preset_queries:
        query = preset_queries[query_input]
        print(f"🔍 Running preset '{query_input}': {query}")
    else:
        query = query_input
        print(f"🔍 Running custom query: {query}")
    
    print()
    
    # Run the query
    results = run_query(query)
    
    if results is not None:
        print_results(results)
    
if __name__ == "__main__":
    main() 