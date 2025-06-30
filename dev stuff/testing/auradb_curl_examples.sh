#!/bin/bash
# AuraDB HTTP API - Curl Examples
# Demonstrates how to query AuraDB using the HTTP Query API

# Configuration - Replace with your actual credentials
AURA_HOST="8644c19e.databases.neo4j.io"
AURA_USERNAME="neo4j"
AURA_PASSWORD="y8sglVkq2XclwYWM6-2R0fzQdtbzQjksq7RbSuNfuzs"

# Base URL for Query API v2
BASE_URL="https://${AURA_HOST}/db/neo4j/query/v2"

echo "🎵 AuraDB HTTP API - Curl Examples"
echo "=================================="
echo "Host: ${AURA_HOST}"
echo "Endpoint: ${BASE_URL}"
echo

# Example 1: Simple Query
echo "📋 Example 1: Simple Hello World Query"
echo "--------------------------------------"
curl -X POST "${BASE_URL}" \
  -u "${AURA_USERNAME}:${AURA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: AuraDB-Curl-Example/1.0" \
  -d '{
    "statement": "RETURN 1 as number, '\''Hello AuraDB!'\'' as greeting"
  }' | jq '.'

echo
echo

# Example 2: Get All Artists
echo "🎤 Example 2: Get All Artists"
echo "-----------------------------"
curl -X POST "${BASE_URL}" \
  -u "${AURA_USERNAME}:${AURA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: AuraDB-Curl-Example/1.0" \
  -d '{
    "statement": "MATCH (a:Artist) RETURN a.name as artist_name ORDER BY a.name"
  }' | jq '.data.values[] | .[0]'

echo
echo

# Example 3: Parameterized Query - Taylor Swift Albums
echo "💿 Example 3: Taylor Swift Albums (Parameterized Query)"
echo "-------------------------------------------------------"
curl -X POST "${BASE_URL}" \
  -u "${AURA_USERNAME}:${AURA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: AuraDB-Curl-Example/1.0" \
  -d '{
    "statement": "MATCH (a:Artist {name: $artist_name})-[:HAS_ALBUM]->(album:Album) RETURN album.name as album_name, album.release_date as release_date ORDER BY album.name",
    "parameters": {
      "artist_name": "Taylor Swift"
    }
  }' | jq '.data.values[] | {album: .[0], year: .[1]}'

echo
echo

# Example 4: Database Statistics
echo "📊 Example 4: Database Statistics"
echo "---------------------------------"
curl -X POST "${BASE_URL}" \
  -u "${AURA_USERNAME}:${AURA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: AuraDB-Curl-Example/1.0" \
  -d '{
    "statement": "MATCH (n) RETURN distinct labels(n)[0] as node_type, count(n) as count ORDER BY count DESC"
  }' | jq '.data.values[] | {type: .[0], count: .[1]}'

echo
echo

# Example 5: Complex Query - Artist with Most Albums
echo "🏆 Example 5: Artist with Most Albums"
echo "-------------------------------------"
curl -X POST "${BASE_URL}" \
  -u "${AURA_USERNAME}:${AURA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: AuraDB-Curl-Example/1.0" \
  -d '{
    "statement": "MATCH (a:Artist)-[:HAS_ALBUM]->(album:Album) WITH a, count(album) as album_count ORDER BY album_count DESC LIMIT 5 RETURN a.name as artist, album_count"
  }' | jq '.data.values[] | {artist: .[0], albums: .[1]}'

echo
echo

# Example 6: Search for Tracks
echo "🎵 Example 6: Search for Tracks with 'Love' in the Title"
echo "--------------------------------------------------------"
curl -X POST "${BASE_URL}" \
  -u "${AURA_USERNAME}:${AURA_PASSWORD}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "User-Agent: AuraDB-Curl-Example/1.0" \
  -d '{
    "statement": "MATCH (t:Track) WHERE t.name CONTAINS $search_term RETURN t.name as track_name LIMIT 10",
    "parameters": {
      "search_term": "Love"
    }
  }' | jq '.data.values[] | .[0]'

echo
echo

echo "✅ All examples completed!"
echo
echo "💡 Tips:"
echo "  • Use jq to parse JSON responses (install with: brew install jq)"
echo "  • Status code 202 means success for AuraDB"
echo "  • Always use HTTPS (port 443 is implicit)"
echo "  • Include User-Agent header for best practices"
echo "  • Use parameterized queries for security and performance" 