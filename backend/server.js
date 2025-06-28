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

// Sample music data for demonstration
const sampleArtists = [
  {
    id: 1,
    name: 'Taylor Swift',
    emoji: '🦋',
    genre: 'Pop/Country',
    activeYears: '2006-Present',
    discography: [
      { id: 1, album: 'Taylor Swift', year: '2006', genre: 'Country', popularity: 75 },
      { id: 2, album: 'Fearless', year: '2008', genre: 'Country', popularity: 92 },
      { id: 3, album: 'Speak Now', year: '2010', genre: 'Country Pop', popularity: 85 },
      { id: 4, album: 'Red', year: '2012', genre: 'Pop', popularity: 88 },
      { id: 5, album: '1989', year: '2014', genre: 'Pop', popularity: 94 },
      { id: 6, album: 'Reputation', year: '2017', genre: 'Pop', popularity: 82 },
      { id: 7, album: 'Lover', year: '2019', genre: 'Pop', popularity: 89 },
      { id: 8, album: 'Folklore', year: '2020', genre: 'Indie Folk', popularity: 96 },
      { id: 9, album: 'Evermore', year: '2020', genre: 'Indie Folk', popularity: 90 },
      { id: 10, album: 'Midnights', year: '2022', genre: 'Pop', popularity: 98 }
    ]
  },
  {
    id: 2,
    name: 'The Weeknd',
    emoji: '🌙', 
    genre: 'R&B/Pop',
    activeYears: '2010-Present',
    discography: [
      { id: 1, album: 'House of Balloons', year: '2011', genre: 'Alternative R&B', popularity: 85 },
      { id: 2, album: 'Thursday', year: '2011', genre: 'Alternative R&B', popularity: 82 },
      { id: 3, album: 'Echoes of Silence', year: '2011', genre: 'Alternative R&B', popularity: 80 },
      { id: 4, album: 'Trilogy', year: '2012', genre: 'Alternative R&B', popularity: 88 },
      { id: 5, album: 'Kiss Land', year: '2013', genre: 'Alternative R&B', popularity: 76 },
      { id: 6, album: 'Beauty Behind the Madness', year: '2015', genre: 'R&B Pop', popularity: 94 },
      { id: 7, album: 'Starboy', year: '2016', genre: 'Pop R&B', popularity: 91 },
      { id: 8, album: 'After Hours', year: '2020', genre: 'Synth-pop', popularity: 96 },
      { id: 9, album: 'Dawn FM', year: '2022', genre: 'Synth-pop', popularity: 89 }
    ]
  },
  {
    id: 3,
    name: 'Billie Eilish',
    emoji: '💚',
    genre: 'Alternative Pop', 
    activeYears: '2016-Present',
    discography: [
      { id: 1, album: 'dont smile at me (EP)', year: '2017', genre: 'Alternative Pop', popularity: 78 },
      { id: 2, album: 'When We All Fall Asleep, Where Do We Go?', year: '2019', genre: 'Alternative Pop', popularity: 95 },
      { id: 3, album: 'Happier Than Ever', year: '2021', genre: 'Alternative Pop', popularity: 92 }
    ]
  }
];

// Music Besties API endpoints
app.get('/api/artists', (req, res) => {
  res.json(sampleArtists);
});

app.get('/api/artists/:id', (req, res) => {
  const artistId = parseInt(req.params.id);
  const artist = sampleArtists.find(a => a.id === artistId);
  
  if (artist) {
    res.json(artist);
  } else {
    res.status(404).json({ error: 'Artist not found' });
  }
});

app.get('/api/charts/:artistId', (req, res) => {
  const artistId = parseInt(req.params.artistId);
  const artist = sampleArtists.find(a => a.id === artistId);
  
  if (artist) {
    // Generate chart data based on discography
    const chartData = {
      timeline: artist.discography.map(album => ({
        year: album.year,
        album: album.album,
        value: album.popularity
      })),
      popularity: artist.discography.map(album => ({
        album: album.album,
        popularity: album.popularity
      })),
      genres: artist.discography.reduce((acc, album) => {
        acc[album.genre] = (acc[album.genre] || 0) + 1;
        return acc;
      }, {})
    };
    
    res.json(chartData);
  } else {
    res.status(404).json({ error: 'Artist not found' });
  }
});

// Update the features endpoint to return music-focused features
app.get('/api/features', (req, res) => {
  const musicFeatures = [
    {
      id: 1,
      icon: '🎤',
      title: 'Artist Discovery',
      description: 'Explore discographies of popular artists',
      details: `${sampleArtists.length} artists available`
    },
    {
      id: 2,
      icon: '📊',
      title: 'Interactive Charts',
      description: 'Visualize music data in creative ways',
      details: 'Timeline, popularity, and genre charts'
    },
    {
      id: 3,
      icon: '🎵',
      title: 'Album Analytics',
      description: 'Deep dive into album popularity and trends',
      details: 'Comprehensive discography analysis'
    },
    {
      id: 4,
      icon: '❤️',
      title: 'Music Besties',
      description: 'Connect with fellow music lovers',
      details: 'Share and discover new music together'
    }
  ];
  
  res.json(musicFeatures);
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