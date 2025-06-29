// AG-UI Backend Server for Music Besties with AuraDB Integration
const WebSocket = require('ws')
const { v4: uuidv4 } = require('uuid')
const neo4j = require('neo4j-driver')
const OpenAI = require('openai')

class MusicBestiesAGUIServer {
  constructor(httpServer) {
    this.httpServer = httpServer
    this.wss = null
    this.clients = new Map()
    this.conversations = new Map()
    
    // AuraDB Configuration
    this.neo4jDriver = null
    this.initializeAuraDB()
    
    // OpenAI Configuration
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    })
    
    this.setupWebSocketServer()
  }

  initializeAuraDB() {
    try {
      this.neo4jDriver = neo4j.driver(
        process.env.AURA_DB_URI || 'neo4j+s://your-aura-instance.databases.neo4j.io',
        neo4j.auth.basic(
          process.env.AURA_DB_USERNAME || 'neo4j',
          process.env.AURA_DB_PASSWORD || 'your-password'
        )
      )
      console.log('AuraDB connection initialized')
    } catch (error) {
      console.error('Failed to initialize AuraDB:', error)
    }
  }

  setupWebSocketServer() {
    this.wss = new WebSocket.Server({ 
      server: this.httpServer,
      path: '/agui-ws'
    })

    this.wss.on('connection', (ws, req) => {
      const clientId = uuidv4()
      this.clients.set(clientId, {
        ws: ws,
        id: clientId,
        conversations: new Set()
      })

      console.log(`AG-UI client connected: ${clientId}`)

      ws.on('message', async (data) => {
        try {
          const message = JSON.parse(data.toString())
          await this.handleClientMessage(clientId, message)
        } catch (error) {
          console.error('Error handling client message:', error)
          this.sendToClient(clientId, {
            type: 'error',
            message: 'Failed to process message'
          })
        }
      })

      ws.on('close', () => {
        console.log(`AG-UI client disconnected: ${clientId}`)
        this.clients.delete(clientId)
      })

      // Send welcome message
      this.sendToClient(clientId, {
        type: 'connection',
        status: 'connected',
        message: 'Welcome to Music Besties AG-UI!'
      })
    })
  }

  async handleClientMessage(clientId, message) {
    console.log('Processing message:', JSON.stringify(message, null, 2))
    const { type, conversationId, content, context } = message

    // Safety check for content
    if (!content && message.message) {
      console.log('Using message.message as content')
      message.content = message.message
    }

    switch (type) {
      case 'user_message':
        await this.handleUserMessage(clientId, conversationId || uuidv4(), content || message.message, context)
        break
        
      case 'start_conversation':
        await this.startArtistConversation(clientId, context.artist)
        break
        
      case 'get_insights':
        await this.getArtistInsights(clientId, context.artist, context.insightType)
        break
        
      default:
        this.sendToClient(clientId, {
          type: 'error',
          message: `Unknown message type: ${type}`
        })
    }
  }

  async handleUserMessage(clientId, conversationId, message, context) {
    try {
      // Store conversation if not exists
      if (!this.conversations.has(conversationId)) {
        this.conversations.set(conversationId, {
          id: conversationId,
          clientId: clientId,
          artist: context.currentArtist,
          messages: [],
          startTime: new Date().toISOString()
        })
      }

      const conversation = this.conversations.get(conversationId)
      conversation.messages.push({
        type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      })

      // Generate AI response based on artist and AuraDB data
      const aiResponse = await this.generateAIResponse(message, context)
      
      conversation.messages.push({
        type: 'ai',
        content: aiResponse,
        timestamp: new Date().toISOString()
      })

      // Send AI response to client
      this.sendToClient(clientId, {
        type: 'ai_response',
        conversationId: conversationId,
        content: aiResponse,
        timestamp: new Date().toISOString(),
        streaming: false
      })

      // Check if we should generate additional insights or components
      await this.checkForAdditionalContent(clientId, conversationId, message, context)

    } catch (error) {
      console.error('Error handling user message:', error)
      this.sendToClient(clientId, {
        type: 'error',
        message: 'Failed to generate response'
      })
    }
  }

  async generateAIResponse(userMessage, context) {
    try {
      const artist = context.currentArtist
      const userIntent = context.userIntent
      
      // Get relevant data from AuraDB
      const artistData = await this.getArtistDataFromAuraDB(artist.name)
      
      // Create system prompt for Music Bestie personality
      const systemPrompt = `You are a Music Bestie - an enthusiastic, knowledgeable AI companion who shares the user's deep obsession with their favorite artists. Your role is to:

1. Be genuinely excited about the artist and their work
2. Provide deep, insightful analysis that goes beyond surface-level facts
3. Share lesser-known details and connections
4. Ask engaging follow-up questions to deepen the conversation
5. Relate to the user's passion and validate their obsession
6. Use a warm, friendly tone like talking to your best friend

Current artist: ${artist.name}
User intent: ${userIntent}
Available data: ${JSON.stringify(artistData, null, 2)}

Respond as if you're the user's best friend who shares their obsession with this artist.`

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage }
        ],
        max_tokens: 300,
        temperature: 0.8
      })

      return completion.choices[0].message.content
    } catch (error) {
      console.error('Error generating AI response:', error)
      throw error // Let the calling function handle the error
    }
  }

  async getArtistDataFromAuraDB(artistName) {
    if (!this.neo4jDriver) {
      console.log('AuraDB not configured, using sample data')
      return this.getSampleArtistData(artistName)
    }

    const session = this.neo4jDriver.session()
    
    try {
      // Query for artist information and relationships
      const result = await session.run(`
        MATCH (artist:Artist {name: $artistName})
        OPTIONAL MATCH (artist)-[:RELEASED]->(album:Album)
        OPTIONAL MATCH (artist)-[:INFLUENCED_BY]->(influence:Artist)
        OPTIONAL MATCH (artist)-[:COLLABORATED_WITH]->(collab:Artist)
        RETURN artist, 
               collect(distinct album) as albums,
               collect(distinct influence) as influences,
               collect(distinct collab) as collaborations
      `, { artistName })

      if (result.records.length > 0) {
        const record = result.records[0]
        return {
          artist: record.get('artist').properties,
          albums: record.get('albums').map(album => album.properties),
          influences: record.get('influences').map(inf => inf.properties),
          collaborations: record.get('collaborations').map(collab => collab.properties)
        }
      }
      
      return this.getSampleArtistData(artistName)
    } catch (error) {
      console.error('Error querying AuraDB:', error)
      return this.getSampleArtistData(artistName)
    } finally {
      await session.close()
    }
  }

  getSampleArtistData(artistName) {
    // Sample data for development/testing
    return {
      artist: { name: artistName, genre: 'Pop' },
      albums: [],
      influences: [],
      collaborations: []
    }
  }

  async checkForAdditionalContent(clientId, conversationId, userMessage, context) {
    // Safety check for userMessage
    if (!userMessage || typeof userMessage !== 'string') {
      console.log('Warning: userMessage is invalid:', userMessage)
      return
    }
    
    const intent = context.userIntent
    
    // Generate additional insights based on user intent
    if (['analyze', 'explore', 'deep-dive'].includes(intent)) {
      const insights = await this.generateDeepInsights(context.currentArtist)
      
      this.sendToClient(clientId, {
        type: 'artist_insight',
        conversationId: conversationId,
        artist: context.currentArtist.name,
        insight: insights,
        insightType: intent,
        metadata: {
          generatedAt: new Date().toISOString(),
          confidence: 0.85
        }
      })
    }
    
    // Generate visualization components for certain queries
    if (userMessage.toLowerCase().includes('chart') || userMessage.toLowerCase().includes('timeline')) {
      const vizData = await this.generateVisualizationData('timeline', context)
      
      this.sendToClient(clientId, {
        type: 'generated_component',
        component: 'TimelineChart',
        props: vizData,
        context: {
          artist: context.currentArtist.name,
          type: 'evolution'
        }
      })
    }
  }

  async generateDeepInsights(artist) {
    return {
      themes: ['Musical evolution', 'Artistic influences', 'Genre experimentation'],
      connections: ['Contemporary artists', 'Musical predecessors', 'Production collaborators'],
      hiddenGems: ['Deep cuts', 'B-sides', 'Unreleased tracks']
    }
  }

  sendToClient(clientId, data) {
    const client = this.clients.get(clientId)
    if (client && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(JSON.stringify(data))
    }
  }

  getHTTPRoutes() {
    const express = require('express')
    const router = express.Router()

    // Health check for AG-UI
    router.get('/health', (req, res) => {
      res.json({
        status: 'AG-UI Server Running',
        clients: this.clients.size,
        conversations: this.conversations.size,
        auradb: this.neo4jDriver ? 'connected' : 'not configured',
        openai: process.env.OPENAI_API_KEY ? 'configured' : 'not configured'
      })
    })

    // Get conversation history
    router.get('/conversations/:id', (req, res) => {
      const conversation = this.conversations.get(req.params.id)
      if (conversation) {
        res.json(conversation)
      } else {
        res.status(404).json({ error: 'Conversation not found' })
      }
    })

    // Start new conversation
    router.post('/conversations', (req, res) => {
      const { artist } = req.body
      const conversationId = uuidv4()
      
      this.conversations.set(conversationId, {
        id: conversationId,
        artist: artist,
        messages: [],
        startTime: new Date().toISOString()
      })

      res.json({ conversationId, artist: artist.name })
    })

    return router
  }

  async generateVisualizationData(type, context) {
    // Generate data for visualization components
    const artist = context.currentArtist
    
    switch (type) {
      case 'timeline':
        return {
          title: `${artist.name} Career Timeline`,
          data: artist.discography?.map(album => ({
            year: album.year,
            album: album.album,
            popularity: album.popularity
          })) || []
        }
      default:
        return { title: 'Visualization', data: [] }
    }
  }

  async shutdown() {
    if (this.neo4jDriver) {
      await this.neo4jDriver.close()
    }
    if (this.wss) {
      this.wss.close()
    }
  }
}

module.exports = MusicBestiesAGUIServer 