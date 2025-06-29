// AG-UI Service for Music Besties Conversational Interface
// This service replaces the traditional API service with a conversational AI interface

class MusicBestiesAGUI {
  constructor() {
    this.isConnected = false
    this.conversations = new Map()
    this.currentArtist = null
    this.eventListeners = new Map()
    this.wsConnection = null
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:3001'
  }

  async initialize() {
    try {
      // Initialize WebSocket connection for real-time communication
      await this.connectWebSocket()
      
      // Test connection
      const health = await this.checkHealth()
      this.isConnected = health.success
      
      return { success: true, message: 'AG-UI initialized successfully' }
    } catch (error) {
      console.error('AG-UI initialization failed:', error)
      return { success: false, error: error.message }
    }
  }

  async connectWebSocket() {
    return new Promise((resolve, reject) => {
      const wsUrl = this.baseURL.replace('http', 'ws') + '/agui-ws'
      this.wsConnection = new WebSocket(wsUrl)

      this.wsConnection.onopen = () => {
        console.log('AG-UI WebSocket connected')
        this.isConnected = true
        resolve()
      }

      this.wsConnection.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleIncomingMessage(data)
      }

      this.wsConnection.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      this.wsConnection.onclose = () => {
        this.isConnected = false
        this.notifyListeners('connection', { status: 'disconnected' })
      }
    })
  }

  // Start a conversation about an artist
  async startArtistConversation(artist) {
    this.currentArtist = artist
    
    const conversationId = `artist-${artist.id}-${Date.now()}`
    
    try {
      const conversation = {
        id: conversationId,
        artist: artist,
        startTime: new Date().toISOString(),
        messages: [],
        context: {
          conversationType: 'deep-dive',
          goal: 'explore-artistic-obsession',
          userIntent: 'deepen-understanding'
        }
      }

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
      const messageData = {
        type: 'user_message',
        conversationId: targetConversation,
        message: message,
        context: {
          currentArtist: this.currentArtist,
          timestamp: new Date().toISOString(),
          userIntent: this.classifyUserIntent(message)
        }
      }

      // Send via WebSocket for real-time response
      if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
        this.wsConnection.send(JSON.stringify(messageData))
      } else {
        // Fallback to HTTP request
        return await this.httpRequest('/agui/message', {
          method: 'POST',
          body: JSON.stringify(messageData)
        })
      }

      return { success: true, messageId: Date.now().toString() }
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
      'deep-cuts': `What are some hidden gems in ${artist.name}'s catalog that deserve more attention?`,
      'lyrics': `Let's analyze the lyrical genius of ${artist.name} - what makes their words so powerful?`,
      'production': `Walk me through ${artist.name}'s approach to production and sound design`,
      'collaborations': `Tell me about ${artist.name}'s most meaningful collaborations and what they reveal`
    }

    return await this.sendMessage(queries[insightType] || queries.general)
  }

  // Request dynamic visualizations based on conversation
  async requestVisualization(type, context = {}) {
    try {
      const visualizationData = {
        type: 'generate_visualization',
        visualizationType: type,
        context: {
          ...context,
          artist: this.currentArtist,
          conversationContext: this.getCurrentConversationContext()
        }
      }

      return await this.httpRequest('/agui/visualization', {
        method: 'POST',
        body: JSON.stringify(visualizationData)
      })
    } catch (error) {
      console.error('Failed to generate visualization:', error)
      throw error
    }
  }

  // Handle incoming WebSocket messages
  handleIncomingMessage(data) {
    switch (data.type) {
      case 'ai_response':
        this.notifyListeners('message', {
          type: 'ai',
          content: data.content,
          conversationId: data.conversationId,
          timestamp: data.timestamp,
          streaming: data.streaming || false
        })
        break
        
      case 'generated_component':
        this.notifyListeners('component', {
          component: data.component,
          props: data.props,
          context: data.context
        })
        break
        
      case 'context_update':
        this.notifyListeners('context', data.context)
        break
        
      case 'artist_insight':
        this.notifyListeners('insight', {
          artist: data.artist,
          insight: data.insight,
          type: data.insightType,
          metadata: data.metadata
        })
        break
    }
  }

  // Classify user intent for better responses
  classifyUserIntent(message) {
    const intents = {
      'explore': ['tell me', 'show me', 'explore', 'discover', 'what about'],
      'compare': ['compare', 'versus', 'vs', 'difference', 'similar', 'like'],
      'analyze': ['analyze', 'breakdown', 'explain', 'why', 'how', 'what makes'],
      'recommend': ['recommend', 'suggest', 'what should', 'next', 'other'],
      'discuss': ['think', 'opinion', 'feel', 'discuss', 'talk about'],
      'deep-dive': ['obsessed', 'love', 'favorite', 'best', 'genius', 'masterpiece'],
      'personal': ['my', 'i feel', 'reminds me', 'makes me', 'when i listen']
    }

    const lowerMessage = message.toLowerCase()
    
    for (const [intent, keywords] of Object.entries(intents)) {
      if (keywords.some(keyword => lowerMessage.includes(keyword))) {
        return intent
      }
    }
    
    return 'general'
  }

  // HTTP request helper
  async httpRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('HTTP request failed:', error)
      throw error
    }
  }

  // Health check
  async checkHealth() {
    try {
      const response = await this.httpRequest('/health')
      return { success: true, ...response }
    } catch (error) {
      return { success: false, error: error.message }
    }
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

  // Get conversation history
  getConversationHistory(conversationId = null) {
    const targetId = conversationId || this.getCurrentConversationId()
    if (targetId && this.conversations.has(targetId)) {
      return this.conversations.get(targetId).messages
    }
    return []
  }

  // Cleanup
  async disconnect() {
    if (this.wsConnection) {
      this.wsConnection.close()
      this.wsConnection = null
    }
    this.isConnected = false
  }
}

export default new MusicBestiesAGUI() 