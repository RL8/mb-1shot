# 🎵 Music Besties - Your AI Music Companion

An AI-powered conversational music app that transforms from static artist displays into a dynamic music companion that shares your obsessions!

## 🚀 **NEW: AG-UI Integration Complete!**

Music Besties now features a **conversational AI companion** that can discuss your favorite artists with the depth and enthusiasm of a true music bestie.

### ✨ **What's New:**
- 🎵 **Conversational Interface**: Chat naturally about artists instead of just viewing data
- 🧠 **AI Music Companion**: Powered by OpenAI GPT-4 with music knowledge
- 📊 **AuraDB Knowledge Graph**: Rich, interconnected artist data and relationships
- 🔄 **Real-time Streaming**: WebSocket-powered live conversations
- 📱 **Mobile-Optimized Chat**: Touch-friendly conversational interface

## 🎯 **Features**

### **Traditional Features:**
- Interactive artist discography charts
- Mobile-first responsive design
- Artist timeline visualizations
- Album popularity analytics

### **NEW: Conversational Features:**
- Deep artist conversations with AI
- Intent-based response system
- Artist influence mapping
- Thematic analysis and insights
- Quick action buttons for exploration
- Real-time message streaming

## 🏗️ **Architecture**

```
Vue.js Frontend
    ↓ (WebSocket Connection)
Conversational Service Layer (agui.js)
    ↓ (Real-time Communication)
Express.js Backend with WebSocket Server
    ↓ (Cypher Queries)
AuraDB Neo4j Knowledge Graph
    ↓ (AI Context)
OpenAI GPT-4 Conversational AI
```

## 🚀 **Quick Start**

### **Development Setup:**
```bash
# 1. Install dependencies
npm install
cd backend && npm install && cd ..

# 2. Set up environment (backend/.env)
# Add your OpenAI API key and AuraDB credentials

# 3. Run full stack
npm run dev:full
# OR run separately:
# Terminal 1: npm run dev
# Terminal 2: cd backend && npm run dev
```

### **Try the AI Chat:**
1. Open `http://localhost:3000`
2. Select "Taylor Swift 🦋"
3. Click "💬 Start Chat"
4. Try: *"I'm obsessed with folklore!"*
5. Watch your AI music bestie respond! 🎵

## 📊 **Setup AuraDB (Optional for Full Features)**

1. Create free AuraDB instance at [neo4j.com/aura](https://neo4j.com/aura)
2. Run setup queries from `dev stuff/AURADB_SETUP.cypher`
3. Update `backend/.env` with your credentials
4. Restart backend server

## 🎪 **Example Conversations**

```
You: "Tell me about Taylor's songwriting evolution"
AI: "Taylor's evolution is absolutely fascinating! From country 
     storytelling to pop anthems to indie folk poetry... 
     *generates timeline visualization*
     See how her lyrical complexity increased with folklore?"

You: "I love The Weeknd's dark aesthetic"
AI: "YES! The way Abel channels Prince and MJ into something 
     completely his own... After Hours was pure 80s synth 
     perfection mixed with that signature melancholy."
```

## 🔧 **Tech Stack**

- **Frontend**: Vue.js 3, WebSocket API, ECharts
- **Backend**: Express.js, WebSocket Server, OpenAI API
- **Database**: Neo4j AuraDB (Knowledge Graph)
- **AI**: OpenAI GPT-4
- **Deployment**: Vercel (Frontend), Render (Backend)

## 📁 **Project Structure**

```
mb-1shot/
├── src/
│   ├── components/
│   │   ├── MusicBestieChat.vue     # Main chat interface
│   │   └── MusicChart.vue          # Chart visualizations
│   ├── services/
│   │   ├── agui.js                 # Conversational service layer
│   │   └── api.js                  # Traditional API service
│   └── App.vue                     # Main app with chat integration
├── backend/
│   ├── agui-server.js              # WebSocket + AI server
│   ├── server.js                   # Main Express server
│   └── .env                        # Environment configuration
└── dev stuff/
    ├── AURADB_SETUP.cypher        # Database setup script
    ├── AGUI_INTEGRATION_GUIDE.md  # Original integration guide
    └── AGUI_COMPLETION_GUIDE.md   # Implementation status
```

## 🎵 **Artist Data**

Currently includes comprehensive data for:
- **Taylor Swift** 🦋 - Complete discography with folklore/evermore deep dive
- **The Weeknd** 🌙 - From mixtapes to mainstream success
- **Billie Eilish** 💚 - Alternative pop evolution

Each artist includes:
- Complete discography with themes and genres
- Artistic influences and relationships
- Producer collaborations
- Song-level analysis for key tracks

## 🚀 **Deployment**

### **Environment Variables:**
```bash
# Frontend (Vercel)
VITE_API_URL=https://your-backend.onrender.com

# Backend (Render/Railway)
PORT=3001
OPENAI_API_KEY=sk-your-openai-key
AURA_DB_URI=neo4j+s://your-instance.databases.neo4j.io
AURA_DB_USERNAME=neo4j
AURA_DB_PASSWORD=your-password
AGUI_ENABLED=true
```

## 🎯 **What Makes This Special**

Unlike traditional music apps that just display data, Music Besties creates a **genuine conversation** about the artists you love. The AI doesn't just recite facts - it shares your enthusiasm, asks follow-up questions, and generates insights that make you see your favorite artists in new ways.

**This is music discovery through conversation, not just data consumption.** 🎵✨

## 📖 **Documentation**

- `dev stuff/AGUI_INTEGRATION_GUIDE.md` - Original vision and technical guide
- `dev stuff/AGUI_COMPLETION_GUIDE.md` - Implementation status and setup
- `dev stuff/AURADB_SETUP.cypher` - Database schema and sample data

---

**Built with 🎵 for music lovers who want to go deeper into their obsessions.** 