# 🎵 AuraDB CLI Query Guide - Music Besties

## 🚀 Available CLI Tools for AuraDB

### 1. **Cypher Shell** ⭐ (Primary CLI Tool)
The official Neo4j command-line interface for running Cypher queries.

#### Installation Options:
```bash
# Option A: Download from GitHub (Recommended)
curl -L https://github.com/neo4j/cypher-shell/releases/latest/download/cypher-shell.zip -o cypher-shell.zip
# Extract and add to PATH

# Option B: Via Neo4j Installation
# Download from https://neo4j.com/deployment-center/

# Option C: Docker (Quick start)
docker run --rm -it neo4j/cypher-shell -a neo4j+s://your-instance.databases.neo4j.io -u neo4j -p your-password
```

#### Connection Command:
```bash
cypher-shell -a neo4j+s://8644c19e.databases.neo4j.io -u neo4j -p "y8sglVkq2XclwYWM6-2R0fzQdtbzQjksq7RbSuNfuzs"
```

### 2. **Aura CLI** (Instance Management)
Official CLI for managing AuraDB instances (not for querying data).

```bash
# Installation
curl -L https://github.com/neo4j/aura-cli/releases/latest/download/aura-cli-windows.zip -o aura-cli.zip

# Commands
aura-cli instances list
aura-cli instances pause <instance-id>
aura-cli instances resume <instance-id>
```

### 3. **Python Neo4j Driver** (Your Current Setup) ✅
You already have this working! Perfect for scripting and automation.

### 4. **HTTP API** (curl/wget commands)
Direct REST API access to your AuraDB instance.

---

## 🎼 Essential Cypher Queries for Music Besties

### **Basic Data Exploration**
```cypher
// Count all nodes
MATCH (n) RETURN count(n) as total_nodes;

// List all artists
MATCH (a:Artist) RETURN a.name ORDER BY a.name;

// Get node types and counts
MATCH (n) RETURN distinct labels(n) as labels, count(n) as count ORDER BY count DESC;

// Sample relationships
MATCH ()-[r]->() RETURN type(r) as relationship, count(r) as count ORDER BY count DESC LIMIT 10;
```

### **Artist Deep Dives**
```cypher
// Taylor Swift complete discography
MATCH (taylor:Artist {name: "Taylor Swift"})-[:HAS_ALBUM]->(album:Album)
OPTIONAL MATCH (album)-[:HAS_TRACK]->(track:Track)
RETURN album.name as album, count(track) as track_count
ORDER BY album.name;

// Find tracks by any artist
MATCH (artist:Artist {name: "Billie Eilish"})-[:HAS_ALBUM]->(album)-[:HAS_TRACK]->(track)
RETURN track.name as track, album.name as album
LIMIT 20;

// Artist with most albums
MATCH (a:Artist)-[:HAS_ALBUM]->(al:Album)
RETURN a.name as artist, count(al) as album_count
ORDER BY album_count DESC;
```

### **Advanced Graph Queries**
```cypher
// Find similar artists (artists who appear together in search results)
MATCH (a1:Artist)-[:HAS_ALBUM]->(album1:Album),
      (a2:Artist)-[:HAS_ALBUM]->(album2:Album)
WHERE a1 <> a2 AND album1.name CONTAINS album2.name
RETURN a1.name, a2.name, count(*) as connections
ORDER BY connections DESC;

// Track length analysis
MATCH (track:Track)
WHERE track.duration_ms IS NOT NULL
RETURN avg(track.duration_ms)/1000/60 as avg_minutes,
       min(track.duration_ms)/1000/60 as shortest_minutes,
       max(track.duration_ms)/1000/60 as longest_minutes;

// Albums by year (if release dates exist)
MATCH (album:Album)
WHERE album.release_date IS NOT NULL
RETURN substring(album.release_date, 0, 4) as year, count(album) as albums
ORDER BY year DESC;
```

### **Data Quality Checks**
```cypher
// Find albums without tracks
MATCH (album:Album)
WHERE NOT (album)-[:HAS_TRACK]->()
RETURN album.name as empty_album;

// Find artists without albums
MATCH (artist:Artist)
WHERE NOT (artist)-[:HAS_ALBUM]->()
RETURN artist.name as no_albums;

// Check for duplicate artists
MATCH (a:Artist)
WITH a.name as name, count(a) as count
WHERE count > 1
RETURN name, count;
```

---

## 🔧 Cypher Shell Commands

Once connected to cypher-shell, these commands are available:

### **Session Management**
```
:help                    # Show all commands
:exit                    # Exit shell
:connect                 # Reconnect to database
:disconnect              # Disconnect from database
```

### **Transaction Control**
```
:begin                   # Start transaction
:commit                  # Commit transaction
:rollback                # Rollback transaction
```

