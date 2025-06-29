// AG-UI Service for Music Besties Conversational Interface
import { AGUIClient } from '@ag-ui/core'

class MusicBestiesAGUI {
  constructor() {
    this.client = null
    this.isConnected = false
    this.conversations = new Map()
    this.currentArtist = null
    this.eventListeners = new Map()
  }

  async initialize() {
    try {
      this.client = new AGUIClient({
        apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:3001',
        enableStreaming: true,
        enableRealTimeSync: true,
        // Music Besties specific configuration
        context: {
          appType: 'music-besties',
          userRole: 'music-enthusiast',
          conversationStyle: 'deep-dive',
          focusArea: 'single-artist-obsession'
        }
      })

      // Connect to AG-UI backend
      await this.client.connect()
      this.isConnected = true
      
      // Set up event listeners
      this.setupEventListeners()
      
      return { success: true, message: 'AG-UI initialized successfully' }
    } catch (error) {
      console.error('AG-UI initialization failed:', error)
      return { success: false, error: error.message }
    }
  }

  setupEventListeners() {
    // Handle streaming responses
    this.client.on('message', (data) => {
      this.handleStreamingMessage(data)
    })

    // Handle generated UI components
    this.client.on('component', (component) => {
      this.handleGeneratedComponent(component)
    })

    // Handle context updates
    this.client.on('context', (context) => {
      this.handleContextUpdate(context)
    })

    // Handle connection status
    this.client.on('connect', () => {
      this.isConnected = true
      this.notifyListeners('connection', { status: 'connected' })
    })

    this.client.on('disconnect', () => {
      this.isConnected = false
      this.notifyListeners('connection', { status: 'disconnected' })
    })
  }

  // Start a conversation about an artist
  async startArtistConversation(artist) {
    this.currentArtist = artist
    
    const conversationId = `artist-${artist.id}-${Date.now()}`
    
    try {
      const conversation = await this.client.createConversation({
        id: conversationId,
        context: {
          artist: artist,
          conversationType: 'deep-dive',
          goal: 'explore-artistic-obsession',
          userIntent: 'deepen-understanding',
          dataSource: 'auradb'
        }
      })

      this.conversations.set(conversationId, conversation)
      
      // Send initial message to start the conversation
      await this.sendMessage(
        `I'm absolutely obsessed with ${artist.name}! Let's dive deep into their artistry together. What fascinating insights can you share about their creative evolution?`,
        conversationId
      )
      
      return { success: true, conversationId, artist: artist.name }
    } catch (error) {
      console.error('Failed to start artist conversation:', error)
      return { success: false, error: error.message }
    }
  }

  // Send a message to the AI bestie
  async sendMessage(message, conversationId = null) {
    if (!this.isConnected) {
      throw new Error('AG-UI not connected')
    }

    const targetConversation = conversationId || this.getCurrentConversationId()
    
    try {
      const response = await this.client.sendMessage({
        conversationId: targetConversation,
        message: message,
        context: {
          currentArtist: this.currentArtist,
          timestamp: new Date().toISOString(),
          userIntent: this.classifyUserIntent(message)
        }
      })

      return response
    } catch (error) {
      console.error('Failed to send message:', error)
      throw error
    }
  }

  // Ask for specific insights about an artist
  async getArtistInsights(artist, insightType = 'general') {
    const queries = {
      'general': `Tell me something fascinating about ${artist.name} that most fans don't know`,
      'evolution': `How has ${artist.name}'s artistic style evolved throughout their career?`,
      'influences': `What artists and experiences have shaped ${artist.name}'s unique sound?`,
      'themes': `What are the recurring themes in ${artist.name}'s work that reveal their inner world?`,
      'connections': `How does ${artist.name} connect to other artists in the music ecosystem?`,
      'deep-cuts': `What are some hidden gems in ${artist.name}'s catalog that deserve more attention?`
    }

    return await this.sendMessage(queries[insightType] || queries.general)
  }

  // Get dynamic visualizations based on conversation
  async requestVisualization(type, context = {}) {
    try {
      const response = await this.client.generateComponent({
        type: 'visualization',
        subtype: type,
        context: {
          ...context,
          artist: this.currentArtist,
          conversationContext: this.getCurrentConversationContext()
        }
      })

      return response
    } catch (error) {
      console.error('Failed to generate visualization:', error)
      throw error
    }
  }

  // Classify user intent for better responses
  classifyUserIntent(message) {
    const intents = {
      'explore': ['tell me', 'show me', 'explore', 'discover'],
      'compare': ['compare', 'versus', 'vs', 'difference', 'similar'],
      'analyze': ['analyze', 'breakdown', 'explain', 'why', 'how'],
      'recommend': ['recommend', 'suggest', 'what should', 'next'],
      'discuss': ['think', 'opinion', 'feel', 'discuss', 'talk about']
    }

    const lowerMessage = message.toLowerCase()
    
    for (const [intent, keywords] of Object.entries(intents)) {
      if (keywords.some(keyword => lowerMessage.includes(keyword))) {
        return intent
      }
    }
    
    return 'general'
  }

  // Handle streaming messages from AI
  handleStreamingMessage(data) {
    this.notifyListeners('message', data)
  }

  // Handle generated UI components
  handleGeneratedComponent(component) {
    this.notifyListeners('component', component)
  }

  // Handle context updates
  handleContextUpdate(context) {
    this.notifyListeners('context', context)
  }

  // Event listener management
  on(event, callback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, [])
    }
    this.eventListeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.eventListeners.has(event)) {
      const listeners = this.eventListeners.get(event)
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  notifyListeners(event, data) {
    if (this.eventListeners.has(event)) {
      this.eventListeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Event listener error:', error)
        }
      })
    }
  }

  // Utility methods
  getCurrentConversationId() {
    const conversations = Array.from(this.conversations.keys())
    return conversations[conversations.length - 1] || null
  }

  getCurrentConversationContext() {
    const conversationId = this.getCurrentConversationId()
    if (conversationId && this.conversations.has(conversationId)) {
      return this.conversations.get(conversationId).context
    }
    return null
  }

  // Cleanup
  async disconnect() {
    if (this.client) {
      await this.client.disconnect()
      this.isConnected = false
    }
  }
}

export default new MusicBestiesAGUI() 