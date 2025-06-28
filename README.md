# 🎵 Music Besties

**A mobile-first app for exploring artist discographies through beautiful, interactive charts.**

> **Music Besties** lets fans dive deep into their favorite artists' musical journeys with touch-optimized data visualizations, timeline explorations, and comprehensive discography analytics.

![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![ECharts](https://img.shields.io/badge/ECharts-AA344D?style=for-the-badge&logo=apache-echarts&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)

## ✨ Features

### 🎤 **Artist Exploration**
- **Interactive Artist Selection** with emoji-based design
- **Complete Discographies** for Taylor Swift, The Weeknd, Billie Eilish
- **Touch-Optimized Interface** designed exclusively for mobile
- **Real-time Chart Switching** between different visualization types

### 📊 **Data Visualizations** 
- **📅 Timeline Charts** - Track album releases over artist's career
- **⭐ Popularity Charts** - Compare album ratings and success
- **🎵 Genre Analysis** - Visualize musical evolution and style changes
- **Mobile-First Design** - Optimized for finger interactions and gestures

### 🎨 **Beautiful Mobile UI**
- **Touch Gestures** - Pinch, zoom, and swipe through charts
- **Gradient Artist Buttons** with music-themed styling
- **Album Cards** with popularity ratings and genre tags
- **Smooth Animations** and responsive feedback

### 🚀 **Production Ready**
- **Auto-Deployment** to Vercel (frontend) + Render (backend)
- **GitHub Actions** CI/CD pipeline
- **Environment-Based** configuration
- **Analytics Tracking** for user interactions

## 🏗️ Project Structure

```
music-besties/
├── 📁 src/
│   ├── App.vue              # Main Music Besties app
│   ├── components/
│   │   └── MusicChart.vue   # Interactive ECharts component
│   ├── services/
│   │   └── api.js           # Backend API integration
│   └── style.css            # Music-themed mobile styling
├── 📁 backend/
│   └── server.js            # Express API with artist data
├── 📁 .github/workflows/
│   └── deploy.yml           # Auto-deployment pipeline
└── package.json             # Dependencies including ECharts
```

## 🚀 Quick Start

### 1️⃣ **Install Dependencies**
```bash
npm install
cd backend && npm install && cd ..
```

### 2️⃣ **Start Development**
```bash
# Start both frontend and backend
npm run dev:full

# Frontend: http://localhost:3000
# Backend:  http://localhost:3001
```

### 3️⃣ **Explore Artists**
1. Open the app on your mobile device
2. Select an artist (🦋 Taylor Swift, 🌙 The Weeknd, 💚 Billie Eilish)
3. Interact with the charts using touch gestures
4. Switch between Timeline, Popularity, and Genre views

## 🎤 Featured Artists

### 🦋 **Taylor Swift**
- **10 Albums** from 2006-2022
- **Genre Evolution**: Country → Pop → Indie Folk
- **Career Highlights**: 1989, Folklore, Midnights

### 🌙 **The Weeknd** 
- **9 Albums** from 2011-2022
- **Signature Sound**: Alternative R&B → Synth-pop
- **Peak Albums**: Beauty Behind the Madness, After Hours

### 💚 **Billie Eilish**
- **3 Albums** from 2017-2021
- **Consistent Genre**: Alternative Pop
- **Breakthrough**: When We All Fall Asleep, Where Do We Go?

## 📊 Chart Types

| Chart Type | Description | Best For |
|------------|-------------|----------|
| 📅 **Timeline** | Album releases over time | Career progression |
| ⭐ **Popularity** | Album ratings comparison | Success analysis |
| 🎵 **Genre** | Musical style breakdown | Artistic evolution |

## 🔧 API Endpoints

```javascript
GET /api/artists           // All featured artists
GET /api/artists/:id       // Specific artist details
GET /api/charts/:artistId  // Chart data for artist
GET /api/features          // App features
```

## 📱 Mobile Optimizations

- **Touch Targets**: Minimum 44px for all interactive elements
- **Gesture Support**: Pinch to zoom, swipe navigation
- **Safe Areas**: iPhone notch and home indicator support
- **Performance**: Lazy loading and efficient chart rendering
- **Offline Mode**: Fallback data when backend unavailable

## 🎨 Design System

```css
/* Music-themed color palette */
--primary-color: #007AFF;      /* iOS Blue */
--music-accent: #ff6b6b;       /* Coral */
--music-secondary: #4ecdc4;    /* Teal */
--secondary-color: #34C759;    /* Green */
```

## 🚀 Live Demo

- **Frontend**: [https://mb-1shot.vercel.app](https://mb-1shot.vercel.app)
- **Backend**: [https://mb-1shot.onrender.com](https://mb-1shot.onrender.com)
- **Repository**: [https://github.com/RL8/mb-1shot](https://github.com/RL8/mb-1shot)

## 🛠️ Development

```bash
# Frontend only
npm run dev

# Backend only  
npm run dev:backend

# Both concurrently
npm run dev:full

# Build for production
npm run build
```

## 🤝 Contributing

Want to add more artists or chart types?
1. Fork the repository
2. Add artist data in `backend/server.js`
3. Extend chart types in `MusicChart.vue`
4. Submit a pull request

## 📄 License

MIT License - Perfect for music lovers and developers alike!

---

## 🎵 **Ready to explore music like never before?**

**Music Besties** combines the power of interactive data visualization with the passion for music discovery. Dive into your favorite artists' journeys and uncover insights about their musical evolution!

⭐ **Star this repository** if you love music and data visualization! 