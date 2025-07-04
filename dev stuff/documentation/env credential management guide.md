# 🎯 Configuration Management Guide - Single Source of Truth

## 📋 Overview

As of this update, **ALL configuration for the Music Besties project is centralized in the main `.env` file**. This eliminates configuration duplication and provides a single place to manage all environment variables across the entire project.

## 🔄 What Changed

### ❌ Before (Multiple Configuration Files)
```
mb-1shot/
├── .env.development          ← Duplicate config
├── .env.production           ← Duplicate config  
├── backend/.env.example      ← Separate backend config
└── [Various hardcoded values in scripts]
```

### ✅ After (Single Source of Truth)
```
mb-1shot/
├── .env                      ← 🎯 SINGLE SOURCE OF TRUTH
├── backend/.env.example      ← Reference only (deprecated)
└── [All scripts load from main .env]
```

## 📁 How Each Component Loads Configuration

### 1. Frontend (Vue.js/Vite)
```javascript
// vite.config.js automatically loads from .env
// Uses VITE_ prefixed variables only
const env = loadEnv(mode, process.cwd(), '')
```

**Available in browser:**
- `VITE_API_URL`
- `VITE_APP_NAME` 
- `VITE_APP_VERSION`
- `VITE_APP_ENV`

### 2. Backend (Node.js/Express)
```javascript
// backend/server.js
require('dotenv').config(); // Loads from root .env automatically
const port = process.env.PORT;
const dbUri = process.env.AURA_DB_URI;
```

**Loads ALL variables from main `.env` file**

### 3. Python Scripts
```python
# All Python scripts now use explicit path to main .env
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)
```

**Scripts Updated:**
- `spotify_knowledge_builder.py`
- `spotify_knowledge_builder_enhanced.py` 
- `test_spotify_api.py`

### 4. Deployment (Vercel)
```json
// vercel.json - Environment variables override .env
{
  "env": {
    "NODE_ENV": "production",
    "FRONTEND_URL": "https://mb-1shot.vercel.app"
  }
}
```

**Vercel environment variables take precedence over `.env` file**

## 🛠️ Main `.env` File Structure

```env
# =============================================================================
# 🎵 MUSIC BESTIES - SINGLE SOURCE OF TRUTH CONFIGURATION
# =============================================================================

# Frontend Configuration (VITE_ prefix for client access)
VITE_API_URL=http://localhost:3001
VITE_APP_NAME=Music Besties

# Backend Configuration  
PORT=3001
FRONTEND_URL=http://localhost:3000

# Database & APIs
AURA_DB_URI=your_aura_db_uri_here
AURA_DB_PASSWORD=your_aura_db_password_here
OPENAI_API_KEY=your_openai_api_key_here
SPOTIFY_CLIENT_ID=your_spotify_client_id_here

# Deployment
PRODUCTION_FRONTEND_URL=https://mb-1shot.vercel.app
```

## 📝 Developer Guidelines

### ✅ DO:

1. **Always add new configuration to main `.env` file**
   ```env
   # Add new variables here with appropriate prefix
   NEW_API_KEY=your-key                    # Backend/Python access
   VITE_NEW_SETTING=your-setting          # Frontend access  
   ```

2. **Use descriptive comments in `.env` file**
   ```env
   # Spotify API Configuration - Get from developer.spotify.com
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   ```

3. **Reference the main `.env` in documentation**
   ```markdown
   Configure your API key in the main `.env` file:
   OPENAI_API_KEY=sk-your-key
   ```

### ❌ DON'T:

1. **Never create separate config files**
   ```
   ❌ backend/.env
   ❌ .env.local.example  
   ❌ config/development.json
   ```

2. **Never hardcode configuration values**
   ```javascript
   // ❌ Don't do this
   const apiUrl = 'http://localhost:3001';
   
   // ✅ Do this instead
   const apiUrl = process.env.VITE_API_URL;
   ```

3. **Never duplicate configuration across files**
   ```
   ❌ Same variable in multiple places
   ❌ Hardcoded values in scripts
   ```

## 🔧 Migration for Existing Developers

If you have existing local configuration files:

### 1. **Backup Your Current Values**
```bash
# Save your current credentials
cp backend/.env my-backup-credentials.txt  # If you have one
```

### 2. **Update Main `.env` File**
```bash
# Edit the main .env file with your actual values
# Replace all placeholder values with your real credentials
```

### 3. **Remove Old Config Files**
```bash
# Clean up old configuration files
rm backend/.env                 # If exists
rm .env.development.local       # If exists  
rm .env.production.local        # If exists
```

### 4. **Test All Components**
```bash
# Test frontend
npm run dev

# Test backend  
cd backend && npm start

# Test Python scripts
python "dev stuff/data-scripts/scripts/test_spotify_api.py"
```

## 🚀 Production Deployment

### Vercel Environment Variables

Set these in your Vercel dashboard (they override `.env` values):

```
OPENAI_API_KEY=sk-your-production-key
AURA_DB_URI=neo4j+s://your-production-instance
AURA_DB_PASSWORD=your-production-password
SPOTIFY_CLIENT_ID=your-production-spotify-id
SPOTIFY_CLIENT_SECRET=your-production-spotify-secret
NODE_ENV=production
```

### Environment Variable Precedence

1. **Vercel Environment Variables** (highest priority)
2. **Main `.env` file** (development default)
3. **System environment variables** (fallback)

## 🔍 Troubleshooting

### Configuration Not Loading

```bash
# Check if .env file exists
ls -la .env

# Verify file content
cat .env | grep -v password  # Hide sensitive values

# Test Python script loading
python -c "
from pathlib import Path
from dotenv import load_dotenv
import os

project_root = Path.cwd()
env_path = project_root / '.env'
print(f'Env file exists: {env_path.exists()}')
load_dotenv(env_path)
print(f'PORT value: {os.getenv(\"PORT\")}')
"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Frontend can't access env vars | Ensure variables have `VITE_` prefix |
| Backend can't load config | Check `require('dotenv').config()` is called |
| Python scripts fail | Verify path calculation to main `.env` |
| Production deployment issues | Set environment variables in Vercel dashboard |

## 📚 Benefits of This Approach

1. **🎯 Single Source of Truth**: No configuration scattered across files
2. **🔄 Easy Synchronization**: Changes in one place affect entire project  
3. **📝 Better Documentation**: All configuration documented in one file
4. **🚀 Simpler Deployment**: Clear separation between dev and prod config
5. **🛠️ Easier Debugging**: All configuration in one place to check
6. **👥 Team Consistency**: Every developer uses the same configuration approach

---

**This configuration approach is now the standard for the Music Besties project. All future development should follow these guidelines.** 