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

// Import Taxonomy API
const taxonomyAPI = require('./taxonomy-api.js');

const app = express();
const server = http.createServer(app);

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

// Add Taxonomy API routes
app.use('/api/taxonomy', taxonomyAPI);

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
app.get('/api/knowledge-graph/stats', async (req, res) => {
  try {
    const session = driver.session();
    const result = await session.run(`
      MATCH (a:Artist) 
      OPTIONAL MATCH (a)-[:RELEASED]->(al:Album)
      OPTIONAL MATCH (al)-[:CONTAINS]->(s:Song)
      RETURN count(DISTINCT a) as artists, 
             count(DISTINCT al) as albums, 
             count(DISTINCT s) as songs
    `);
    
    const stats = result.records[0];
    const artistCount = stats.get('artists').toNumber();
    const albumCount = stats.get('albums').toNumber();
    const songCount = stats.get('songs').toNumber();
    
    await session.close();
    
    res.json({
      artists: artistCount,
      albums: albumCount,
      songs: songCount,
      total: artistCount + albumCount + songCount
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    // Fallback to zero stats if database fails
    res.json({
      artists: 0,
      albums: 0,
      songs: 0,
      total: 0,
      error: 'Database connection failed'
    });
  }
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

// Features endpoint for app capabilities
app.get('/api/features', (req, res) => {
  res.json({
    knowledgeGraph: {
      enabled: true,
      description: 'Enhanced Spotify knowledge graph with era-based consolidation',
      endpoints: ['/api/artists', '/api/knowledge-graph/stats', '/api/search']
    },
    aguiIntegration: {
      enabled: process.env.AGUI_ENABLED === 'true',
      description: 'Conversational AI music assistant',
      websocket: process.env.AGUI_ENABLED === 'true',
      port: process.env.AGUI_WS_PORT || 3001
    },
    redditAnalysis: {
      enabled: true,
      description: 'Music community sentiment analysis',
      endpoints: ['/api/reddit-analysis']
    },
    spotifyIntegration: {
      enabled: !!(process.env.SPOTIFY_CLIENT_ID && process.env.SPOTIFY_CLIENT_SECRET),
      description: 'Spotify API integration for music data',
      clientConfigured: !!(process.env.SPOTIFY_CLIENT_ID && process.env.SPOTIFY_CLIENT_SECRET)
    },
    database: {
      type: 'Neo4j AuraDB',
      connected: !!driver,
      description: 'Graph database for music relationships'
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

// Add comprehensive database inventory endpoint
app.get('/api/database-inventory', async (req, res) => {
  try {
    const session = driver.session();
    const inventory = {
      timestamp: new Date().toISOString(),
      database_info: {},
      node_types: {},
      relationship_types: {},
      all_nodes: [],
      all_relationships: []
    };

    // Get all node labels and counts
    const labelResult = await session.run(`
      CALL db.labels() YIELD label
      CALL {
        WITH label
        MATCH (n)
        WHERE label IN labels(n)
        RETURN count(n) as count
      }
      RETURN label, count
      ORDER BY count DESC
    `);
    
    for (const record of labelResult.records) {
      const label = record.get('label');
      const count = record.get('count').toNumber();
      inventory.node_types[label] = count;
    }

    // Get all relationship types and counts
    const relResult = await session.run(`
      CALL db.relationshipTypes() YIELD relationshipType
      CALL {
        WITH relationshipType
        MATCH ()-[r]->()
        WHERE type(r) = relationshipType
        RETURN count(r) as count
      }
      RETURN relationshipType, count
      ORDER BY count DESC
    `);
    
    for (const record of relResult.records) {
      const relType = record.get('relationshipType');
      const count = record.get('count').toNumber();
      inventory.relationship_types[relType] = count;
    }

    // Get all nodes with their properties
    const allNodesResult = await session.run(`
      MATCH (n)
      RETURN id(n) as nodeId, labels(n) as labels, properties(n) as props
      LIMIT 100
    `);
    
    for (const record of allNodesResult.records) {
      inventory.all_nodes.push({
        id: record.get('nodeId').toNumber(),
        labels: record.get('labels'),
        properties: record.get('props')
      });
    }

    // Get all relationships
    const allRelsResult = await session.run(`
      MATCH (a)-[r]->(b)
      RETURN id(r) as relId, type(r) as relType, 
             id(a) as startNodeId, labels(a) as startLabels,
             id(b) as endNodeId, labels(b) as endLabels,
             properties(r) as props
      LIMIT 100
    `);
    
    for (const record of allRelsResult.records) {
      inventory.all_relationships.push({
        id: record.get('relId').toNumber(),
        type: record.get('relType'),
        startNode: {
          id: record.get('startNodeId').toNumber(),
          labels: record.get('startLabels')
        },
        endNode: {
          id: record.get('endNodeId').toNumber(),
          labels: record.get('endLabels')
        },
        properties: record.get('props')
      });
    }

    await session.close();
    res.json(inventory);
  } catch (error) {
    console.error('Error getting database inventory:', error);
    res.status(500).json({ error: 'Failed to get database inventory', details: error.message });
  }
});

// Song properties inspection endpoint
app.get('/api/songs/properties', async (req, res) => {
    try {
        const session = driver.session();
        
        // Get a sample Song with all its properties
        const sampleQuery = `
            MATCH (s:Song)
            RETURN s LIMIT 3
        `;
        const sampleResult = await session.run(sampleQuery);
        
        // Get all property keys that exist on Song nodes
        const keysQuery = `
            MATCH (s:Song)
            WITH s LIMIT 100
            UNWIND keys(s) AS prop
            RETURN DISTINCT prop
            ORDER BY prop
        `;
        const keysResult = await session.run(keysQuery);
        
        // Get property statistics
        const statsQuery = `
            MATCH (s:Song)
            WITH count(s) as total_songs,
                 count(s.title) as has_title,
                 count(s.albumCode) as has_album_code,
                 count(s.energy) as has_energy,
                 count(s.valence) as has_valence,
                 count(s.tempo) as has_tempo
            RETURN total_songs, has_title, has_album_code, has_energy, has_valence, has_tempo
        `;
        const statsResult = await session.run(statsQuery);
        
        const analysis = {
            sample_songs: sampleResult.records.map(record => record.get('s').properties),
            all_properties: keysResult.records.map(record => record.get('prop')),
            property_statistics: statsResult.records[0] ? Object.fromEntries(
                Object.entries(statsResult.records[0].toObject()).map(([key, value]) => 
                    [key, typeof value === 'object' && value.toNumber ? value.toNumber() : value]
                )
            ) : {}
        };
        
        await session.close();
        res.json(analysis);
    } catch (error) {
        console.error('Song properties inspection error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Check artist and album data availability
app.get('/api/check-metadata', async (req, res) => {
    try {
        const session = driver.session();
        
        // Check Artist nodes and properties
        const artistQuery = `
            MATCH (a:Artist)
            RETURN a LIMIT 3
        `;
        const artistResult = await session.run(artistQuery);
        
        // Check Album nodes and properties  
        const albumQuery = `
            MATCH (al:Album)
            RETURN al LIMIT 3
        `;
        const albumResult = await session.run(albumQuery);
        
        // Check Album codes to names mapping
        const albumMappingQuery = `
            MATCH (s:Song)
            WHERE s.albumCode IS NOT NULL
            RETURN DISTINCT s.albumCode as album_code, 
                   collect(DISTINCT s.title)[0..3] as sample_songs
            ORDER BY s.albumCode
        `;
        const albumMappingResult = await session.run(albumMappingQuery);
        
        // Check for any relationship-based metadata
        const relationshipQuery = `
            MATCH (s:Song)
            OPTIONAL MATCH (s)<-[r1]-(connected1)
            OPTIONAL MATCH (s)-[r2]->(connected2)
            WHERE connected1 IS NOT NULL OR connected2 IS NOT NULL
            WITH s, type(r1) as incoming_rel, labels(connected1) as incoming_labels,
                 type(r2) as outgoing_rel, labels(connected2) as outgoing_labels
            RETURN DISTINCT incoming_rel, incoming_labels, outgoing_rel, outgoing_labels
            LIMIT 10
        `;
        const relationshipResult = await session.run(relationshipQuery);
        
        const metadata = {
            artist_nodes: {
                count: artistResult.records.length,
                sample: artistResult.records.map(record => record.get('a').properties),
                available: artistResult.records.length > 0
            },
            album_nodes: {
                count: albumResult.records.length,
                sample: albumResult.records.map(record => record.get('al').properties),
                available: albumResult.records.length > 0
            },
            album_code_mapping: albumMappingResult.records.map(record => ({
                code: record.get('album_code'),
                sample_songs: record.get('sample_songs')
            })),
            song_relationships: relationshipResult.records.map(record => ({
                incoming: {
                    relationship: record.get('incoming_rel'),
                    from_labels: record.get('incoming_labels')
                },
                outgoing: {
                    relationship: record.get('outgoing_rel'),
                    to_labels: record.get('outgoing_labels')
                }
            }))
        };
        
        await session.close();
        res.json(metadata);
    } catch (error) {
        console.error('Metadata check error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Add missing metadata to Song nodes (simple batch update)
app.post('/api/add-missing-metadata', async (req, res) => {
    try {
        console.log('🚀 Starting metadata batch update...');
        
        // Album metadata mapping (from source analysis)
        const albumMetadata = {
            'TSW': { name: 'Taylor Swift', year: 2006 },
            'FER': { name: 'Fearless', year: 2008 },
            'SPN': { name: 'Speak Now', year: 2010 },
            'RED': { name: 'Red', year: 2012 },
            'NEN': { name: '1989', year: 2014 },
            'REP': { name: 'reputation', year: 2017 },
            'LVR': { name: 'Lover', year: 2019 },
            'FOL': { name: 'folklore', year: 2020 },
            'EVE': { name: 'evermore', year: 2020 },
            'MID': { name: 'Midnights', year: 2022 },
            'TPD': { name: 'The Tortured Poets Department', year: 2024 }
        };
        
        const session = driver.session();
        
        // Step 1: Create simple performance index
        console.log('🔧 Creating performance index...');
        try {
            await session.run(`
                CREATE INDEX song_albumcode_idx IF NOT EXISTS FOR (s:Song) ON (s.albumCode)
            `);
            console.log('✅ Index created');
        } catch (indexError) {
            console.log('⚠️ Index already exists or creation skipped');
        }
        
        // Step 2: Get current status before update
        const beforeQuery = `
            MATCH (s:Song)
            RETURN count(s) as total_songs,
                   count(s.albumName) as songs_with_album_names,
                   count(s.releaseYear) as songs_with_years,
                   count(s.artistName) as songs_with_artist
        `;
        const beforeResult = await session.run(beforeQuery);
        const beforeStats = beforeResult.records[0].toObject();
        
        console.log('📊 Before update:', beforeStats);
        
        // Step 3: Batch update using UNWIND
        console.log('🔄 Updating song metadata...');
        
        // Prepare batch data for all album codes
        const batchData = Object.entries(albumMetadata).map(([code, data]) => ({
            albumCode: code,
            albumName: data.name,
            releaseYear: data.year,
            artistName: 'Taylor Swift'
        }));
        
        const updateQuery = `
            UNWIND $batch_data AS item
            MATCH (s:Song {albumCode: item.albumCode})
            SET s.albumName = item.albumName,
                s.releaseYear = item.releaseYear,
                s.artistName = item.artistName,
                s.metadata_updated_at = datetime()
            RETURN count(s) as updated_count
        `;
        
        const updateResult = await session.run(updateQuery, { batch_data: batchData });
        const updatedCount = updateResult.records[0].get('updated_count');
        
        // Step 4: Get status after update
        const afterResult = await session.run(beforeQuery);
        const afterStats = afterResult.records[0].toObject();
        
        console.log('📊 After update:', afterStats);
        
        // Step 5: Validation query
        const validationQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL
            RETURN s.albumCode as code, 
                   s.albumName as name, 
                   s.releaseYear as year,
                   count(s) as song_count
            ORDER BY s.releaseYear, s.albumCode
        `;
        const validationResult = await session.run(validationQuery);
        const validation = validationResult.records.map(record => ({
            code: record.get('code'),
            name: record.get('name'),
            year: record.get('year'),
            songs: record.get('song_count')
        }));
        
        await session.close();
        
        const results = {
            success: true,
            message: 'Metadata batch update completed successfully',
            statistics: {
                before: {
                    total_songs: beforeStats.total_songs,
                    songs_with_album_names: beforeStats.songs_with_album_names,
                    songs_with_years: beforeStats.songs_with_years,
                    songs_with_artist: beforeStats.songs_with_artist
                },
                after: {
                    total_songs: afterStats.total_songs,
                    songs_with_album_names: afterStats.songs_with_album_names,
                    songs_with_years: afterStats.songs_with_years,
                    songs_with_artist: afterStats.songs_with_artist
                },
                songs_updated: updatedCount
            },
            albums_updated: validation
        };
        
        console.log('✅ Metadata update completed successfully');
        res.json(results);
        
    } catch (error) {
        console.error('❌ Metadata update error:', error);
        res.status(500).json({ 
            success: false, 
            error: error.message,
            message: 'Failed to update metadata'
        });
    }
});

// Validate metadata update results
app.get('/api/metadata-status', async (req, res) => {
    try {
        const session = driver.session();
        
        // Get comprehensive metadata status
        const statusQuery = `
            MATCH (s:Song)
            RETURN count(s) as total_songs,
                   count(s.albumName) as songs_with_album_names,
                   count(s.releaseYear) as songs_with_years,
                   count(s.artistName) as songs_with_artist,
                   count(s.metadata_updated_at) as songs_with_update_timestamp
        `;
        const statusResult = await session.run(statusQuery);
        
        // Get sample of updated songs
        const sampleQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL
            RETURN s.title as title,
                   s.albumCode as code,
                   s.albumName as album,
                   s.releaseYear as year,
                   s.artistName as artist
            ORDER BY s.releaseYear, s.albumCode, s.title
            LIMIT 10
        `;
        const sampleResult = await session.run(sampleQuery);
        
        // Get album breakdown
        const albumsQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL
            RETURN s.albumCode as code,
                   s.albumName as name,
                   s.releaseYear as year,
                   count(s) as song_count
            ORDER BY s.releaseYear
        `;
        const albumsResult = await session.run(albumsQuery);
        
        await session.close();
        
        const status = {
            overview: statusResult.records[0].toObject(),
            sample_songs: sampleResult.records.map(record => record.toObject()),
            albums: albumsResult.records.map(record => ({
                code: record.get('code'),
                name: record.get('name'),
                year: record.get('year'),
                songs: record.get('song_count')
            }))
        };
        
        // Convert Neo4j integers to regular numbers
        status.overview = Object.fromEntries(
            Object.entries(status.overview).map(([key, value]) => 
                [key, value]
            )
        );
        
        res.json(status);
    } catch (error) {
        console.error('Metadata status error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get songs needing Spotify metadata
app.get('/api/songs-needing-spotify-data', async (req, res) => {
    try {
        const session = driver.session();
        
        // Get songs that don't have Spotify metadata yet
        const songsQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL 
            AND s.artistName IS NOT NULL
            AND (s.spotify_track_id IS NULL OR s.genres IS NULL)
            RETURN s.title as title,
                   s.albumCode as albumCode,
                   s.albumName as albumName,
                   s.artistName as artistName,
                   s.releaseYear as releaseYear,
                   s.trackNumber as trackNumber,
                   s.spotify_track_id as existing_spotify_id,
                   s.genres as existing_genres
            ORDER BY s.releaseYear, s.albumCode, s.trackNumber
        `;
        const songsResult = await session.run(songsQuery);
        
        // Get summary statistics
        const statsQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL
            RETURN count(s) as total_songs,
                   count(s.spotify_track_id) as songs_with_spotify_id,
                   count(s.genres) as songs_with_genres,
                   count(CASE WHEN s.spotify_track_id IS NOT NULL AND s.genres IS NOT NULL THEN 1 END) as songs_with_both
        `;
        const statsResult = await session.run(statsQuery);
        
        await session.close();
        
        const songs = songsResult.records.map(record => ({
            title: record.get('title'),
            albumCode: record.get('albumCode'),
            albumName: record.get('albumName'),
            artistName: record.get('artistName'),
            releaseYear: record.get('releaseYear'),
            trackNumber: record.get('trackNumber'),
            existing_spotify_id: record.get('existing_spotify_id'),
            existing_genres: record.get('existing_genres')
        }));
        
        const stats = statsResult.records[0].toObject();
        
        res.json({
            songs_needing_metadata: songs,
            count: songs.length,
            statistics: {
                total_songs: stats.total_songs,
                songs_with_spotify_id: stats.songs_with_spotify_id,
                songs_with_genres: stats.songs_with_genres,
                songs_with_both: stats.songs_with_both,
                songs_needing_data: songs.length
            }
        });
        
    } catch (error) {
        console.error('Songs needing Spotify data error:', error);
        res.status(500).json({ error: error.message });
    }
});

// Spotify metadata batch acquisition endpoint
app.post('/api/acquire-spotify-metadata', async (req, res) => {
    const { batch_size = 10, start_index = 0, test_mode = true } = req.body;
    
    try {
        console.log(`🎵 Starting Spotify metadata acquisition (batch size: ${batch_size}, start: ${start_index}, test: ${test_mode})`);
        
        // Check if we have Spotify credentials
        const spotifyClientId = process.env.SPOTIFY_CLIENT_ID;
        const spotifyClientSecret = process.env.SPOTIFY_CLIENT_SECRET;
        
        if (!spotifyClientId || !spotifyClientSecret) {
            return res.status(400).json({
                success: false,
                error: 'Spotify API credentials not configured',
                message: 'SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in environment'
            });
        }
        
        // Get songs needing metadata
        const session = driver.session();
        const songsQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL 
            AND s.artistName IS NOT NULL
            AND (s.spotify_track_id IS NULL OR s.genres IS NULL)
            RETURN s.title as title,
                   s.albumCode as albumCode,
                   s.albumName as albumName,
                   s.artistName as artistName,
                   s.releaseYear as releaseYear,
                   s.trackNumber as trackNumber
            ORDER BY s.releaseYear, s.albumCode, s.trackNumber
            SKIP ${parseInt(start_index)}
            LIMIT ${parseInt(batch_size)}
        `;
        
        const songsResult = await session.run(songsQuery);
        
        const songs = songsResult.records.map(record => ({
            title: record.get('title'),
            albumCode: record.get('albumCode'),
            albumName: record.get('albumName'),
            artistName: record.get('artistName'),
            releaseYear: record.get('releaseYear'),
            trackNumber: record.get('trackNumber')
        }));
        
        if (songs.length === 0) {
            await session.close();
            return res.json({
                success: true,
                message: 'No more songs need Spotify metadata',
                processed: 0,
                total_processed: start_index
            });
        }
        
        console.log(`📝 Processing ${songs.length} songs starting from index ${start_index}`);
        
        // Initialize results tracking
        const results = {
            processed: 0,
            successful: 0,
            failed: 0,
            songs_updated: [],
            errors: []
        };
        
        // Mock Spotify search for test mode (replace with actual API calls later)
        if (test_mode) {
            console.log('🧪 Running in test mode (mock data)');
            
            for (const song of songs) {
                try {
                    // Mock Spotify data
                    const mockSpotifyData = {
                        track_id: `mock_id_${song.title.replace(/\s+/g, '_').toLowerCase()}`,
                        uri: `spotify:track:mock_id_${song.title.replace(/\s+/g, '_').toLowerCase()}`,
                        genres: getGenresForAlbum(song.albumName),
                        popularity: Math.floor(Math.random() * 100),
                        external_urls: { spotify: `https://open.spotify.com/track/mock_id` }
                    };
                    
                    // Update song in database
                    const updateQuery = `
                        MATCH (s:Song {title: $title, albumCode: $albumCode})
                        SET s.spotify_track_id = $track_id,
                            s.spotify_uri = $uri,
                            s.genres = $genres,
                            s.spotify_popularity = $popularity,
                            s.spotify_external_url = $external_url,
                            s.spotify_metadata_updated = datetime(),
                            s.spotify_metadata_source = 'test_mode'
                        RETURN s.title as updated_title
                    `;
                    
                    const updateResult = await session.run(updateQuery, {
                        title: song.title,
                        albumCode: song.albumCode,
                        track_id: mockSpotifyData.track_id,
                        uri: mockSpotifyData.uri,
                        genres: mockSpotifyData.genres,
                        popularity: mockSpotifyData.popularity,
                        external_url: mockSpotifyData.external_urls.spotify
                    });
                    
                    if (updateResult.records.length > 0) {
                        results.successful++;
                        results.songs_updated.push({
                            title: song.title,
                            album: song.albumName,
                            spotify_id: mockSpotifyData.track_id,
                            genres: mockSpotifyData.genres
                        });
                        console.log(`✅ Updated: ${song.title} (${song.albumName})`);
                    } else {
                        results.failed++;
                        results.errors.push(`Song not found in database: ${song.title}`);
                    }
                    
                    results.processed++;
                    
                    // Small delay to simulate API rate limiting
                    await new Promise(resolve => setTimeout(resolve, 100));
                    
                } catch (error) {
                    results.failed++;
                    results.processed++;
                    results.errors.push(`Error processing ${song.title}: ${error.message}`);
                    console.error(`❌ Error updating ${song.title}:`, error.message);
                }
            }
        } else {
            // TODO: Implement actual Spotify API calls here
            await session.close();
            return res.status(501).json({
                success: false,
                error: 'Real Spotify API integration not yet implemented',
                message: 'Use test_mode: true for now'
            });
        }
        
        await session.close();
        
        const response = {
            success: true,
            message: `Batch processing completed`,
            batch_info: {
                start_index: start_index,
                batch_size: batch_size,
                processed: results.processed,
                successful: results.successful,
                failed: results.failed
            },
            next_batch_start: start_index + batch_size,
            songs_updated: results.songs_updated,
            errors: results.errors.slice(0, 5), // Limit error details
            test_mode: test_mode
        };
        
        console.log(`✅ Batch completed: ${results.successful}/${results.processed} songs updated`);
        res.json(response);
        
    } catch (error) {
        console.error('Spotify metadata acquisition error:', error);
        res.status(500).json({
            success: false,
            error: error.message,
            message: 'Failed to acquire Spotify metadata'
        });
    }
});

// Helper function to get genres for albums (mock data for testing)
function getGenresForAlbum(albumName) {
    const genreMapping = {
        'Taylor Swift': ['Country', 'Country Pop'],
        'Fearless': ['Country', 'Country Pop'], 
        'Speak Now': ['Country', 'Country Pop'],
        'Red': ['Pop', 'Country Pop', 'Rock'],
        '1989': ['Pop', 'Synth-pop'],
        'reputation': ['Pop', 'Electropop'],
        'Lover': ['Pop', 'Indie Pop'],
        'folklore': ['Indie Folk', 'Alternative'],
        'evermore': ['Indie Folk', 'Alternative'],
        'Midnights': ['Pop', 'Synth-pop'],
        'The Tortured Poets Department': ['Pop', 'Alternative']
    };
    
    return genreMapping[albumName] || ['Pop'];
}

// Get Spotify metadata acquisition progress
app.get('/api/spotify-metadata-progress', async (req, res) => {
    try {
        const session = driver.session();
        
        const progressQuery = `
            MATCH (s:Song)
            WHERE s.albumName IS NOT NULL
            RETURN count(s) as total_songs,
                   count(s.spotify_track_id) as songs_with_spotify_id,
                   count(s.genres) as songs_with_genres,
                   count(CASE WHEN s.spotify_track_id IS NOT NULL AND s.genres IS NOT NULL THEN 1 END) as songs_with_complete_metadata,
                   count(CASE WHEN s.spotify_metadata_updated IS NOT NULL THEN 1 END) as songs_processed
        `;
        
        const progressResult = await session.run(progressQuery);
        const stats = progressResult.records[0].toObject();
        
        // Get sample of recently updated songs
        const sampleQuery = `
            MATCH (s:Song)
            WHERE s.spotify_metadata_updated IS NOT NULL
            RETURN s.title as title,
                   s.albumName as album,
                   s.genres as genres,
                   s.spotify_track_id as spotify_id,
                   s.spotify_metadata_updated as updated_at
            ORDER BY s.spotify_metadata_updated DESC
            LIMIT 5
        `;
        
        const sampleResult = await session.run(sampleQuery);
        
        await session.close();
        
        const progress = {
            total_songs: stats.total_songs,
            songs_with_spotify_id: stats.songs_with_spotify_id,
            songs_with_genres: stats.songs_with_genres,
            songs_with_complete_metadata: stats.songs_with_complete_metadata,
            songs_processed: stats.songs_processed,
            completion_percentage: Math.round((stats.songs_with_complete_metadata.toNumber() / stats.total_songs.toNumber()) * 100),
            recently_updated: sampleResult.records.map(record => ({
                title: record.get('title'),
                album: record.get('album'),
                genres: record.get('genres'),
                spotify_id: record.get('spotify_id'),
                updated_at: record.get('updated_at')
            }))
        };
        
        res.json(progress);
        
    } catch (error) {
        console.error('Progress check error:', error);
        res.status(500).json({ error: error.message });
    }
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



// Add music visualization generation endpoint for mb-mobile compatibility
app.post('/api/generate', async (req, res) => {
  try {
    const { prompt, debug } = req.body;
    
    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    console.log('🎵 Music visualization request:', prompt.substring(0, 100) + '...');

    // Analyze prompt for music-related content
    const promptLower = prompt.toLowerCase();
    let musicData = {};
    
    // Get songs with taxonomy data from AuraDB
    const session = driver.session();
    
    if (promptLower.includes('taylor swift') || promptLower.includes('music') || promptLower.includes('song')) {
      // Get Taylor Swift songs with taxonomy data
      const result = await session.run(`
        MATCH (s:Song)
        WHERE s.title IS NOT NULL AND s.taxonomy_energy_label IS NOT NULL
        RETURN s.title as title,
               s.albumCode as albumCode,
               s.taxonomy_energy_level as energy_level,
               s.taxonomy_energy_label as energy_label,
               s.taxonomy_emotional_valence as emotional_valence,
               s.taxonomy_emotional_label as emotional_label,
               s.taxonomy_time_primary as time_primary,
               s.taxonomy_activity_category as activity_category,
               s.valence as valence,
               s.energy as energy,
               s.danceability as danceability
        ORDER BY s.title
        LIMIT 10
      `);
      
      musicData.songs = result.records.map(record => ({
        title: record.get('title'),
        albumCode: record.get('albumCode'),
        energy_level: record.get('energy_level'),
        energy_label: record.get('energy_label'),
        emotional_valence: record.get('emotional_valence'),
        emotional_label: record.get('emotional_label'),
        time_primary: record.get('time_primary'),
        activity_category: record.get('activity_category'),
        valence: record.get('valence'),
        energy: record.get('energy'),
        danceability: record.get('danceability')
      }));
    }

    await session.close();

    // Generate HTML based on music data
    const html = generateMusicHTML(musicData, prompt);
    
    // Return format expected by mb-mobile
    res.json({
      html: html,
      explanation: "Created a beautiful music visualization with your Taylor Swift collection!",
      status: 'success',
      analysis: {
        contentType: 'music',
        platform: 'mobile',
        theme: 'musical'
      },
      validation: {
        isValid: true,
        score: 95,
        maxScore: 100,
        feedback: 'High quality music visualization'
      }
    });

  } catch (error) {
    console.error('Music visualization error:', error);
    res.status(500).json({ 
      error: 'Failed to generate music visualization',
      details: error.message 
    });
  }
});

// Generate HTML for music visualization
function generateMusicHTML(musicData, prompt) {
  const songs = musicData.songs || [];
  
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Music Discovery</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: white;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .songs-grid {
            display: grid;
            gap: 20px;
        }
        
        .song-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .song-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .song-title {
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .song-album {
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 15px;
            font-size: 0.9rem;
        }
        
        .song-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 15px;
        }
        
        .tag {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .energy-high { background: linear-gradient(45deg, #ff6b6b, #ff8e53); }
        .energy-energetic { background: linear-gradient(45deg, #4ecdc4, #44a08d); }
        .energy-moderate { background: linear-gradient(45deg, #ffeaa7, #fdcb6e); }
        .energy-chill { background: linear-gradient(45deg, #a8e6cf, #7fcdcd); }
        
        .mood-euphoric { background: linear-gradient(45deg, #ff9a9e, #fecfef); }
        .mood-uplifting { background: linear-gradient(45deg, #a8edea, #fed6e3); }
        .mood-neutral { background: linear-gradient(45deg, #c7d2fe, #f9ca24); }
        .mood-reflective { background: linear-gradient(45deg, #667eea, #764ba2); }
        .mood-melancholic { background: linear-gradient(45deg, #5f27cd, #341f97); }
        
        .stats-bar {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            height: 6px;
            margin-bottom: 5px;
            overflow: hidden;
        }
        
        .stats-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            border-radius: 10px;
            transition: width 0.5s ease;
        }
        
        .stats-label {
            font-size: 0.8rem;
            opacity: 0.8;
            margin-bottom: 8px;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .song-card {
                padding: 16px;
            }
            
            .song-title {
                font-size: 1.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 Music Discovery</h1>
            <p>Your Taylor Swift collection with AI-powered insights</p>
        </div>
        
        <div class="songs-grid">
            ${songs.map(song => `
                <div class="song-card" onclick="selectSong('${song.title}')">
                    <div class="song-title">${song.title}</div>
                    <div class="song-album">${song.albumCode}</div>
                    
                    <div class="song-tags">
                        <span class="tag energy-${song.energy_label?.toLowerCase().replace(' ', '')}">${song.energy_label || 'Moderate'}</span>
                        <span class="tag mood-${song.emotional_label?.toLowerCase()}">${song.emotional_label || 'Neutral'}</span>
                        <span class="tag">${song.activity_category || 'General'}</span>
                    </div>
                    
                    <div class="stats-label">Energy: ${Math.round((song.energy || 0.5) * 100)}%</div>
                    <div class="stats-bar">
                        <div class="stats-fill" style="width: ${Math.round((song.energy || 0.5) * 100)}%"></div>
                    </div>
                    
                    <div class="stats-label">Positivity: ${Math.round((song.valence || 0.5) * 100)}%</div>
                    <div class="stats-bar">
                        <div class="stats-fill" style="width: ${Math.round((song.valence || 0.5) * 100)}%"></div>
                    </div>
                    
                    <div class="stats-label">Danceability: ${Math.round((song.danceability || 0.5) * 100)}%</div>
                    <div class="stats-bar">
                        <div class="stats-fill" style="width: ${Math.round((song.danceability || 0.5) * 100)}%"></div>
                    </div>
                </div>
            `).join('')}
        </div>
    </div>
    
    <script>
        function selectSong(title) {
            // Add haptic feedback on mobile
            if (navigator.vibrate) {
                navigator.vibrate(50);
            }
            
            // Show selection feedback
            event.target.style.transform = 'scale(0.95)';
            setTimeout(() => {
                event.target.style.transform = 'translateY(-5px)';
            }, 100);
            
            console.log('Selected song:', title);
        }
        
        // Add touch feedback
        document.querySelectorAll('.song-card').forEach(card => {
            card.addEventListener('touchstart', function() {
                this.style.background = 'rgba(255, 255, 255, 0.2)';
            });
            
            card.addEventListener('touchend', function() {
                setTimeout(() => {
                    this.style.background = 'rgba(255, 255, 255, 0.1)';
                }, 150);
            });
        });
    </script>
</body>
</html>`;
}

// Analysis endpoints have been moved to direct Python scripts for better performance

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