### **Parameters & Variables**
```
:param {artist: 'Taylor Swift'}          # Set parameter
:param                                   # Show current parameters
:param clear                            # Clear all parameters

# Use parameter in query
MATCH (a:Artist {name: $artist}) RETURN a;
```

### **File Operations**
```
:source /path/to/script.cypher          # Execute file
```

### **Database Commands**
```
:use neo4j                              # Switch database (if multiple)
:access-mode read                       # Set to read-only
:access-mode write                      # Set to read-write
```

---

## 🐍 Python Script Commands (Your Current Setup)

You already have these working! Here are some useful extensions:

```python
# Save this as query_auradb.py
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv('.env.development')

def run_query(query, params=None):
    """Run any Cypher query against AuraDB"""
    driver = GraphDatabase.driver(
        os.getenv('AURA_DB_URI'),
        auth=(os.getenv('AURA_DB_USERNAME'), os.getenv('AURA_DB_PASSWORD'))
    )
    
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]
    
    driver.close()

# Usage examples:
# python -c "from query_auradb import run_query; print(run_query('MATCH (a:Artist) RETURN a.name LIMIT 5'))"
```

---

## 🌐 HTTP API Commands (Alternative)

Using curl to query via HTTP API:

```bash
# Set credentials
export NEO4J_URI="neo4j+s://8644c19e.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="y8sglVkq2XclwYWM6-2R0fzQdtbzQjksq7RbSuNfuzs"

# Query via HTTP
curl -X POST \
  https://8644c19e.databases.neo4j.io:7473/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n $NEO4J_USER:$NEO4J_PASSWORD | base64)" \
  -d '{
    "statements": [
      {
        "statement": "MATCH (a:Artist) RETURN a.name LIMIT 5"
      }
    ]
  }'
```

---

## 🚀 Quick Start Commands

### **Check What's in Your Database (Copy & Paste Ready)**

```bash
# 1. Connect with Python (you already have this working)
python -c "
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv('.env.development')
driver = GraphDatabase.driver(os.getenv('AURA_DB_URI'), auth=(os.getenv('AURA_DB_USERNAME'), os.getenv('AURA_DB_PASSWORD')))
with driver.session() as session:
    result = session.run('MATCH (a:Artist) RETURN a.name ORDER BY a.name')
    for record in result:
        print(f'• {record[\"a.name\"]}')
driver.close()
"

# 2. If you install cypher-shell
cypher-shell -a neo4j+s://8644c19e.databases.neo4j.io -u neo4j -p "y8sglVkq2XclwYWM6-2R0fzQdtbzQjksq7RbSuNfuzs" "MATCH (a:Artist) RETURN a.name ORDER BY a.name;"
```

---

## 🎯 **Recommendation: Stick with Python for Now**

Given that:
✅ You already have Python + Neo4j driver working
✅ Your credentials are configured  
✅ You can create custom scripts easily

**For your Music Besties project, Python scripts are perfect for:**
- Data exploration and validation
- Automated data quality checks  
- Custom queries for your AI system
- ETL operations

**Install cypher-shell only if you need:**
- Interactive command-line querying
- Quick ad-hoc data exploration
- Shell scripting integration

---

## 📝 **Next Steps**

1. **Keep using your Python setup** - it's working great!
2. **Try the example queries above** in your Python scripts
3. **Consider installing cypher-shell** for quick interactive queries
4. **Use the Aura Console** (browser) for visual exploration

Your AuraDB is rich with music data and ready for your Music Besties AI! 🎵✨ 

# AuraDB CLI Access Guide

## Quick Start
Use the custom Python CLI tool for immediate data querying:
```bash
python query_auradb.py
```

## Available Query Options

### Built-in Presets
1. **artists** - List all artists with popularity scores
2. **albums** - Show albums with release dates  
3. **stats** - Database statistics (nodes, relationships, etc.)
4. **taylor** - Taylor Swift discography deep-dive
5. **recent** - Recent releases (2020+)
6. **popular** - Most popular tracks
7. **custom** - Run your own Cypher query

### Custom Query Examples
```bash
# Run specific queries
python query_auradb.py --query "MATCH (a:Artist) RETURN a.name LIMIT 5"

# Get database schema
python query_auradb.py --preset schema
```

## Alternative CLI Tools

### 1. Python Neo4j Driver ✅ (WORKING)
**Status**: Fully functional with your AuraDB instance
- **Tool**: `query_auradb.py` (custom built)
- **Features**: Preset queries, custom Cypher, connection validation
- **Usage**: `python query_auradb.py`

### 2. Cypher Shell ⚠️ (Java Required)
**Status**: Downloaded but requires Java installation
- **Location**: Available in project root
- **Requirement**: Java 11+ needed
- **Usage**: `./cypher-shell -a neo4j+s://your-instance.databases.neo4j.io`

