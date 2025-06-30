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

// Database connection test endpoint for debugging
app.get('/api/db-test', async (req, res) => {
  console.log('=== AuraDB Connection Test ===');
  console.log('Environment variables:');
  console.log('AURA_DB_URI:', process.env.AURA_DB_URI ? 'SET' : 'NOT SET');
  console.log('AURA_DB_USERNAME:', process.env.AURA_DB_USERNAME ? 'SET' : 'NOT SET');
  console.log('AURA_DB_PASSWORD:', process.env.AURA_DB_PASSWORD ? 'SET (length: ' + (process.env.AURA_DB_PASSWORD?.length || 0) + ')' : 'NOT SET');
  
  const response = {
    timestamp: new Date().toISOString(),
    environment: {
      NODE_ENV: process.env.NODE_ENV,
      AURA_DB_URI: process.env.AURA_DB_URI ? 'SET' : 'NOT SET',
      AURA_DB_USERNAME: process.env.AURA_DB_USERNAME ? 'SET' : 'NOT SET',
      AURA_DB_PASSWORD: process.env.AURA_DB_PASSWORD ? 'SET (length: ' + (process.env.AURA_DB_PASSWORD?.length || 0) + ')' : 'NOT SET'
    },
    driver: {
      initialized: !!driver,
      config: {
        uri: process.env.AURA_DB_URI?.substring(0, 30) + '...' || 'NOT SET'
      }
    },
    tests: []
  };

  try {
    // Test 1: Basic driver verification
    console.log('Test 1: Driver verification...');
    response.tests.push({
      name: 'Driver Initialization',
      status: driver ? 'PASS' : 'FAIL',
      details: driver ? 'Driver object exists' : 'Driver object missing'
    });

    if (!driver) {
      return res.json(response);
    }

    // Test 2: Session creation
    console.log('Test 2: Session creation...');
    const session = driver.session();
    response.tests.push({
      name: 'Session Creation',
      status: 'PASS',
      details: 'Session created successfully'
    });

    // Test 3: Simple connectivity test
    console.log('Test 3: Connectivity test...');
    const connectivityResult = await session.run('RETURN 1 as test');
    const testValue = connectivityResult.records[0].get('test').toNumber();
    
    response.tests.push({
      name: 'Basic Connectivity',
      status: testValue === 1 ? 'PASS' : 'FAIL',
      details: `Received: ${testValue}, Expected: 1`
    });

    // Test 4: Database info
    console.log('Test 4: Database info...');
    const dbInfoResult = await session.run('CALL dbms.components() YIELD name, versions, edition');
    const dbInfo = dbInfoResult.records.map(record => ({
      name: record.get('name'),
      versions: record.get('versions'),
      edition: record.get('edition')
    }));

    response.tests.push({
      name: 'Database Info',
      status: 'PASS',
      details: dbInfo
    });

    // Test 5: Check for existing data
    console.log('Test 5: Data check...');
    const dataResult = await session.run('MATCH (n) RETURN count(n) as nodeCount LIMIT 1');
    const nodeCount = dataResult.records[0].get('nodeCount').toNumber();
    
    response.tests.push({
      name: 'Data Check',
      status: 'PASS',
      details: `Total nodes in database: ${nodeCount}`
    });

    await session.close();
    response.overall = 'SUCCESS';
    console.log('=== All tests completed successfully ===');

  } catch (error) {
    console.error('Database test failed:', error);
    response.tests.push({
      name: 'Connection Test',
      status: 'FAIL',
      details: {
        message: error.message,
        code: error.code,
        name: error.name,
        stack: error.stack?.split('\n').slice(0, 5) // First 5 lines of stack
      }
    });
    response.overall = 'FAILED';
    response.error = {
      message: error.message,
      code: error.code,
      type: error.constructor.name
    };
  }

  res.json(response);
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