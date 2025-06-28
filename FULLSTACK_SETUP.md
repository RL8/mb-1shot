# Full-Stack Mobile App Setup

## 🏗️ Architecture Overview

Your mobile Vue app now has a complete full-stack setup:

- **Frontend**: Vue 3 mobile app → **Vercel**
- **Backend**: Node.js/Express API → **Render**
- **Deployment**: GitHub Actions for both services

## 🚀 Quick Start

### 1. Development (Both Frontend & Backend)
```bash
# Install all dependencies
npm install
cd backend && npm install && cd ..

# Run both frontend and backend together
npm run dev:full

# Or run separately:
npm run dev          # Frontend only (port 3000)
npm run dev:backend  # Backend only (port 3001)
```

### 2. Test Full-Stack Locally
- Frontend: http://localhost:3000
- Backend API: http://localhost:3001/health
- App will show "✅ Connected to backend API" when working

## 📡 Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/features` | Get app features |
| POST | `/api/actions` | Process user actions |
| POST | `/api/analytics` | Track events |
| GET | `/api/device-info` | Get device information |
| GET | `/api/settings` | Get app configuration |

## 🔧 Environment Configuration

### Frontend (.env.development)
```env
VITE_API_URL=http://localhost:3001
VITE_APP_NAME=Mobile Vue App
VITE_APP_ENV=development
```

### Frontend (.env.production)
```env
VITE_API_URL=https://mb-1shot-backend.onrender.com
VITE_APP_NAME=Mobile Vue App  
VITE_APP_ENV=production
```

### Backend (backend/.env)
```env
PORT=3001
NODE_ENV=development
FRONTEND_URL=http://localhost:3000
```

## 🌐 Deployment to Render

### Option 1: GitHub Integration (Recommended)
1. **Connect Repository to Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo: `RL8/mb-1shot`

2. **Configure Service**:
   - **Name**: `mb-1shot-backend`
   - **Runtime**: `Node`
   - **Build Command**: `cd backend && npm install`
   - **Start Command**: `cd backend && npm start`
   - **Auto-Deploy**: `Yes`

3. **Environment Variables**:
   - `NODE_ENV` = `production`
   - `FRONTEND_URL` = `https://your-vercel-url.vercel.app`

### Option 2: Render.yaml (Alternative)
The `render.yaml` file is already configured for automatic deployment.

## 🔄 Deployment Flow

### Frontend (Vercel)
```bash
git push origin master
# → GitHub Actions → Vercel deployment
```

### Backend (Render)
```bash
git push origin master  
# → Render auto-deploy → Backend updated
```

## 📱 Mobile App Features

### With Backend Connected:
- ✅ Real-time feature loading from API
- ✅ User action tracking and processing
- ✅ Analytics event collection
- ✅ Device information detection
- ✅ Dynamic app configuration

### Offline Mode:
- ⚠️ Fallback to cached data
- ⚠️ Local-only interactions
- ⚠️ No analytics tracking

## 🛠️ Development Workflow

1. **Make Changes**: Edit Vue components or API endpoints
2. **Test Locally**: Use `npm run dev:full` to test both services
3. **Commit & Push**: Changes automatically deploy to both services
4. **Verify**: Check both Vercel and Render deployments

## 📊 Monitoring

### Frontend (Vercel)
- Dashboard: https://vercel.com/dashboard
- Analytics: Built-in web vitals
- Logs: Real-time deployment logs

### Backend (Render)
- Dashboard: https://dashboard.render.com
- Logs: Real-time server logs
- Health: `/health` endpoint monitoring

## 🔍 Troubleshooting

### "Running in offline mode"
- Check if backend is running: `curl http://localhost:3001/health`
- Verify environment variables are set correctly
- Check CORS configuration in backend/server.js

### Backend deployment fails
- Check `render.yaml` configuration
- Verify build commands in Render dashboard
- Check logs in Render dashboard

### Frontend can't connect to backend
- Update `VITE_API_URL` in environment files
- Check CORS origins in backend
- Verify both services are deployed

## 🎯 Next Steps

1. **Add Database**: PostgreSQL on Render (free tier available)
2. **Add Authentication**: JWT tokens with user management
3. **Add Push Notifications**: Service workers + FCM
4. **Add Caching**: Redis for session storage
5. **Add File Upload**: Cloudinary or AWS S3 integration

## 📚 Useful Commands

```bash
# Development
npm run dev:full              # Both services
npm run dev                   # Frontend only
npm run dev:backend          # Backend only

# Production builds
npm run build                # Frontend build
cd backend && npm start      # Backend production

# Deployment
npm run deploy:vercel        # Manual Vercel deploy
# Backend deploys automatically via Render

# Health checks
curl http://localhost:3001/health
curl https://mb-1shot-backend.onrender.com/health
```

Your mobile app is now a complete full-stack application! 🎉 