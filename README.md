# 🎵 Music Besties - Taylor Swift Knowledge Graph Chat Application

**Last Updated:** January 27, 2025

A sophisticated Vue.js application that creates an interactive Taylor Swift knowledge graph using Neo4j and provides AI-powered chat functionality. 

**🎯 Single-Artist Focus Strategy**: Rather than attempting to analyze multiple artists superficially, we've chosen to perfect our music analysis technology by deeply understanding Taylor Swift's complete catalog. This approach enables:

- **Deep Lyrical Analysis**: Comprehensive word-level semantic analysis across her entire discography
- **Evolution Tracking**: Musical and lyrical development from debut through current releases  
- **Advanced Taxonomy Development**: Creating sophisticated music categorization systems
- **Proof of Concept**: Perfecting the technology before scaling to additional artists

## 🏗️ Project Architecture

```
mb-1shot/
├── .env                    ← 🎯 SINGLE SOURCE OF TRUTH for ALL configuration
├── src/                    ← Vue.js frontend application  
├── backend/                ← Node.js/Express API server
├── dev stuff/              ← Development tools & scripts
│   ├── data-scripts/       ← Python scripts for data population
│   └── documentation/      ← Project documentation
└── dist/                   ← Built application (generated)
```

## ⚙️ Configuration Management

### 🎯 Single Source of Truth: `.env` File

**IMPORTANT**: All configuration is centralized in the main `.env` file. This approach:

- ✅ Eliminates configuration duplication across files
- ✅ Provides a single place to manage all environment variables  
- ✅ Works seamlessly across frontend, backend, and Python scripts
- ✅ Simplifies deployment and development workflows

### 📁 How Different Parts Read Configuration:

| Component | How it loads `.env` | Notes |
|-----------|-------------------|--------|
| **Frontend (Vue/Vite)** | Automatic via `VITE_` prefix | Only `VITE_*` variables accessible in browser |
| **Backend (Node.js)** | `require('dotenv').config()` | Loads all variables from root `.env` |
| **Python Scripts** | `load_dotenv()` | Use `python-dotenv` package |
| **Vercel Deployment** | Environment variables override | Set in Vercel dashboard |

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ with pip
- Neo4j AuraDB instance
- OpenAI API key
- Spotify Developer account (optional)

### 1. Configuration Setup

1. **Copy and configure the main `.env` file:**
   ```bash
   # The .env file is already created - just update the placeholder values:
   cp .env .env.local  # Optional: create local copy for your credentials
   ```

2. **Update required values in `.env`:**
   ```env
   # Replace these placeholder values with your actual credentials:
   OPENAI_API_KEY=sk-your-actual-openai-key
   AURA_DB_URI=neo4j+s://your-instance.databases.neo4j.io  
   AURA_DB_PASSWORD=your-actual-password
   SPOTIFY_CLIENT_ID=your-spotify-client-id      # Optional
   SPOTIFY_CLIENT_SECRET=your-spotify-secret     # Optional
   ```

### 2. Frontend Development

```bash
# Install dependencies
npm install

# Start development server (uses .env automatically)
npm run dev
# Frontend will be available at http://localhost:3000
```

### 3. Backend Development

```bash
# Install backend dependencies  
cd backend && npm install

# Start backend server (loads from root .env automatically)
npm run start
# Backend API will be available at http://localhost:3001
```

### 4. Python Scripts (Taylor Swift Data Analysis)

```bash
# Install Python dependencies
pip install -r "dev stuff/scripts/testing_validation/requirements.txt"
pip install spotipy  # For Spotify integration (planned)

# Query current Taylor Swift database
cd "dev stuff/scripts/testing_validation/query_auradb"
python query_auradb.py stats
python query_auradb.py "MATCH (s:Song) RETURN s.title, s.albumCode LIMIT 10"

# Test database connections
python "dev stuff/scripts/testing_validation/test_auradb_connections/test_auradb_connections.py"

# Future: Spotify audio features integration
# python "dev stuff/scripts/spotify_knowledge_graph/spotify_knowledge_builder/spotify_knowledge_builder.py"
```

## 🌐 Deployment

### Vercel Deployment

The app is deployed to: **https://mb-1shot.vercel.app**

Environment variables are managed in Vercel dashboard and override the `.env` file values in production.

**Required Vercel Environment Variables:**
```
OPENAI_API_KEY=sk-your-production-key
AURA_DB_URI=neo4j+s://your-production-instance.databases.neo4j.io
AURA_DB_PASSWORD=your-production-password
NODE_ENV=production
```