### 3. HTTP API ✅ (Alternative)
**Status**: Available as backup option
- **Endpoint**: `https://your-instance.databases.neo4j.io/db/neo4j/query/v2/cypher`
- **Auth**: Basic authentication with your credentials

## Connection Details
- **URI**: `neo4j+s://8644c19e.databases.neo4j.io`  
- **Username**: `neo4j`
- **Credentials**: Stored in `.env.development`

## Current Database Content
- **Total Nodes**: 1,044 (832 Tracks + 191 Albums + 21 Artists)
- **Relationships**: 1,045
- **Artists**: 21 major artists including Taylor Swift, Billie Eilish, The Weeknd
- **Data Freshness**: Includes 2025 releases (very current)

## Troubleshooting
- **Connection Issues**: Run `python test_auradb_connections.py`
- **Validation**: Run `python validate_auradb_setup.py`
- **Performance**: Use read transactions for better performance

## Audit Trails & Data Tracking

### ⚠️ Important Limitations
**AuraDB does not provide built-in automated audit trails** for tracking individual data modifications (CREATE, UPDATE, DELETE operations). Standard AuraDB plans don't include:
- Automatic logging of when specific nodes/relationships were created
- Built-in change tracking for data modifications  
- Timestamped audit trails of data operations

### 📊 Available Logging Features

#### 1. Query Logs
- **Access**: Via Aura Console → Logs tab
- **Content**: All executed queries with timestamps
- **Retention**: Up to 30 days
- **Limitation**: Queries under 50ms not logged
- **Use Case**: See WHEN queries ran, WHO ran them

#### 2. Security Logs  
- **Content**: Login attempts, authorization failures, admin commands
- **Retention**: Up to 30 days
- **Use Case**: User access and security events

#### 3. Transaction Logs
- **Configuration**: Already enabled in your project
- **Setting**: `db.logs.query.transaction.enabled=VERBOSE` 
- **Content**: Transaction start/end times, transaction IDs

### 🛠️ Custom Audit Trail Solutions

#### Option 1: Application-Level Timestamps
Add timestamp properties to your nodes when creating/updating:

```cypher
// When creating nodes
CREATE (a:Artist {
  name: "New Artist",
  created_at: datetime(),
  updated_at: datetime()
})

// When updating nodes  
MATCH (a:Artist {name: "Existing Artist"})
SET a.property = "new_value", 
    a.updated_at = datetime()
```

#### Option 2: Change Log Nodes
Create audit trail nodes for significant changes:

```cypher
// Create audit log for data changes
MATCH (a:Artist {name: "Taylor Swift"})
CREATE (log:AuditLog {
  action: "UPDATE",
  entity_type: "Artist", 
  entity_id: a.spotify_id,
  changes: "Updated popularity score",
  timestamp: datetime(),
  user: "system"
})
CREATE (log)-[:AUDITED]->(a)
```

#### Option 3: Query Log Analysis
Use your existing query logs to track data operations:

```bash
# Download query logs from Aura Console
# Search for CREATE, MERGE, DELETE, SET operations
# Correlate with timestamps to track changes
```

### 📈 Monitoring Data Changes

#### Current Setup Analysis
Your database already includes some timestamp tracking:
- **updated_at** fields in Spotify data
- **Transaction logging** enabled
- **Query logging** configured

#### Recommended Implementation
1. **Add timestamps** to all future data operations
2. **Use query logs** to track when bulk operations occurred  
3. **Create audit nodes** for critical business data changes
4. **Monitor via dashboards** in Aura Console

### 🔍 Investigating Historical Changes

#### Query Log Analysis
```bash
# Download logs from Aura Console for specific time periods
# Search for patterns like:
grep "CREATE\|MERGE\|DELETE\|SET" query_log.json
```

#### Database Introspection  
```cypher
// Find nodes with timestamp properties
MATCH (n) 
WHERE exists(n.updated_at) OR exists(n.created_at)
RETURN labels(n), count(n)

// Check when Spotify data was last updated
MATCH (a:Artist)
WHERE exists(a.updated_at) 
RETURN a.name, a.updated_at
ORDER BY a.updated_at DESC LIMIT 10
```

### 💡 Best Practices Moving Forward

1. **Implement timestamps** on all new data operations
2. **Use query logs** for forensic analysis of data changes
3. **Create audit procedures** for critical data modifications
4. **Monitor via Aura Console** for real-time insights
5. **Consider upgrading** to higher Aura tiers for enhanced logging

### 📞 Enterprise Options
For comprehensive audit trails, consider:
- **AuraDB Enterprise**: Enhanced logging capabilities
- **Custom solutions**: Application-level audit frameworks
- **Third-party tools**: Specialized database audit solutions 