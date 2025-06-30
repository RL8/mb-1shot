# 🎵 **Spotify-First Knowledge Graph Builder Plan**

## **Strategy Overview**
Use Spotify API as the primary data source for structured, real-time music data, then optionally enrich with Wikipedia for additional context.

## **Advantages of Spotify-First Approach:**
- ✅ **Structured Data**: Consistent JSON responses
- ✅ **Real-time Metrics**: Popularity scores, follower counts
- ✅ **Audio Features**: Tempo, energy, danceability, valence
- ✅ **Reliable API**: No HTML parsing or rate limiting issues
- ✅ **Rich Metadata**: Genres, release dates, duration, explicit flags
- ✅ **Related Artists**: Network connections for graph relationships

---

## **Step-by-Step Process**

### **Phase 1: Artist Discovery & Basic Info** 🎤
For each artist in our list:
1. **Search Artist** → Get Spotify Artist ID
2. **Get Artist Details** → Name, followers, popularity, genres
3. **Get Related Artists** → Build artist relationship network
4. **Store in Neo4j** → Create Artist nodes with properties

### **Phase 2: Discography Collection** 💿
For each artist:
1. **Get All Albums** → Studio albums, singles, compilations
2. **Album Details** → Name, release date, total tracks, genres
3. **Album Tracks** → Get complete tracklist for each album
4. **Store in Neo4j** → Create Album nodes, link to Artists

### **Phase 3: Track Deep Dive** 🎵
For each track:
1. **Track Metadata** → Duration, explicit, popularity, preview URL
2. **Audio Features** → Tempo, key, energy, danceability, valence
3. **Track Analysis** → Loudness, speechiness, acousticness
4. **Store in Neo4j** → Create Song nodes with rich properties

### **Phase 4: Relationship Building** 🕸️
1. **Artist → Album** → `RELEASED` relationships
2. **Album → Track** → `CONTAINS` relationships (with track number)
3. **Artist → Artist** → `RELATED_TO` relationships  
4. **Track → Genre** → `HAS_GENRE` relationships
5. **Track → Features** → `HAS_AUDIO_FEATURES` relationships

### **Phase 5: Data Enrichment** 📊
1. **Popularity Trends** → Track popularity over time
2. **Genre Classification** → Enhanced genre categorization
3. **Collaboration Networks** → Featured artists, collaborations
4. **Market Analysis** → Available markets per track/album

---

## **Data Structure Design**

### **Neo4j Node Types:**
```cypher
// Artist Node
(:Artist {
  spotify_id: "string",
  name: "string", 
  followers: number,
  popularity: number,
  genres: ["array"],
  image_url: "string",
  spotify_url: "string"
})

// Album Node  
(:Album {
  spotify_id: "string",
  name: "string",
  release_date: "date",
  total_tracks: number,
  album_type: "string", // album, single, compilation
  genres: ["array"],
  popularity: number,
  image_url: "string",
  spotify_url: "string"
})

// Song Node
(:Song {
  spotify_id: "string",
  name: "string",
  duration_ms: number,
  explicit: boolean,
  popularity: number,
  track_number: number,
  preview_url: "string",
  spotify_url: "string"
})

// AudioFeatures Node
(:AudioFeatures {
  danceability: float,
  energy: float,
  key: number,
  loudness: float,
  mode: number,
  speechiness: float,
  acousticness: float,
  instrumentalness: float,
  liveness: float,
  valence: float,
  tempo: float,
  time_signature: number
})

// Genre Node
(:Genre {
  name: "string",
  description: "string"
})
```

### **Relationship Types:**
```cypher
(Artist)-[:RELEASED]->(Album)
(Album)-[:CONTAINS {track_number: number}]->(Song)
(Artist)-[:RELATED_TO {strength: float}]->(Artist)
(Song)-[:HAS_GENRE]->(Genre)
(Song)-[:HAS_AUDIO_FEATURES]->(AudioFeatures)
(Artist)-[:HAS_GENRE]->(Genre)
(Song)-[:FEATURED_IN {role: "string"}]->(Album)
```

---

## **Technical Implementation**

### **Script Architecture:**
```
Spotify API → Data Processing → Neo4j Database
     ↓              ↓              ↓
Raw JSON    →  Structured Data → Graph Nodes
```

### **Key Functions Needed:**
1. `get_artist_by_name(name)` → Artist details
2. `get_artist_albums(artist_id)` → All albums
3. `get_album_tracks(album_id)` → Track list
4. `get_audio_features(track_ids)` → Audio analysis
5. `get_related_artists(artist_id)` → Artist network
6. `load_to_neo4j(data)` → Database insertion

### **Rate Limiting Strategy:**
- **Spotify API Limits**: 2000 requests per hour
- **Batch Processing**: Get multiple tracks' audio features in one call
- **Smart Caching**: Store results to avoid duplicate API calls
- **Progress Tracking**: Resume from interruptions

---

## **Implementation Phases**

### **Phase A: MVP (Minimum Viable Product)** - 30 minutes
- Basic artist → album → track data collection
- Simple Neo4j node creation
- Test with 2-3 artists

### **Phase B: Enhanced Data** - 1 hour  
- Audio features integration
- Genre and relationship mapping
- All 20 artists processing

### **Phase C: Advanced Features** - 2 hours
- Related artist networks
- Collaboration detection
- Market availability analysis
- Data validation and cleanup

### **Phase D: Wikipedia Enhancement** - 1 hour
- Identify gaps in Spotify data
- Fetch missing information from Wikipedia
- Merge data sources intelligently

---

## **Expected Output**

### **Knowledge Graph Contents:**
- **20 Artists** with complete profiles
- **~200-300 Albums** across all artists
- **~2000-3000 Songs** with audio features
- **~50-100 Unique Genres** 
- **~400-500 Artist Relationships**
- **Rich Metadata** for all nodes

### **Queryable Insights:**
- "Find all songs with high danceability by Taylor Swift"
- "Show artists related to Ed Sheeran with their connection strength"
- "Get all albums released in 2023 with their popularity scores"
- "Find the most energetic songs across all artists"
- "Show genre distribution across the knowledge graph"

---

## **Comparison: Spotify vs Wikipedia**

| Aspect | Spotify API | Wikipedia |
|--------|-------------|-----------|
| **Data Quality** | ✅ Structured, consistent | ❌ Unstructured, varies |
| **Real-time Data** | ✅ Live popularity scores | ❌ Static historical data |
| **Audio Features** | ✅ Rich audio analysis | ❌ Not available |
| **Reliability** | ✅ Stable API | ❌ Parsing complexity |
| **Coverage** | ❌ Limited to Spotify catalog | ✅ Comprehensive |
| **Historical Context** | ❌ Limited history | ✅ Rich background info |

## **Next Steps**
1. **Implement MVP script** with basic Spotify data collection
2. **Test with 3 artists** to validate approach
3. **Scale to full 20 artists** with enhanced features
4. **Add Wikipedia enrichment** for missing context
5. **Connect to Vue.js frontend** for visualization

---

**Bottom Line**: Spotify-first approach provides structured, reliable data foundation that can be enhanced with Wikipedia context where needed. This is more maintainable and scalable than Wikipedia scraping. 