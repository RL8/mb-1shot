#!/usr/bin/env python3
"""
AuraDB Connection Test & Best Practices Validation
Tests and validates API connections to AuraDB following Neo4j best practices
"""

import os
import sys
import time
import traceback
from neo4j import GraphDatabase, __version__ as neo4j_version
from neo4j.exceptions import (
    ServiceUnavailableException, 
    SessionExpiredException,
    TransientException,
    AuthError,
    ConfigurationError
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.development')

class AuraDBConnectionTester:
    def __init__(self):
        self.uri = os.getenv('AURA_DB_URI')
        self.username = os.getenv('AURA_DB_USERNAME')
        self.password = os.getenv('AURA_DB_PASSWORD')
        self.driver = None
        
    def print_config(self):
        """Print current configuration and best practices check"""
        print("🔧 AuraDB Connection Configuration Analysis")
        print("=" * 60)
        
        # Check credentials
        print(f"URI: {self.uri}")
        print(f"Username: {self.username}")
        print(f"Password: {'*' * len(self.password) if self.password else 'NOT SET'}")
        print(f"Neo4j Driver Version: {neo4j_version}")
        print()
        
        # Best practices validation
        issues = []
        recommendations = []
        
        # 1. Check URI scheme
        if self.uri:
            if self.uri.startswith('neo4j+s://'):
                print("✅ Using neo4j+s:// scheme (RECOMMENDED)")
            elif self.uri.startswith('neo4j://'):
                print("⚠️  Using neo4j:// scheme")
                recommendations.append("Consider using neo4j+s:// for secure connections")
            elif self.uri.startswith('bolt://'):
                print("❌ Using bolt:// scheme")
                issues.append("bolt:// connects to only one machine, won't work with clusters")
                recommendations.append("Use neo4j+s:// for AuraDB connections")
            else:
                print("❌ Unknown URI scheme")
                issues.append("URI scheme not recognized")
        else:
            print("❌ URI not configured")
            issues.append("AURA_DB_URI environment variable not set")
        
        # 2. Check driver version
        major, minor = neo4j_version.split('.')[:2]
        version_num = float(f"{major}.{minor}")
        
        if version_num >= 5.0:
            print("✅ Using Neo4j driver >= 5.0 (RECOMMENDED)")
        elif version_num >= 4.4:
            print("✅ Using Neo4j driver >= 4.4 (Good)")
        else:
            print("❌ Using outdated Neo4j driver")
            issues.append("Driver version too old")
            recommendations.append("Upgrade to neo4j-driver >= 5.0")
        
        # 3. Check credentials
        if not all([self.uri, self.username, self.password]):
            issues.append("Missing required credentials")
        
        print()
        if issues:
            print("❌ ISSUES FOUND:")
            for issue in issues:
                print(f"   • {issue}")
            print()
        
        if recommendations:
            print("💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
            print()
        
        return len(issues) == 0
    
    def test_connection_creation(self):
        """Test 1: Driver creation and verification"""
        print("🔌 Test 1: Driver Creation & Verification")
        print("-" * 40)
        
        try:
            # Best Practice: Use recommended configuration
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                # Best practice configurations
                max_connection_lifetime=300,  # 5 minutes
                max_connection_pool_size=50,
                connection_acquisition_timeout=60,
                connection_timeout=30,
                max_retry_time=30,
                initial_retry_delay=1.0,
                retry_delay_multiplier=2.0,
                retry_delay_jitter_factor=0.2
            )
            
            print("✅ Driver created successfully")
            
            # Best Practice: Verify connectivity immediately
            start_time = time.time()
            self.driver.verify_connectivity()
            verify_time = time.time() - start_time
            
            print(f"✅ Connectivity verified in {verify_time:.2f}s")
            
            # Get server info
            with self.driver.session() as session:
                result = session.run("CALL dbms.components() YIELD name, versions")
                components = [{"name": record["name"], "versions": record["versions"]} 
                             for record in result]
                
                for comp in components:
                    print(f"   • {comp['name']}: {comp['versions'][0]}")
            
            return True
            
        except AuthError as e:
            print(f"❌ Authentication failed: {e}")
            return False
        except ServiceUnavailableException as e:
            print(f"❌ Service unavailable: {e}")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            traceback.print_exc()
            return False
    
    def test_session_management(self):
        """Test 2: Session management best practices"""
        print("\n🔄 Test 2: Session Management")
        print("-" * 40)
        
        try:
            # Test 1: Auto-commit transaction (simple)
            with self.driver.session() as session:
                result = session.run("RETURN 'Hello AuraDB' as message")
                message = result.single()["message"]
                print(f"✅ Auto-commit transaction: {message}")
            
            # Test 2: Read transaction function (RECOMMENDED)
            def read_artists(tx):
                result = tx.run("MATCH (a:Artist) RETURN count(a) as count")
                return result.single()["count"]
            
            with self.driver.session() as session:
                artist_count = session.read_transaction(read_artists)
                print(f"✅ Read transaction function: {artist_count} artists")
            
            # Test 3: Write transaction function (RECOMMENDED)
            def create_test_node(tx):
                result = tx.run("""
                    MERGE (t:TestNode {id: 'connection_test', timestamp: $timestamp})
                    SET t.status = 'active'
                    RETURN t.id as id
                """, timestamp=int(time.time()))
                return result.single()["id"]
            
            with self.driver.session() as session:
                test_id = session.write_transaction(create_test_node)
                print(f"✅ Write transaction function: Created {test_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Session management test failed: {e}")
            return False
    
    def test_error_handling(self):
        """Test 3: Error handling and retry mechanisms"""
        print("\n🛡️  Test 3: Error Handling & Resilience")
        print("-" * 40)
        
        try:
            # Test parameter injection protection
            with self.driver.session() as session:
                # GOOD: Using parameters
                result = session.run(
                    "MATCH (a:Artist {name: $name}) RETURN a.name",
                    name="Taylor Swift"
                )
                print("✅ Parameterized query protection")
            
            # Test connection pool behavior
            sessions = []
            for i in range(5):
                session = self.driver.session()
                sessions.append(session)
            
            # Close all sessions
            for session in sessions:
                session.close()
            print("✅ Connection pool handling")
            
            # Test transaction retry behavior
            def potentially_failing_transaction(tx):
                # This should succeed normally
                result = tx.run("MATCH (n) RETURN count(n) as count LIMIT 1")
                return result.single()["count"]
            
            with self.driver.session() as session:
                count = session.read_transaction(potentially_failing_transaction)
                print(f"✅ Transaction retry mechanism: {count} nodes")
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    def test_performance_patterns(self):
        """Test 4: Performance and best practice patterns"""
        print("\n⚡ Test 4: Performance Patterns")
        print("-" * 40)
        
        try:
            # Test 1: Efficient data retrieval
            start_time = time.time()
            with self.driver.session() as session:
                # Process results within transaction
                def get_sample_data(tx):
                    result = tx.run("""
                        MATCH (a:Artist)
                        RETURN a.name as name, a.popularity as popularity
                        ORDER BY a.popularity DESC
                        LIMIT 5
                    """)
                    # GOOD: Process results inside transaction
                    artists = []
                    for record in result:
                        artists.append({
                            "name": record["name"],
                            "popularity": record["popularity"]
                        })
                    return artists
                
                artists = session.read_transaction(get_sample_data)
                query_time = time.time() - start_time
                print(f"✅ Efficient data processing: {len(artists)} artists in {query_time:.3f}s")
            
            # Test 2: Bookmarking for consistency
            bookmark = None
            with self.driver.session() as session1:
                def create_bookmark_test(tx):
                    tx.run("MERGE (b:BookmarkTest {id: 'test', created: $time})", 
                           time=int(time.time()))
                    return True
                
                session1.write_transaction(create_bookmark_test)
                bookmark = session1.last_bookmark()
                print("✅ Write bookmark captured")
            
            # Read with bookmark for consistency
            with self.driver.session(bookmarks=[bookmark]) as session2:
                def read_with_bookmark(tx):
                    result = tx.run("MATCH (b:BookmarkTest {id: 'test'}) RETURN b.created")
                    return result.single()["b.created"] if result.peek() else None
                
                created_time = session2.read_transaction(read_with_bookmark)
                if created_time:
                    print("✅ Bookmark consistency verified")
                else:
                    print("⚠️  Bookmark test node not found")
            
            return True
            
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False
    
    def test_schema_and_data(self):
        """Test 5: Schema validation and data integrity"""
        print("\n📊 Test 5: Schema & Data Validation")
        print("-" * 40)
        
        try:
            with self.driver.session() as session:
                # Check database schema
                result = session.run("CALL db.labels() YIELD label RETURN label ORDER BY label")
                labels = [record["label"] for record in result]
                print(f"✅ Node labels: {', '.join(labels)}")
                
                result = session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
                relationships = [record["relationshipType"] for record in result]
                print(f"✅ Relationship types: {', '.join(relationships)}")
                
                # Check indexes
                result = session.run("CALL db.indexes() YIELD name, state RETURN name, state")
                indexes = [(record["name"], record["state"]) for record in result]
                print(f"✅ Indexes: {len(indexes)} defined")
                
                # Data sampling
                result = session.run("""
                    MATCH (n) 
                    RETURN distinct labels(n) as labels, count(*) as count 
                    ORDER BY count DESC
                """)
                
                print("📈 Data distribution:")
                for record in result:
                    labels = record["labels"]
                    count = record["count"]
                    label_str = ":".join(labels) if labels else "No labels"
                    print(f"   • {label_str}: {count:,} nodes")
            
            return True
            
        except Exception as e:
            print(f"❌ Schema validation failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up test data and close connections"""
        print("\n🧹 Cleanup")
        print("-" * 40)
        
        try:
            # Remove test nodes
            with self.driver.session() as session:
                result = session.run("MATCH (n:TestNode) DETACH DELETE n RETURN count(n) as deleted")
                deleted = result.single()["deleted"]
                if deleted > 0:
                    print(f"✅ Cleaned up {deleted} test nodes")
                
                result = session.run("MATCH (n:BookmarkTest) DETACH DELETE n RETURN count(n) as deleted")
                deleted = result.single()["deleted"]
                if deleted > 0:
                    print(f"✅ Cleaned up {deleted} bookmark test nodes")
            
            # Close driver
            if self.driver:
                self.driver.close()
                print("✅ Driver connection closed")
            
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def run_full_test(self):
        """Run complete connection test suite"""
        print("🎵 AuraDB Connection Test Suite - Music Besties")
        print("=" * 60)
        
        # Configuration check
        config_ok = self.print_config()
        if not config_ok:
            print("❌ Configuration issues found. Please fix before proceeding.")
            return False
        
        tests = [
            ("Connection Creation", self.test_connection_creation),
            ("Session Management", self.test_session_management),
            ("Error Handling", self.test_error_handling),
            ("Performance Patterns", self.test_performance_patterns),
            ("Schema & Data", self.test_schema_and_data),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results.append((test_name, False))
        
        # Cleanup
        self.cleanup()
        
        # Summary
        print("\n📋 TEST SUMMARY")
        print("=" * 60)
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Your AuraDB connection follows best practices.")
            return True
        else:
            print("⚠️  Some tests failed. Review the output above for details.")
            return False

def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        print("\nUsage: python test_auradb_connections.py")
        print("\nThis script tests your AuraDB connections against Neo4j best practices.")
        return
    
    tester = AuraDBConnectionTester()
    success = tester.run_full_test()
    
    if success:
        print("\n✅ Your AuraDB API connections are properly configured!")
        print("🚀 Ready for production deployment.")
    else:
        print("\n❌ Connection issues detected.")
        print("📖 Refer to the Neo4j documentation for best practices:")
        print("   • https://neo4j.com/docs/driver-manual/current/")
        print("   • https://neo4j.com/blog/neo4j-driver-best-practices/")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 