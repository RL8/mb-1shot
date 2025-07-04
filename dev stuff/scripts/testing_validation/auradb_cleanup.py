#!/usr/bin/env python3
"""
AuraDB Cleanup Script
Completely clears all data from the Neo4j AuraDB instance
Use before running the enhanced Spotify knowledge graph builder
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

class AuraDBCleaner:
    def __init__(self):
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_user = os.getenv('NEO4J_USER')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        
        if not all([self.neo4j_uri, self.neo4j_user, self.neo4j_password]):
            raise ValueError("Missing Neo4j credentials in .env file")
        
        self.driver = None
        self._connect()
    
    def _connect(self):
        """Connect to Neo4j AuraDB"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            print("✅ Connected to Neo4j AuraDB")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            raise e
    
    def get_database_stats(self):
        """Get current database statistics"""
        with self.driver.session() as session:
            try:
                # Count nodes by type
                node_counts = {}
                
                # Get all node labels
                labels_result = session.run("CALL db.labels()")
                labels = [record["label"] for record in labels_result]
                
                total_nodes = 0
                for label in labels:
                    count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                    count = count_result.single()["count"]
                    node_counts[label] = count
                    total_nodes += count
                
                # Count relationships
                rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                total_relationships = rel_result.single()["count"]
                
                return {
                    'total_nodes': total_nodes,
                    'total_relationships': total_relationships,
                    'node_types': node_counts
                }
                
            except Exception as e:
                print(f"❌ Error getting database stats: {e}")
                return None
    
    def clean_database(self):
        """Completely clean the database"""
        print("🧹 Starting database cleanup...")
        
        # Get initial stats
        initial_stats = self.get_database_stats()
        if initial_stats:
            print(f"📊 Current database contains:")
            print(f"   📋 Total nodes: {initial_stats['total_nodes']}")
            print(f"   🔗 Total relationships: {initial_stats['total_relationships']}")
            if initial_stats['node_types']:
                print(f"   📊 Node types:")
                for node_type, count in initial_stats['node_types'].items():
                    print(f"      - {node_type}: {count}")
        
        with self.driver.session() as session:
            try:
                print("\n🗑️  Deleting all relationships...")
                # Delete all relationships first
                rel_result = session.run("MATCH ()-[r]->() DELETE r RETURN count(r) as deleted")
                deleted_rels = rel_result.single()["deleted"]
                print(f"✅ Deleted {deleted_rels} relationships")
                
                print("\n🗑️  Deleting all nodes...")
                # Delete all nodes
                node_result = session.run("MATCH (n) DELETE n RETURN count(n) as deleted")
                deleted_nodes = node_result.single()["deleted"]
                print(f"✅ Deleted {deleted_nodes} nodes")
                
                print("\n🗑️  Removing constraints and indexes...")
                # Drop all constraints
                try:
                    constraints_result = session.run("CALL db.constraints()")
                    constraints = [record["name"] for record in constraints_result]
                    
                    for constraint in constraints:
                        try:
                            session.run(f"DROP CONSTRAINT {constraint}")
                            print(f"✅ Dropped constraint: {constraint}")
                        except Exception as e:
                            print(f"⚠️  Could not drop constraint {constraint}: {e}")
                except Exception as e:
                    print(f"⚠️  Error listing constraints: {e}")
                
                # Drop all indexes
                try:
                    indexes_result = session.run("CALL db.indexes()")
                    indexes = [record["name"] for record in indexes_result if record["name"]]
                    
                    for index in indexes:
                        try:
                            session.run(f"DROP INDEX {index}")
                            print(f"✅ Dropped index: {index}")
                        except Exception as e:
                            print(f"⚠️  Could not drop index {index}: {e}")
                except Exception as e:
                    print(f"⚠️  Error listing indexes: {e}")
                
            except Exception as e:
                print(f"❌ Error during cleanup: {e}")
                raise e
    
    def verify_cleanup(self):
        """Verify the database is completely clean"""
        print("\n🔍 Verifying cleanup...")
        
        final_stats = self.get_database_stats()
        if final_stats:
            if final_stats['total_nodes'] == 0 and final_stats['total_relationships'] == 0:
                print("✅ Database is completely clean!")
                print("🎯 Ready for enhanced Spotify knowledge graph builder")
                return True
            else:
                print(f"⚠️  Cleanup incomplete:")
                print(f"   📋 Remaining nodes: {final_stats['total_nodes']}")
                print(f"   🔗 Remaining relationships: {final_stats['total_relationships']}")
                return False
        return False
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            print("✅ Database connection closed")

def main():
    """Main cleanup function"""
    print("🧹 AuraDB Cleanup Script")
    print("=" * 50)
    print("⚠️  This will DELETE ALL DATA in your Neo4j database!")
    print("🎯 Use this before running the enhanced Spotify script")
    print("=" * 50)
    
    # Confirmation prompt
    confirmation = input("\n🔴 Are you sure you want to delete ALL data? (type 'YES' to confirm): ")
    
    if confirmation != 'YES':
        print("❌ Cleanup cancelled")
        return
    
    try:
        cleaner = AuraDBCleaner()
        
        # Perform cleanup
        cleaner.clean_database()
        
        # Verify cleanup
        success = cleaner.verify_cleanup()
        
        if success:
            print("\n" + "=" * 50)
            print("🎉 CLEANUP COMPLETE!")
            print("=" * 50)
            print("✅ Database is now empty and ready")
            print("🚀 You can now run the enhanced Spotify script:")
            print("   cd scripts/spotify_knowledge_graph/spotify_knowledge_builder/")
            print("   python spotify_knowledge_builder.py")
        else:
            print("\n❌ Cleanup may not be complete. Please check manually.")
        
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        print("💡 Please check your .env file and try again")
    
    finally:
        if 'cleaner' in locals():
            cleaner.close()

if __name__ == "__main__":
    main() 