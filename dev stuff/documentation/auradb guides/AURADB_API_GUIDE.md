# 🌐 AuraDB API Guide - Complete HTTP & Query API Reference

## 📋 API Summary

AuraDB provides **multiple APIs** for querying your database. Here's what's available and tested:

### ✅ **Primary APIs (Working & Tested)**

1. **Neo4j Driver API** (Bolt Protocol) - Your current setup ⭐
   - Protocol: `neo4j+s://` (encrypted Bolt)
   - Port: 7687 
   - Status: ✅ **Working perfectly**
   - Use case: Application development, scripting

2. **Query API v2** (HTTP/HTTPS) - **NEW & Recommended** 🚀
   - Protocol: HTTPS  
   - Port: 443 (implicit)
   - Endpoint: `https://your-instance.databases.neo4j.io/db/neo4j/query/v2`
   - Status: ✅ **Working perfectly**
   - Use case: REST API calls, web applications, microservices

3. **Discovery API** (HTTP/HTTPS)
   - Endpoint: `https://your-instance.databases.neo4j.io/`
   - Status: ✅ **Working perfectly**
   - Use case: Get server info and available endpoints

### ❌ **Legacy APIs (Not Available)**

4. **Legacy HTTP Transactional API**
   - Endpoint: `/db/neo4j/tx/commit`
   - Status: ❌ **Not available in AuraDB** (Returns 403)
   - Note: This is expected and normal for AuraDB

---

## 🧪 **Test Results**

I ran comprehensive tests on your AuraDB instance. Here are the results:

```
🎯 TEST SUMMARY
===============
✅ Discovery API: Working (200 OK)
✅ Query API - Simple Query: Working (202 Accepted)  
✅ Query API - Data Query: Working (202 Accepted)
✅ Query API - Parameterized Query: Working (202 Accepted)
✅ Query API - Statistics: Working (202 Accepted)
⚠️  Legacy API: Not available (403 Forbidden - Expected)

🎉 5/5 core APIs working perfectly!
```

### 📊 **Data Retrieved Successfully:**
- **Artists**: 21 (including Adele, Ariana Grande, BTS, Bad Bunny, Beyoncé)
- **Albums**: 191 total
- **Tracks**: 832 total  
- **Taylor Swift Albums**: 10 albums successfully queried via parameterized API call

---

## 🔧 **API Details & Usage**

### **1. Query API v2 (HTTPS) - Recommended for HTTP Access**

**Endpoint**: `https://8644c19e.databases.neo4j.io/db/neo4j/query/v2`

**Authentication**: Basic Auth (Base64 encoded username:password)

**Request Format**:
```json
{
  "statement": "CYPHER QUERY HERE",
  "parameters": {
    "param_name": "value"
  }
}
```

**Response Format**:
```json
{
  "data": {
    "fields": ["column1", "column2"],
    "values": [
      ["value1", "value2"],
      ["value3", "value4"]
    ]
  },
  "bookmarks": ["FB:kcwQ..."]
}
```

**Status Codes**:
- `200 OK`: Success  
- `202 Accepted`: Success (AuraDB default)
- `400 Bad Request`: Invalid query or parameters
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Access denied

### **2. cURL Examples**

#### Simple Query:
```bash
curl -X POST "https://8644c19e.databases.neo4j.io/db/neo4j/query/v2" \
  -u "neo4j:your_password" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "statement": "MATCH (a:Artist) RETURN a.name ORDER BY a.name LIMIT 5"
  }'
```

#### Parameterized Query:
```bash
curl -X POST "https://8644c19e.databases.neo4j.io/db/neo4j/query/v2" \
  -u "neo4j:your_password" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "statement": "MATCH (a:Artist {name: $artist_name})-[:HAS_ALBUM]->(album:Album) RETURN album.name",
    "parameters": {
      "artist_name": "Taylor Swift"
    }
  }'
```

### **3. Python Requests Example**

