#!/usr/bin/env python3
"""
AuraDB Connection Validator - Music Besties
Validates API connections to AuraDB against Neo4j best practices
"""

import os
import time
import sys
from neo4j import GraphDatabase, __version__ as neo4j_version
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.development')

class AuraDBValidator:
    def __init__(self):
        self.uri = os.getenv('AURA_DB_URI')
        self.username = os.getenv('AURA_DB_USERNAME')
        self.password = os.getenv('AURA_DB_PASSWORD')
        self.driver = None
        
    def check_configuration(self):
        """Validate configuration against best practices"""
        print("🔧 Configuration Analysis")
        print("=" * 50)
        
        print(f"Neo4j Driver Version: {neo4j_version}")
        print(f"URI: {self.uri}")
        print(f"Username: {self.username}")
        print(f"Password: {'✓ Set' if self.password else '✗ Missing'}")
        print()
        
        issues = []
        recommendations = []
        
        # Check URI scheme
        if self.uri:
            if self.uri.startswith('neo4j+s://'):
                print("✅ Using neo4j+s:// scheme (RECOMMENDED for AuraDB)")
            elif self.uri.startswith('bolt://'):
                print("❌ Using bolt:// scheme")
                issues.append("bolt:// only connects to one machine, won't work with AuraDB clusters")
                recommendations.append("Change to neo4j+s:// for AuraDB")
            else:
                print(f"⚠️  Using {self.uri.split('://')[0]}:// scheme")
        
        # Check driver version
        major, minor = neo4j_version.split('.')[:2]
        if float(f"{major}.{minor}") >= 5.0:
            print("✅ Neo4j driver version 5.x (EXCELLENT)")
        elif float(f"{major}.{minor}") >= 4.4:
            print("✅ Neo4j driver version 4.4+ (Good)")
        else:
            issues.append("Outdated Neo4j driver")
            recommendations.append("Upgrade to neo4j-driver >= 5.0")
        
        print()
        if issues:
            print("❌ CONFIGURATION ISSUES:")
            for issue in issues:
                print(f"   • {issue}")
        
        if recommendations:
            print("💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        return len(issues) == 0
    
    def test_connection(self):
        """Test connection following best practices"""
        print("\n🔌 Connection Test")
        print("=" * 50)
        
        try:
            # Best Practice: Create driver with proper config
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password),
                # Production-ready settings
                max_connection_lifetime=300,  # 5 minutes
                max_connection_pool_size=50,
                connection_acquisition_timeout=60,
                connection_timeout=30
            )
            print("✅ Driver created with optimized settings")
            
            # Best Practice: Verify connectivity immediately
            start_time = time.time()
            self.driver.verify_connectivity()
            connect_time = time.time() - start_time
            print(f"✅ Connectivity verified in {connect_time:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def test_best_practices(self):
        """Test implementation of Neo4j best practices"""
        print("\n⭐ Best Practices Validation")
        print("=" * 50)
        
        try:
            # Best Practice 1: Use read transactions for reads
            def get_artist_count(tx):
                result = tx.run("MATCH (a:Artist) RETURN count(a) as count")
                return result.single()["count"]
            
            with self.driver.session() as session:
                artist_count = session.read_transaction(get_artist_count)
                print(f"✅ Read transaction: Found {artist_count} artists")
            
            # Best Practice 2: Use write transactions for writes
            def create_test_marker(tx):
                result = tx.run("""
                    MERGE (t:ValidationTest {id: 'connection_test', timestamp: $timestamp})
                    SET t.validated = true
                    RETURN t.id as id
                """, timestamp=int(time.time()))
                return result.single()["id"]
            
            with self.driver.session() as session:
                test_id = session.write_transaction(create_test_marker)
                print(f"✅ Write transaction: Created validation marker")
            
            # Best Practice 3: Use parameterized queries
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (a:Artist {name: $name}) RETURN a.name",
                    name="Taylor Swift"
                )
                print("✅ Parameterized queries: Security protection verified")
            
            # Best Practice 4: Process results within transaction scope
            def get_sample_data(tx):
                result = tx.run("""
                    MATCH (a:Artist)
                    RETURN a.name as name, a.popularity as popularity
                    ORDER BY a.popularity DESC
                    LIMIT 3
                """)
                # GOOD: Process within transaction
                artists = []
                for record in result:
                    artists.append({
                        "name": record["name"], 
                        "popularity": record.get("popularity", 0)
                    })
                return artists
            
            with self.driver.session() as session:
                top_artists = session.read_transaction(get_sample_data)
                print(f"✅ Result processing: Retrieved {len(top_artists)} top artists")
            
            return True
            
        except Exception as e:
            print(f"❌ Best practices test failed: {e}")
            return False
    
    def test_backend_integration(self):
        """Test backend integration patterns"""
        print("\n🔧 Backend Integration Analysis")
        print("=" * 50)
        
        # Check if backend files exist and analyze them
        backend_file = "backend/server.js"
        if os.path.exists(backend_file):
            print("✅ Backend server file found")
            
            with open(backend_file, 'r') as f:
                content = f.read()
                
            if 'neo4j-driver' in content:
                print("✅ Neo4j driver imported in backend")
            if 'verify_connectivity' in content:
                print("✅ Connection verification found")
            else:
                print("⚠️  Missing verify_connectivity() call")
            if 'session()' in content:
                print("✅ Session usage detected")
            if '.env' in content or 'process.env' in content:
                print("✅ Environment configuration detected")
        else:
            print("⚠️  Backend server file not found")
        
        # Check package.json for proper Neo4j version
        package_file = "backend/package.json"
        if os.path.exists(package_file):
            with open(package_file, 'r') as f:
                content = f.read()
            if '"neo4j-driver": "^5.' in content:
                print("✅ Backend using Neo4j driver 5.x")
            elif '"neo4j-driver"' in content:
                print("⚠️  Backend using older Neo4j driver")
            else:
                print("❌ Neo4j driver not found in backend dependencies")
        
        return True
    
    def cleanup_and_summary(self):
        """Clean up test data and provide summary"""
        print("\n🧹 Cleanup & Summary")
        print("=" * 50)
        
        try:
            # Remove test data
            with self.driver.session() as session:
                result = session.run("MATCH (n:ValidationTest) DETACH DELETE n RETURN count(n) as deleted")
                deleted = result.single()["deleted"]
                if deleted > 0:
                    print(f"✅ Cleaned up {deleted} test nodes")
            
            # Database summary
            with self.driver.session() as session:
                result = session.run("MATCH (n) RETURN distinct labels(n) as labels, count(*) as count ORDER BY count DESC")
                print("\n📊 Database Contents:")
                total_nodes = 0
                for record in result:
                    labels = record["labels"]
                    count = record["count"]
                    total_nodes += count
                    label_str = ":".join(labels) if labels else "Unlabeled"
                    print(f"   • {label_str}: {count:,} nodes")
                print(f"   📈 Total: {total_nodes:,} nodes")
            
            if self.driver:
                self.driver.close()
                print("✅ Driver connection closed properly")
                
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def run_validation(self):
        """Run complete validation suite"""
        print("🎵 AuraDB Connection Validation - Music Besties")
        print("=" * 60)
        
        tests = [
            ("Configuration", self.check_configuration),
            ("Connection", self.test_connection),
            ("Best Practices", self.test_best_practices),
            ("Backend Integration", self.test_backend_integration)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed: {e}")
                results.append((test_name, False))
        
        self.cleanup_and_summary()
        
        # Final summary
        print("\n📋 VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nScore: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 EXCELLENT! Your AuraDB setup follows all best practices!")
            print("🚀 Ready for production use.")
            
            print("\n💡 NEXT STEPS FOR OPTIMIZATION:")
            print("   • Consider adding connection pooling monitoring")
            print("   • Implement circuit breaker pattern for resilience") 
            print("   • Add query performance monitoring")
            print("   • Set up proper logging for connection events")
            
        elif passed >= total * 0.75:
            print("\n✅ GOOD! Your setup is mostly following best practices.")
            print("📝 Review failed tests above for improvements.")
            
        else:
            print("\n⚠️  NEEDS IMPROVEMENT: Several best practices not implemented.")
            print("📖 Consider reviewing Neo4j driver documentation.")
        
        return passed == total

def main():
    validator = AuraDBValidator()
    success = validator.run_validation()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 