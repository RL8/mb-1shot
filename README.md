# 🎵 Music Besties - Knowledge Graph Chat Application

A sophisticated Vue.js application that creates interactive music knowledge graphs using Neo4j and provides AI-powered chat functionality.

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

### 4. Python Scripts (Data Population)

```bash
# Install Python dependencies
pip install -r "dev stuff/testing/requirements.txt"
pip install spotipy  # For Spotify scripts

# Test Spotify API connection
python "dev stuff/data-scripts/scripts/test_spotify_api.py"

# Run knowledge graph builder
python "dev stuff/data-scripts/scripts/spotify_knowledge_builder.py"
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

- **🎵 Music Knowledge Graph**: Neo4j-powered relationship mapping
- **🤖 AI Chat Interface**: OpenAI-powered music conversations  
- **📊 Interactive Visualizations**: D3.js charts and graphs
- **🎧 Spotify Integration**: Real-time music data and audio features
- **🔄 Real-time Updates**: WebSocket-based live data sync

## 🛠️ Technology Stack

- **Frontend**: Vue.js 3, Vite, D3.js
- **Backend**: Node.js, Express, WebSocket
- **Database**: Neo4j AuraDB
- **AI**: OpenAI GPT API
- **Music Data**: Spotify Web API
- **Deployment**: Vercel
- **Data Processing**: Python scripts

## 📖 Documentation

Detailed documentation is available in `dev stuff/documentation/`:

- `SETUP_PYTHON_SCRIPT.md` - Python scripts setup
- `SPOTIFY_APPROACH_SUMMARY.md` - Spotify integration guide  
- `AGUI_INTEGRATION_GUIDE.md` - AI chat setup
- `DEPLOYMENT_SETUP.md` - Production deployment

## 🤝 Contributing

1. **Follow the single source of truth principle** - always use the main `.env` file
2. **Document any new environment variables** with clear comments
3. **Test changes across frontend, backend, and scripts**
4. **Never commit real credentials** to the repository

## 🔐 Security Notes

- The `.env` file contains placeholder values safe for repository
- Real credentials should be set locally or in Vercel environment variables
- Never commit `.env.local` or files with real credentials
- Use environment variable overrides in production

---

**🎵 Happy coding with Music Besties!** 🎵 