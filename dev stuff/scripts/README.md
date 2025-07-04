# 📁 Scripts Directory - Music Besties Project

## 🎯 **Organized Script Structure**

This directory contains all Python scripts organized by functionality and purpose. Each script has its own folder containing the script file and all associated output files, results, and dependencies.

---

## 📂 **Directory Structure**

### 🎵 **Lyrics Processing**
- **`week2_lyrics_structure_parser/`** - Production-ready lyrics parser
  - Parses Genius API lyrics into structured sections (verse, chorus, bridge, etc.)
  - Stores parsed lyrics sections in AuraDB with relationships
  - Handles international terms (Spanish: Estribillo→Chorus, Verso→Verse)
  - **Status**: ✅ Production-ready, fully tested

- **`genius_structure_analyzer/`** - Genius API analysis tool
  - Analyzes real Genius API lyrics formatting patterns
  - Contains: `genius_structure_test.py` + `genius_structure_analysis.json`
  - **Status**: ✅ Analysis complete, 100% structure detection rate

### 🎤 **Artist Data Collection**
- **`top_100_usa_musicians/`** - US musicians ranking system
  - Fetches top 100 US musicians from Spotify API
  - Contains: Main script + improved version + all JSON/TXT/CSV output files
  - **Status**: ✅ Working, produces comprehensive rankings

### 🔍 **Reddit Community Analysis**
- **`reddit_analysis/`** - Complete Reddit analysis pipeline
  - **`final_reddit_merge/`** - Final consolidation (+ `reddit_results/` folder)
  - **`merge_reddit_results/`** - Batch result merging
  - **`reddit_batch_processor/`** - Rate-limited batch processing
  - **`reddit_top100_scorer/`** - Artist scoring by Reddit activity
  - **`reddit_primary_subreddit_scorer/`** - Primary subreddit identification
  - **`reddit_simplified_finder/`** - Basic subreddit discovery
  - **`reddit_public_api_finder/`** - Public API implementation
  - **`reddit_artist_subreddit_finder/`** - Main discovery engine
  - Contains: `requirements.txt`, `README.md`, `REDDIT_ARTIST_SCORING_METHODOLOGY.md`

### 🎼 **Spotify Knowledge Graph**
- **`spotify_knowledge_graph/`** - Neo4j knowledge graph builders
  - **`spotify_knowledge_builder/`** - Main knowledge graph builder
  - **`test_spotify_api/`** - API connectivity testing
  - **`spotify_knowledge_builder_enhanced/`** - Enhanced version with metadata
  - **`spotify_knowledge_builder_fixed/`** - Bug-fixed version
  - **`music_graph_builder/`** - Generic graph construction framework
  - Contains: `spotify_knowledge_graph_plan.md`

### 🧪 **Testing & Validation**
- **`testing_validation/`** - Database and API validation
  - **`validate_auradb_setup/`** - Comprehensive AuraDB validation
  - **`test_auradb_http_api/`** - HTTP API endpoint testing
  - **`test_auradb_connections/`** - Connection method testing
  - **`query_auradb/`** - Query utility with presets
  - Contains: `requirements.txt`, `auradb_curl_examples.sh`

---

## 🚀 **Quick Start Guide**

### 1. **Week 1-2: Lyrics Collection & Parsing**
```bash
# Navigate to lyrics parser
cd scripts/week2_lyrics_structure_parser/
python week2_lyrics_structure_parser.py --test

# Check Genius API analysis
cd ../genius_structure_analyzer/
python genius_structure_test.py
```

### 2. **Artist Data Collection**
```bash
cd scripts/top_100_usa_musicians/
python top_100_usa_musicians.py
```

### 3. **Reddit Analysis Pipeline**
```bash
cd scripts/reddit_analysis/
pip install -r requirements.txt

# Start with basic discovery
cd reddit_artist_subreddit_finder/
python reddit_artist_subreddit_finder.py

# Process in batches
cd ../reddit_batch_processor/
python reddit_batch_processor.py

# Final consolidation
cd ../final_reddit_merge/
python final_reddit_merge.py
```

### 4. **Spotify Knowledge Graph**
```bash
cd scripts/spotify_knowledge_graph/
cd spotify_knowledge_builder/
python spotify_knowledge_builder.py
```

### 5. **Testing & Validation**
```bash
cd scripts/testing_validation/
pip install -r requirements.txt

# Validate AuraDB setup
cd validate_auradb_setup/
python validate_auradb_setup.py

# Quick database queries
cd ../query_auradb/
python query_auradb.py stats
python query_auradb.py artists
```

---

## 📊 **Development Status**

| Category | Scripts | Status | Production Ready |
|----------|---------|--------|------------------|
| **Lyrics Processing** | 2 | ✅ Complete | 100% |
| **Artist Data** | 2 | ✅ Working | 100% |
| **Reddit Analysis** | 8 | ✅ Complete | 87.5% |
| **Spotify Knowledge** | 5 | ✅ Working | 80% |
| **Testing/Validation** | 4 | ✅ Complete | 100% |
| **TOTAL** | **21** | **✅ Ready** | **91%** |

---

## 🔧 **Dependencies**

### Core Requirements
- Python 3.8+
- Neo4j AuraDB instance
- Spotify Developer Account
- Reddit API credentials
- Genius API token

### Key Libraries
- `neo4j-driver` (5.15.0+)
- `spotipy` (Spotify API)
- `praw` (Reddit API)
- `lyricsgenius` (Genius API)
- `python-dotenv`

---

## 🎯 **Next Steps**

1. **Week 3**: Implement thematic analysis using OpenAI
2. **Week 4**: Build relationship mappings and similarity analysis
3. **Production**: Deploy complete pipeline for 10,000+ songs

---

*Last Updated: July 1, 2025*
*Total Scripts: 21 | Organized: 100% | Production Ready: 91%* 