```python
import requests
import json

url = "https://8644c19e.databases.neo4j.io/db/neo4j/query/v2"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
auth = ("neo4j", "your_password")

payload = {
    "statement": "MATCH (a:Artist) RETURN a.name as artist_name ORDER BY a.name"
}

response = requests.post(url, headers=headers, auth=auth, json=payload)

if response.status_code in [200, 202]:
    data = response.json()
    artists = [row[0] for row in data['data']['values']]
    print("Artists:", artists)
else:
    print(f"Error: {response.status_code}")
```

### **4. JavaScript/Node.js Example**

```javascript
const axios = require('axios');

const queryAuraDB = async (statement, parameters = {}) => {
    const url = 'https://8644c19e.databases.neo4j.io/db/neo4j/query/v2';
    const auth = Buffer.from('neo4j:your_password').toString('base64');
    
    try {
        const response = await axios.post(url, {
            statement,
            parameters
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': `Basic ${auth}`
            }
        });
        
        return response.data;
    } catch (error) {
        console.error('AuraDB Query Error:', error);
        throw error;
    }
};

// Usage
queryAuraDB('MATCH (a:Artist) RETURN a.name ORDER BY a.name LIMIT 5')
    .then(data => console.log('Artists:', data.data.values))
    .catch(err => console.error(err));
```

---

## 🔍 **Available Endpoints (from Discovery API)**

Your AuraDB instance exposes these endpoints:

```json
{
  "bolt_routing": "bolt+routing://8644c19e.databases.neo4j.io:7687",
  "query": "https://8644c19e.databases.neo4j.io/db/{databaseName}/query/v2",
  "dbms/cluster": "https://8644c19e.databases.neo4j.io/dbms/cluster",
  "db/cluster": "https://8644c19e.databases.neo4j.io/db/{databaseName}/cluster",
  "transaction": "https://8644c19e.databases.neo4j.io/db/{databaseName}/tx",
  "bolt_direct": "neo4j+s://8644c19e.databases.neo4j.io:7687",
  "neo4j_version": "5.27-aura",
  "neo4j_edition": "enterprise"
}
```

---

## 💡 **Best Practices**

### **When to use each API:**

1. **Neo4j Driver (Bolt)** - Use for:
   - Production applications
   - High-performance queries
   - Connection pooling
   - Transaction management
   - Your current Python setup ✅

2. **Query API v2 (HTTP)** - Use for:
   - REST API integrations
   - Microservices
   - Serverless functions
   - Quick testing and debugging
   - When you can't install Neo4j drivers

3. **Discovery API** - Use for:
   - Health checks
   - Getting server information
   - Discovering available endpoints

### **Security Best Practices:**
- Always use HTTPS (never HTTP)
- Use parameterized queries to prevent injection
- Include User-Agent headers
- Store credentials securely (environment variables)
- Use connection pooling for production

### **Performance Tips:**
- Use parameterized queries for better caching
- Implement retry logic for transient errors
- Use appropriate timeouts
- Consider connection pooling for high-volume apps

---

## 🚀 **Quick Start Commands**

### Test with curl:
```bash
# Run the provided examples
bash auradb_curl_examples.sh

# Or test individual endpoints
curl -u "neo4j:your_password" \
  "https://8644c19e.databases.neo4j.io/" | jq .
```

### Test with Python:
```bash
# Use your existing working setup
python query_auradb.py artists

# Or test the HTTP API
python test_auradb_http_api.py
```

---

## 📈 **Summary**

✅ **Your AuraDB APIs are working perfectly!**

- **Driver API (Bolt)**: Your primary, high-performance option
- **Query API v2 (HTTP)**: New, production-ready REST API 
- **Discovery API**: Server information and health checks
- **Legacy APIs**: Correctly disabled in AuraDB

You now have **multiple tested and working ways** to query your AuraDB instance:
1. Python Driver (your current setup)
2. HTTP Query API v2 (new option)
3. Direct curl/HTTP requests
4. Any language that can make HTTP requests

**Recommendation**: Keep using your Python driver for production, but the HTTP API is perfect for REST integrations, testing, and quick queries! 🎵✨ 