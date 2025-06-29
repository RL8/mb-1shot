# 🚀 Mobile Vue.js Full-Stack Template

> **Production-ready full-stack mobile app template** with Vue.js frontend and Express.js backend, including auto-deployment pipelines and comprehensive mobile optimizations.

![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E)
![Express.js](https://img.shields.io/badge/Express.js-404D59?style=for-the-badge&logo=express&logoColor=white)

## ✨ Features

### 📱 **Mobile-First Frontend**
- **Vue 3** with Composition API
- **Vite** for lightning-fast development
- **Touch-optimized UI** with gesture support
- **Responsive design** (mobile-only approach)
- **Offline mode** with connection status
- **PWA-ready** configuration

### 🖥️ **Robust Backend API** 
- **Express.js** server with security middleware
- **CORS** configured for multiple domains
- **RESTful API** endpoints for mobile features
- **Analytics & user tracking** endpoints
- **Device detection** and mobile optimization
- **Health checks** and monitoring

### 🚀 **Production Deployment**
- **Vercel** frontend deployment (auto)
- **Render** backend deployment 
- **GitHub Actions** CI/CD pipeline
- **Environment-based** configuration
- **Zero-downtime** deployments

### 🛠️ **Developer Experience**
- **Concurrent development** (frontend + backend)
- **Hot module replacement** 
- **Environment variables** management
- **Comprehensive documentation**
- **Ready-to-use** project structure

## 🏗️ Project Structure

```
mobile-vue-fullstack-template/
├── 📁 frontend/
│   ├── src/
│   │   ├── App.vue          # Main mobile app component
│   │   ├── main.js          # Vue app initialization  
│   │   ├── style.css        # Mobile-first CSS
│   │   └── services/
│   │       └── api.js       # Backend API client
│   ├── index.html           # HTML template
│   ├── vite.config.js       # Vite configuration
│   └── package.json         # Frontend dependencies
├── 📁 backend/
│   ├── server.js            # Express.js API server
│   ├── package.json         # Backend dependencies  
│   └── .env.example         # Environment template
├── 📁 .github/workflows/
│   └── deploy.yml           # GitHub Actions pipeline
├── .env.development         # Local development config
├── .env.production          # Production config
├── render.yaml              # Render deployment config
├── vercel.json              # Vercel configuration
└── package.json             # Root package.json
```

## 🚀 Quick Start

### 1️⃣ **Clone & Install**
```bash
# Clone the template
git clone https://github.com/RL8/mobile-vue-fullstack-template.git
cd mobile-vue-fullstack-template

# Install dependencies  
npm install
cd backend && npm install && cd ..
```

### 2️⃣ **Environment Setup**
```bash
# Copy environment files
cp .env.development .env.local
cp backend/.env.example backend/.env
```

### 3️⃣ **Start Development**
```bash
# Start both frontend and backend
npm run dev:full

# Frontend: http://localhost:3000
# Backend:  http://localhost:3001
```

## 📱 Mobile Features

- **Touch Gestures**: Swipe navigation, pull-to-refresh
- **Haptic Feedback**: Native mobile feel  
- **Offline Support**: Works without internet
- **Device Detection**: Mobile-specific optimizations
- **Safe Area Support**: iPhone notch compatibility
- **Performance**: Optimized for mobile devices

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/api/features` | GET | App features list |
| `/api/settings` | GET | App configuration |
| `/api/device-info` | GET | Device detection |
| `/api/actions` | POST | User action tracking |
| `/api/analytics` | POST | Event analytics |

## 🚀 Deployment

### **Automatic Deployment**
1. **Push to GitHub** - triggers auto-deployment
2. **Frontend** → Vercel (via GitHub Actions)
3. **Backend** → Render (auto-deploy enabled)

### **Manual Deployment**

**Frontend (Vercel):**
```bash
npm run deploy:vercel
```

**Backend (Render):**
- Connect your GitHub repo to Render
- Use `render.yaml` configuration
- Set environment variables

## 🔐 Environment Variables

### **Frontend (.env.production)**
```env
VITE_API_URL=https://your-backend.onrender.com
VITE_APP_NAME=Your Mobile App
VITE_APP_ENV=production
```

### **Backend (Render Environment)**
```env
NODE_ENV=production
FRONTEND_URL=https://your-app.vercel.app
PORT=3001
```

## 📦 Available Scripts

```bash
# Development
npm run dev              # Frontend only
npm run dev:backend      # Backend only  
npm run dev:full         # Both frontend & backend

# Build & Deploy
npm run build            # Build frontend
npm run preview          # Preview build
npm run deploy:vercel    # Deploy to Vercel
```

## 🔧 Customization

### **Styling**
- Modify `src/style.css` for UI changes
- Update color variables for theming
- Add/remove mobile-specific styles

### **API Endpoints**
- Edit `backend/server.js` to add new endpoints
- Update `src/services/api.js` for frontend integration
- Add authentication middleware as needed

### **Deployment**
- Update `vercel.json` for Vercel settings
- Modify `render.yaml` for Render configuration  
- Configure GitHub Actions in `.github/workflows/`

## 🔗 Live Demo

- **Frontend**: [Your App URL]
- **Backend**: [Your API URL]
- **Repository**: [GitHub Repository URL]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this template for any project!

---

## 🚀 **Ready to build your next mobile app?**

This template provides everything you need to get started with a production-ready full-stack mobile web application. Happy coding! 

⭐ **Star this repository** if you find it helpful! 