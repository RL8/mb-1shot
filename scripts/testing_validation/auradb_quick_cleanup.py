#!/usr/bin/env python3
"""
AuraDB Quick Cleanup Script (Non-Interactive)
Completely clears all data from the Neo4j AuraDB instance
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables - fixed path
project_root = Path(__file__).parent.parent.parent  # Go up to project root
env_path = project_root / '.env'

print(f"🔍 Looking for .env file at: {env_path}")
print(f"📁 .env file exists: {env_path.exists()}")

load_dotenv(env_path)

def clean_auradb():
    """Clean AuraDB database completely"""
    
    # Get credentials - using correct variable names from .env
    neo4j_uri = os.getenv('AURA_DB_URI')
    neo4j_user = os.getenv('AURA_DB_USERNAME') 
    neo4j_password = os.getenv('AURA_DB_PASSWORD')
    
    print(f"🔑 AURA_DB_URI found: {'Yes' if neo4j_uri else 'No'}")
    print(f"🔑 AURA_DB_USERNAME found: {'Yes' if neo4j_user else 'No'}")
    print(f"🔑 AURA_DB_PASSWORD found: {'Yes' if neo4j_password else 'No'}")
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        print("❌ Missing Neo4j credentials in .env file")
        return False
    
    try:
        # Connect to database
        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        print("✅ Connected to Neo4j AuraDB")
        
        with driver.session() as session:
            # Get initial stats
            try:
                node_result = session.run("MATCH (n) RETURN count(n) as count")
                initial_nodes = node_result.single()["count"]
                
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                initial_rels = rel_result.single()["count"]
                
                print(f"📊 Current database: {initial_nodes} nodes, {initial_rels} relationships")
                
            except Exception as e:
                print(f"⚠️ Could not get initial stats: {e}")
                initial_nodes = "unknown"
                initial_rels = "unknown"
            
            # Delete all relationships
            print("🗑️ Deleting all relationships...")
            try:
                rel_result = session.run("MATCH ()-[r]->() DELETE r")
                print("✅ All relationships deleted")
            except Exception as e:
                print(f"⚠️ Error deleting relationships: {e}")
            
            # Delete all nodes
            print("🗑️ Deleting all nodes...")
            try:
                node_result = session.run("MATCH (n) DELETE n")
                print("✅ All nodes deleted")
            except Exception as e:
                print(f"⚠️ Error deleting nodes: {e}")
            
            # Verify cleanup
            try:
                final_nodes = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                final_rels = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                if final_nodes == 0 and final_rels == 0:
                    print("✅ Database is completely clean!")
                    print("🎯 Ready for enhanced Spotify knowledge graph builder")
                    success = True
                else:
                    print(f"⚠️ Cleanup incomplete: {final_nodes} nodes, {final_rels} relationships remain")
                    success = False
                    
            except Exception as e:
                print(f"⚠️ Could not verify cleanup: {e}")
                success = False
        
        driver.close()
        return success
        
    except Exception as e:
        print(f"❌ Database cleanup failed: {e}")
        return False

if __name__ == "__main__":
    print("🧹 AuraDB Quick Cleanup")
    print("=" * 40)
    
    if clean_auradb():
        print("\n🎉 CLEANUP COMPLETE!")
        print("🚀 You can now run the enhanced Spotify script")
    else:
        print("\n❌ Cleanup failed. Please check your connection and try again.") 