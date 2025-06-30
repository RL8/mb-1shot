#!/usr/bin/env python3
"""
AuraDB HTTP API Endpoint Tester
Tests all available HTTP API endpoints for AuraDB

Based on the new Query API that's now GA (General Availability) for AuraDB
"""

import os
import json
import requests
import base64
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.development')

class AuraDBHTTPAPITester:
    def __init__(self):
        self.uri = os.getenv('AURA_DB_URI')
        self.username = os.getenv('AURA_DB_USERNAME')
        self.password = os.getenv('AURA_DB_PASSWORD')
        
        # Extract hostname from bolt URI for HTTP API
        if self.uri and self.uri.startswith('neo4j+s://'):
            parsed = urlparse(self.uri)
            self.hostname = parsed.hostname
            self.http_base = f"https://{self.hostname}"
        else:
            print("❌ Invalid AuraDB URI format")
            self.hostname = None
            self.http_base = None
        
        # Prepare authentication
        if self.username and self.password:
            self.auth_string = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        else:
            self.auth_string = None
    
    def print_config(self):
        """Print configuration information"""
        print("🔧 AuraDB HTTP API Configuration")
        print("=" * 50)
        print(f"Bolt URI: {self.uri}")
        print(f"HTTP Base: {self.http_base}")
        print(f"Username: {self.username}")
        print(f"Password: {'*' * len(self.password) if self.password else 'NOT SET'}")
        print(f"Auth: {'✓ Ready' if self.auth_string else '✗ Missing'}")
        print()
    
    def test_discovery_api(self):
        """Test the Discovery API - Get available endpoints"""
        print("🔍 Test 1: Discovery API")
        print("-" * 30)
        
        try:
            # Test unauthenticated discovery endpoint
            url = f"{self.http_base}/"
            headers = {
                "Accept": "application/json",
                "User-Agent": "AuraDB-HTTP-API-Tester/1.0"
            }
            
            print(f"GET {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Discovery API working!")
                print(f"Neo4j Version: {data.get('neo4j_version', 'Unknown')}")
                print(f"Neo4j Edition: {data.get('neo4j_edition', 'Unknown')}")
                print("Available endpoints:")
                for key, value in data.items():
                    if key not in ['neo4j_version', 'neo4j_edition', 'auth_config']:
                        print(f"  {key}: {value}")
                return True
            else:
                print(f"❌ Discovery API failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Discovery API error: {e}")
            return False
    
    def test_query_api_simple(self):
        """Test the new Query API with a simple query"""
        print("\n🔍 Test 2: Query API - Simple Query")
        print("-" * 40)
        
        try:
            # Test new Query API endpoint
            url = f"{self.http_base}/db/neo4j/query/v2"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {self.auth_string}",
                "User-Agent": "AuraDB-HTTP-API-Tester/1.0"
            }
            
            payload = {
                "statement": "RETURN 1 as test_number, 'Hello AuraDB!' as greeting"
            }
            
            print(f"POST {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 202]:
                data = response.json()
                print("✅ Query API working!")
                print(f"Response: {json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Query API failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Query API error: {e}")
            return False
    
    def test_query_api_data(self):
        """Test Query API with actual data query"""
        print("\n🔍 Test 3: Query API - Data Query")
        print("-" * 35)
        
        try:
            url = f"{self.http_base}/db/neo4j/query/v2"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {self.auth_string}",
                "User-Agent": "AuraDB-HTTP-API-Tester/1.0"
            }
            
            payload = {
                "statement": "MATCH (a:Artist) RETURN a.name as artist_name ORDER BY a.name LIMIT 5"
            }
            
            print(f"POST {url}")
            print(f"Query: {payload['statement']}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 202]:
                data = response.json()
                print("✅ Data query successful!")
                
                # Extract artist names from response
                if 'data' in data and 'values' in data['data']:
                    artists = [row[0] for row in data['data']['values']]
                    print(f"Found {len(artists)} artists:")
                    for artist in artists:
                        print(f"  • {artist}")
                else:
                    print("Response structure:", json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ Data query failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Data query error: {e}")
            return False
    
    def test_query_api_parameters(self):
        """Test Query API with parameterized query"""
        print("\n🔍 Test 4: Query API - Parameterized Query")
        print("-" * 45)
        
        try:
            url = f"{self.http_base}/db/neo4j/query/v2"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {self.auth_string}",
                "User-Agent": "AuraDB-HTTP-API-Tester/1.0"
            }
            
            payload = {
                "statement": "MATCH (a:Artist {name: $artist_name})-[:HAS_ALBUM]->(album:Album) RETURN album.name as album_name ORDER BY album.name",
                "parameters": {
                    "artist_name": "Taylor Swift"
                }
            }
            
            print(f"POST {url}")
            print(f"Query: {payload['statement']}")
            print(f"Parameters: {payload['parameters']}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 202]:
                data = response.json()
                print("✅ Parameterized query successful!")
                
                # Extract album names from response
                if 'data' in data and 'values' in data['data']:
                    albums = [row[0] for row in data['data']['values']]
                    print(f"Found {len(albums)} Taylor Swift albums:")
                    for album in albums:
                        print(f"  • {album}")
                else:
                    print("Response structure:", json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ Parameterized query failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Parameterized query error: {e}")
            return False
    
    def test_query_api_statistics(self):
        """Test Query API with database statistics"""
        print("\n🔍 Test 5: Query API - Database Statistics")
        print("-" * 45)
        
        try:
            url = f"{self.http_base}/db/neo4j/query/v2"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {self.auth_string}",
                "User-Agent": "AuraDB-HTTP-API-Tester/1.0"
            }
            
            payload = {
                "statement": "MATCH (n) RETURN distinct labels(n) as node_type, count(n) as count ORDER BY count DESC"
            }
            
            print(f"POST {url}")
            print(f"Query: {payload['statement']}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 202]:
                data = response.json()
                print("✅ Statistics query successful!")
                
                # Extract statistics from response
                if 'data' in data and 'values' in data['data']:
                    print("Database statistics:")
                    total_nodes = 0
                    for row in data['data']['values']:
                        node_type = row[0][0] if row[0] else 'Unknown'
                        count = row[1]
                        total_nodes += count
                        print(f"  {node_type}: {count} nodes")
                    print(f"  Total: {total_nodes} nodes")
                else:
                    print("Response structure:", json.dumps(data, indent=2))
                return True
            else:
                print(f"❌ Statistics query failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Statistics query error: {e}")
            return False
    
    def test_legacy_http_api(self):
        """Test legacy HTTP API endpoint (may not be available in AuraDB)"""
        print("\n🔍 Test 6: Legacy HTTP API (Expected to fail for AuraDB)")
        print("-" * 60)
        
        try:
            # Try legacy transaction endpoint
            url = f"{self.http_base}/db/neo4j/tx/commit"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {self.auth_string}",
                "User-Agent": "AuraDB-HTTP-API-Tester/1.0"
            }
            
            payload = {
                "statements": [
                    {
                        "statement": "RETURN 1"
                    }
                ]
            }
            
            print(f"POST {url}")
            print("Note: This endpoint may not be available in AuraDB")
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code in [200, 202]:
                print("✅ Legacy HTTP API working (unexpected for AuraDB)")
                return True
            else:
                print(f"⚠️  Legacy HTTP API not available (expected for AuraDB): {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Legacy HTTP API error (expected): {e}")
            return False
    
    def run_all_tests(self):
        """Run all HTTP API tests"""
        print("🚀 AuraDB HTTP API Endpoint Testing")
        print("=" * 60)
        
        self.print_config()
        
        if not self.http_base or not self.auth_string:
            print("❌ Missing configuration. Cannot run tests.")
            return False
        
        tests = [
            self.test_discovery_api,
            self.test_query_api_simple,
            self.test_query_api_data,
            self.test_query_api_parameters,
            self.test_query_api_statistics,
            self.test_legacy_http_api
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append(False)
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results[:-1])  # Don't count legacy API test
        total = len(results) - 1
        
        print(f"✅ Passed: {passed}/{total} core tests")
        print(f"{'⚠️' if not results[-1] else '✅'} Legacy API: {'Not available (expected)' if not results[-1] else 'Available'}")
        
        if passed >= 4:  # At least 4 out of 5 core tests should pass
            print("\n🎉 AuraDB HTTP API is working correctly!")
            print("You can use the Query API for HTTP-based queries.")
        else:
            print("\n❌ AuraDB HTTP API has issues.")
            print("Check your credentials and network connectivity.")
        
        return passed >= 4

def main():
    """Main test execution"""
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--help':
        print(__doc__)
        print("\nUsage: python test_auradb_http_api.py")
        print("\nThis script tests AuraDB HTTP API endpoints to verify they're working.")
        return
    
    tester = AuraDBHTTPAPITester()
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 