#!/usr/bin/env python3
"""
Quick Connection Test for Enhanced Spotify Knowledge Graph Builder
Tests both Spotify API and AuraDB connections before running main script
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent
sys.path.append(str(parent_dir))

from spotify_knowledge_builder import SpotifyKnowledgeGraphBuilder

def test_connections():
    """Test both Spotify and Neo4j connections"""
    print("🧪 Testing Enhanced Spotify Knowledge Graph Builder Connections")
    print("=" * 70)
    
    try:
        # Initialize builder (this tests connections)
        print("🔌 Initializing connections...")
        builder = SpotifyKnowledgeGraphBuilder()
        
        # Test Spotify API with a simple search
        print("🎵 Testing Spotify API...")
        test_artist = builder.get_artist_by_name("Taylor Swift")
        if test_artist:
            print(f"✅ Spotify API working - Found: {test_artist['name']}")
        else:
            print("❌ Spotify API test failed")
            return False
        
        # Test Neo4j with a simple query
        print("🗄️ Testing Neo4j AuraDB...")
        with builder.driver.session() as session:
            result = session.run("RETURN 'Hello AuraDB' as message")
            message = result.single()["message"]
            print(f"✅ Neo4j AuraDB working - Response: {message}")
        
        # Close connections
        builder.close()
        
        print("\n🎉 ALL CONNECTIONS SUCCESSFUL!")
        print("🚀 Enhanced Spotify Knowledge Graph Builder is ready to use")
        print("\nTo run the full build:")
        print("   python spotify_knowledge_builder.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your .env file credentials")
        print("   2. Ensure internet connection is stable")
        print("   3. Verify AuraDB instance is running")
        return False

if __name__ == "__main__":
    test_connections() 