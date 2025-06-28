const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet());

// CORS configuration - allow your frontend domains
app.use(cors({
  origin: [
    'http://localhost:3000',
    'https://rl8.github.io',
    /\.vercel\.app$/,  // Allow all Vercel preview deployments
    process.env.FRONTEND_URL
  ].filter(Boolean),
  credentials: true
}));

// Parse JSON bodies
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API Routes for mobile app
app.get('/api/features', (req, res) => {
  const features = [
    {
      id: 1,
      icon: '📱',
      title: 'Mobile First',
      description: 'Optimized for touch interactions',
      details: 'Built specifically for mobile devices with touch-friendly UI components'
    },
    {
      id: 2,
      icon: '⚡',
      title: 'Fast Loading',
      description: 'Built with Vite for speed',
      details: 'Lightning-fast development and optimized production builds'
    },
    {
      id: 3,
      icon: '🎨',
      title: 'Modern UI',
      description: 'Clean and responsive design',
      details: 'Contemporary design patterns with smooth animations'
    },
    {
      id: 4,
      icon: '🔒',
      title: 'Secure Backend',
      description: 'API hosted on Render',
      details: 'Scalable and secure backend infrastructure'
    }
  ];
  
  res.json(features);
});

// User actions endpoint
app.post('/api/actions', (req, res) => {
  const { type, data } = req.body;
  
  // Simulate processing
  const response = {
    success: true,
    action: type,
    timestamp: new Date().toISOString(),
    message: `${type} action processed successfully`,
    data: data || null
  };
  
  res.json(response);
});

// Mobile analytics endpoint
app.post('/api/analytics', (req, res) => {
  const { event, properties } = req.body;
  
  // In a real app, you'd save this to a database
  console.log('Analytics event:', { event, properties, timestamp: new Date().toISOString() });
  
  res.json({ 
    success: true, 
    message: 'Event tracked successfully' 
  });
});

// Mobile device info endpoint
app.get('/api/device-info', (req, res) => {
  const userAgent = req.headers['user-agent'] || '';
  const isMobile = /Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent);
  
  res.json({
    isMobile,
    userAgent,
    headers: {
      'x-forwarded-for': req.headers['x-forwarded-for'],
      'accept-language': req.headers['accept-language']
    },
    serverInfo: {
      node: process.version,
      platform: process.platform,
      uptime: process.uptime()
    }
  });
});

// Settings endpoint for mobile app configuration
app.get('/api/settings', (req, res) => {
  res.json({
    theme: {
      primaryColor: '#007AFF',
      secondaryColor: '#34C759',
      isDarkMode: false
    },
    features: {
      pushNotifications: true,
      analytics: true,
      offlineMode: false
    },
    api: {
      version: '1.0.0',
      rateLimit: 1000,
      timeout: 30000
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err.stack);
  res.status(500).json({ 
    error: 'Something went wrong!',
    message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ 
    error: 'Route not found',
    path: req.originalUrl 
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Backend server running on port ${PORT}`);
  console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📱 Mobile API ready for connections`);
}); 