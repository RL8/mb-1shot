#!/usr/bin/env python3
"""
Pre-Implementation Environment Test
"""

import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print("📁 Loading credentials from .env file")

# Use AURA_DB variables from .env file
NEO4J_URI = os.getenv("AURA_DB_URI")
NEO4J_USERNAME = os.getenv("AURA_DB_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("AURA_DB_PASSWORD")

def check_credentials():
    """Check if we have valid credentials"""
    print("🔍 Checking database credentials...")
    
    if not NEO4J_URI:
        print("❌ AURA_DB_URI not found in .env file")
        return False
    
    if not NEO4J_PASSWORD:
        print("❌ AURA_DB_PASSWORD not found in .env file") 
        return False
    
    print(f"✅ URI: {NEO4J_URI}")
    print(f"✅ Username: {NEO4J_USERNAME}")
    print("✅ Password: [CONFIGURED]")
    return True

def test_connection():
    """Test database connection"""
    print("\n🔗 Testing database connection...")
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' as status")
            status = result.single()["status"]
            print(f"✅ {status}")
            
            # Test APOC
            try:
                session.run("RETURN apoc.version() as version")
                print("✅ APOC library available")
            except:
                print("⚠️  APOC library not available")
            
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        try:
            driver.close()
        except:
            pass

def analyze_data():
    """Quick data analysis"""
    print("\n📊 Analyzing current database state...")
    
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
        with driver.session() as session:
            # Count nodes
            queries = {
                "Songs": "MATCH (s:Song) RETURN count(s) as count",
                "Words": "MATCH (w:Word) RETURN count(w) as count",
                "Lyrics": "MATCH (l:Lyric) RETURN count(l) as count",
                "WordDictionary": "MATCH (wd:WordDictionary) RETURN count(wd) as count"
            }
            
            for node_type, query in queries.items():
                try:
                    result = session.run(query)
                    count = result.single()["count"]
                    print(f"   {node_type}: {count:,}")
                except:
                    print(f"   {node_type}: 0")
            
            # Check Spotify features
            spotify_check = session.run("""
                MATCH (s:Song) 
                WHERE s.energy IS NOT NULL AND s.valence IS NOT NULL
                RETURN count(s) as count
            """)
            spotify_count = spotify_check.single()["count"]
            print(f"   Songs with Spotify features: {spotify_count:,}")
            
            return True
            
    except Exception as e:
        print(f"❌ Data analysis failed: {e}")
        return False
    finally:
        try:
            driver.close()
        except:
            pass

def validate_environment():
    """Complete environment validation"""
    print("🚀 Environment Validation")
    print("=" * 40)
    
    # Check credentials
    if not check_credentials():
        print("\n❌ FAILED: Database credentials not found in .env file")
        return False
    
    # Test connection
    if not test_connection():
        print("\n❌ FAILED: Cannot connect to database")
        return False
    
    # Analyze data
    if not analyze_data():
        print("\n❌ FAILED: Cannot analyze database")
        return False
    
    print("\n✅ Environment validation PASSED!")
    print("Ready to proceed with implementation.")
    return True

if __name__ == "__main__":
    if validate_environment():
        print("\n🎯 Next step: Run the unified implementation")
        sys.exit(0)
    else:
        print("\n❌ Please resolve issues before proceeding")
        sys.exit(1) 