const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();
const http = require('http');
const neo4j = require('neo4j-driver');

// Initialize Neo4j driver
const driver = neo4j.driver(
  process.env.AURA_DB_URI,
  neo4j.auth.basic(process.env.AURA_DB_USERNAME || 'neo4j', process.env.AURA_DB_PASSWORD)
);

// Import AG-UI Server
const MusicBestiesAGUIServer = require('./agui-server.js');

const app = express();
const server = http.createServer(app);

// Initialize AG-UI Server
const aguiServer = new MusicBestiesAGUIServer(server);

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

// Add AG-UI HTTP routes
app.use('/agui', aguiServer.getHTTPRoutes());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    agui: process.env.AGUI_ENABLED === 'true' ? 'enabled' : 'disabled'
  });
});

// Knowledge graph stats endpoint
app.get('/api/knowledge-graph/stats', (req, res) => {
  res.json({
    artists: sampleArtists.length,
    albums: sampleArtists.reduce((total, artist) => total + artist.discography.length, 0),
    tracks: sampleArtists.reduce((total, artist) => total + artist.discography.length * 10, 0), // Estimate 10 tracks per album
    total: sampleArtists.length + 
           sampleArtists.reduce((total, artist) => total + artist.discography.length, 0) +
           sampleArtists.reduce((total, artist) => total + artist.discography.length * 10, 0)
  });
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

// Knowledge Graph API Endpoints
app.get('/api/artists', async (req, res) => {
  try {
    const session = driver.session();
    const result = await session.run(`
      MATCH (a:Artist)
      RETURN a.name as name, a.popularity as popularity, a.followers as followers, 
             a.genres as genres, a.spotify_id as spotify_id
      ORDER BY a.popularity DESC
    `);
    
    const artists = result.records.map(record => ({
      name: record.get('name'),
      popularity: record.get('popularity'),
      followers: record.get('followers'),
      genres: record.get('genres'),
      spotify_id: record.get('spotify_id')
    }));
    
    await session.close();
    res.json({ artists, count: artists.length });
  } catch (error) {
    console.error('Error fetching artists:', error);
    res.status(500).json({ error: 'Failed to fetch artists' });
  }
});

app.get('/api/artists/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const session = driver.session();
    const result = await session.run(`
      MATCH (a:Artist {spotify_id: $artistId})-[:HAS_ALBUM]->(al:Album)
      RETURN al.name as name, al.release_date as release_date, 
             al.total_tracks as total_tracks, al.album_type as album_type,
             al.spotify_id as spotify_id
      ORDER BY al.release_date DESC
    `, { artistId: id });
    
    const albums = result.records.map(record => ({
      name: record.get('name'),
      release_date: record.get('release_date'),
      total_tracks: record.get('total_tracks'),
      album_type: record.get('album_type'),
      spotify_id: record.get('spotify_id')
    }));
    
    await session.close();
    res.json({ albums, count: albums.length });
  } catch (error) {
    console.error('Error fetching albums:', error);
    res.status(500).json({ error: 'Failed to fetch albums' });
  }
});

app.get('/api/albums/:id/tracks', async (req, res) => {
  try {
    const { id } = req.params;
    const session = driver.session();
    const result = await session.run(`
      MATCH (al:Album {spotify_id: $albumId})-[:HAS_TRACK]->(t:Track)
      RETURN t.name as name, t.track_number as track_number,
             t.duration_ms as duration_ms, t.explicit as explicit,
             t.preview_url as preview_url, t.spotify_id as spotify_id
      ORDER BY t.track_number ASC
    `, { albumId: id });
    
    const tracks = result.records.map(record => ({
      name: record.get('name'),
      track_number: record.get('track_number'),
      duration_ms: record.get('duration_ms'),
      explicit: record.get('explicit'),
      preview_url: record.get('preview_url'),
      spotify_id: record.get('spotify_id')
    }));
    
    await session.close();
    res.json({ tracks, count: tracks.length });
  } catch (error) {
    console.error('Error fetching tracks:', error);
    res.status(500).json({ error: 'Failed to fetch tracks' });
  }
});

app.get('/api/search', async (req, res) => {
  try {
    const { q, type = 'all' } = req.query;
    if (!q) {
      return res.status(400).json({ error: 'Search query required' });
    }
    
    const session = driver.session();
    let results = { artists: [], albums: [], tracks: [] };
    
    if (type === 'all' || type === 'artist') {
      const artistResult = await session.run(`
        MATCH (a:Artist)
        WHERE toLower(a.name) CONTAINS toLower($query)
        RETURN a.name as name, a.popularity as popularity, a.spotify_id as spotify_id
        ORDER BY a.popularity DESC
        LIMIT 10
      `, { query: q });
      
      results.artists = artistResult.records.map(record => ({
        name: record.get('name'),
        popularity: record.get('popularity'),
        spotify_id: record.get('spotify_id'),
        type: 'artist'
      }));
    }
    
    if (type === 'all' || type === 'album') {
      const albumResult = await session.run(`
        MATCH (a:Artist)-[:HAS_ALBUM]->(al:Album)
        WHERE toLower(al.name) CONTAINS toLower($query)
        RETURN al.name as name, a.name as artist_name, al.release_date as release_date,
               al.spotify_id as spotify_id, a.spotify_id as artist_id
        ORDER BY al.release_date DESC
        LIMIT 10
      `, { query: q });
      
      results.albums = albumResult.records.map(record => ({
        name: record.get('name'),
        artist_name: record.get('artist_name'),
        release_date: record.get('release_date'),
        spotify_id: record.get('spotify_id'),
        artist_id: record.get('artist_id'),
        type: 'album'
      }));
    }
    
    await session.close();
    res.json(results);
  } catch (error) {
    console.error('Error searching:', error);
    res.status(500).json({ error: 'Search failed' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// Start server
server.listen(PORT, () => {
  console.log(`🎵 Music Besties Backend running on port ${PORT}`);
  console.log(`🚀 AG-UI WebSocket server: ws://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('Shutting down gracefully...');
  await aguiServer.shutdown();
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});

module.exports = app; 