## 🔧 Development Workflow

### Adding New Configuration

1. **Add to main `.env` file** with appropriate prefix:
   ```env
   # For backend/Python scripts (no prefix needed)
   NEW_API_KEY=your-key
   
   # For frontend (requires VITE_ prefix) 
   VITE_NEW_SETTING=your-setting
   ```

2. **Never duplicate configuration** in other files

3. **Document the new variable** in the `.env` file comments

### Working with Scripts

All Python scripts automatically load from the main `.env` file:

```python
from dotenv import load_dotenv
import os

load_dotenv()  # Loads from .env in project root
api_key = os.getenv('SPOTIFY_CLIENT_ID')
```

### Environment Variable Precedence

1. **Vercel Environment Variables** (production override)
2. **Local `.env` file** (development default)
3. **System environment variables** (fallback)

## 📚 Key Features

- **🎵 Taylor Swift Knowledge Graph**: Complete discography analysis with 232 songs across 12 albums
- **🤖 AI Chat Interface**: OpenAI-powered conversations about Taylor Swift's music  
- **📊 Interactive Visualizations**: D3.js charts showing lyrical patterns and evolution
- **📝 Advanced Lyrical Analysis**: Word-level analysis with 11,642 lyric lines and 2,179 unique words
- **🎧 Future Spotify Integration**: Planned audio features integration for enhanced analysis
- **🔄 Real-time Updates**: WebSocket-based live data sync

## 📊 Current Database Contents

- **232 Song nodes**: Taylor Swift's complete discography including vault tracks and re-recordings
- **12 Album nodes**: From debut album through Tortured Poets Department
- **1 Artist node**: Taylor Swift with comprehensive metadata
- **11,642 LyricLine nodes**: Detailed line-by-line lyrical analysis
- **2,179 Word nodes**: Unique vocabulary across the entire catalog
- **Advanced Analytics**: Word diversity, lyrical complexity, and semantic analysis

## 🛠️ Technology Stack

- **Frontend**: Vue.js 3, Vite, D3.js
- **Backend**: Node.js, Express, WebSocket
- **Database**: Neo4j AuraDB
- **AI**: OpenAI GPT API
- **Music Data**: Spotify Web API
- **Deployment**: Vercel
- **Data Processing**: Python scripts

## 📖 Documentation

### Current Documentation in `dev stuff/documentation/`:
- `auradb guides/` - AuraDB connection and query guides
- `env credential management guide.md` - Environment setup
- `port management guide.md` - Development server configuration

### Development Plans in `dev stuff/dev plans/`:
- `additional fields for songs.md` - Database schema extensions for music taxonomy
- `fields for songs ex spotify.md` - Spotify audio features integration framework
- `word unique identifiers/` - Advanced lyrical analysis optimization

### Data Status Reports:
- `dev stuff/scripts/top_100_usa_musicians/AURADB_STATUS_REPORT.md` - Database content overview

## 🛣️ Development Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Taylor Swift complete discography (232 songs)
- [x] Advanced lyrical analysis with word-level breakdown
- [x] Neo4j AuraDB integration and optimization
- [x] Basic Vue.js frontend and Node.js backend

### 🚧 Phase 2: Audio Features Integration (In Progress)
- [ ] Spotify API integration for audio features
- [ ] Music taxonomy system (12 categories)
- [ ] Hybrid lyrical-audio analysis algorithms
- [ ] Enhanced visualization components

### 🎯 Phase 3: Advanced Analytics (Planned)
- [ ] Temporal analysis (lyrical evolution over time)
- [ ] Semantic clustering and theme detection
- [ ] Personalized music personality insights
- [ ] Interactive timeline visualizations

### 🚀 Phase 4: Scaling Strategy (Future)
- [ ] Multi-artist expansion framework
- [ ] Real-time recommendation engine
- [ ] Community features and social integration

## 🤝 Contributing

1. **Follow the single source of truth principle** - always use the main `.env` file
2. **Focus on Taylor Swift analysis** - perfect the concept before scaling
3. **Document any new environment variables** with clear comments
4. **Test changes across frontend, backend, and scripts**
5. **Never commit real credentials** to the repository

## 🔐 Security Notes

- The `.env` file contains placeholder values safe for repository
- Real credentials should be set locally or in Vercel environment variables
- Never commit `.env.local` or files with real credentials
- Use environment variable overrides in production

---

**🎵 Happy coding with Music Besties - Taylor's Version!** 🎵 