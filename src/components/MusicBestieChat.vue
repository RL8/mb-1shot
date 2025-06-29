<template>
  <div class="music-bestie-chat">
    <!-- Chat Header -->
    <div class="chat-header">
      <div class="bestie-info">
        <span class="bestie-avatar">🎵</span>
        <div class="bestie-details">
          <h3>Your Music Bestie</h3>
          <p v-if="currentArtist">Obsessing over {{ currentArtist.name }} {{ currentArtist.emoji }}</p>
          <p v-else>Ready to dive deep into your favorite artists</p>
        </div>
      </div>
      <div class="connection-indicator" :class="{ connected: isConnected }">
        <span v-if="isConnected">🟢</span>
        <span v-else>🔴</span>
      </div>
    </div>

    <!-- Chat Messages -->
    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="message in messages" 
        :key="message.id"
        class="message"
        :class="{ 'user-message': message.type === 'user', 'ai-message': message.type === 'ai' }"
      >
        <div class="message-avatar">
          <span v-if="message.type === 'user'">👤</span>
          <span v-else>🎵</span>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="isTyping" class="message ai-message typing">
        <div class="message-avatar">
          <span>🎵</span>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions" v-if="currentArtist && !isTyping">
      <button 
        v-for="action in quickActions" 
        :key="action.id"
        @click="sendQuickAction(action)"
        class="quick-action-btn"
      >
        {{ action.emoji }} {{ action.text }}
      </button>
    </div>

    <!-- Chat Input -->
    <div class="chat-input-container">
      <div class="chat-input-wrapper">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          @focus="scrollToBottom"
          placeholder="Share your thoughts about this artist..."
          class="chat-input"
          :disabled="isTyping"
        />
        <button 
          @click="sendMessage"
          :disabled="!inputMessage.trim() || isTyping"
          class="send-btn"
        >
          <span v-if="isTyping">⏳</span>
          <span v-else>🚀</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import aguiService from '../services/agui.js'

export default {
  name: 'MusicBestieChat',
  props: {
    artist: {
      type: Object,
      default: null
    }
  },
  emits: ['artist-changed', 'insight-generated'],
  setup(props, { emit }) {
    const messagesContainer = ref(null)
    const inputMessage = ref('')
    const isConnected = ref(false)
    const isTyping = ref(false)
    const currentArtist = ref(props.artist)
    const conversationId = ref(null)
    
    const messages = ref([])
    
    const quickActions = ref([
      { id: 1, emoji: '🎭', text: 'Creative Evolution', action: 'evolution' },
      { id: 2, emoji: '🌟', text: 'Hidden Gems', action: 'deep-cuts' },
      { id: 3, emoji: '💭', text: 'Lyrical Themes', action: 'themes' },
      { id: 4, emoji: '🤝', text: 'Collaborations', action: 'collaborations' },
      { id: 5, emoji: '🎹', text: 'Production Style', action: 'production' },
      { id: 6, emoji: '🔗', text: 'Influences', action: 'influences' }
    ])

    // Initialize chat
    onMounted(async () => {
      await initializeChat()
      setupEventListeners()
    })

    onUnmounted(() => {
      cleanup()
    })

    // Watch for artist changes
    watch(() => props.artist, (newArtist) => {
      if (newArtist && newArtist.id !== currentArtist.value?.id) {
        startArtistConversation(newArtist)
      }
    })

    const initializeChat = async () => {
      try {
        const result = await aguiService.initialize()
        isConnected.value = result.success
        
        if (result.success) {
          addSystemMessage('Hey there! I\'m your Music Bestie 🎵 Ready to dive deep into your favorite artists?')
          
          if (props.artist) {
            await startArtistConversation(props.artist)
          }
        } else {
          addSystemMessage('Having trouble connecting to your Music Bestie. Some features may be limited.')
        }
      } catch (error) {
        console.error('Chat initialization failed:', error)
        addSystemMessage('Oops! Something went wrong. Let\'s try again.')
      }
    }

    const setupEventListeners = () => {
      aguiService.on('message', handleIncomingMessage)
      aguiService.on('insight', handleArtistInsight)
      aguiService.on('component', handleGeneratedComponent)
      aguiService.on('connection', handleConnectionChange)
    }

    const startArtistConversation = async (artist) => {
      currentArtist.value = artist
      
      try {
        const result = await aguiService.startArtistConversation(artist)
        
        if (result.success) {
          conversationId.value = result.conversationId
          addSystemMessage(`Let's explore ${artist.name} together! ${artist.emoji}`)
          
          // Send initial AI message
          setTimeout(() => {
            addAIMessage(
              `I'm so excited to talk about ${artist.name}! They're absolutely fascinating. What aspect of their artistry are you most obsessed with right now?`
            )
          }, 1000)
        }
      } catch (error) {
        console.error('Failed to start artist conversation:', error)
        addSystemMessage('Had trouble starting the conversation. Let\'s try chatting anyway!')
      }
    }

    const sendMessage = async () => {
      if (!inputMessage.value.trim() || isTyping.value) return

      const message = inputMessage.value.trim()
      inputMessage.value = ''
      
      // Add user message immediately
      addUserMessage(message)
      
      // Show typing indicator
      isTyping.value = true
      
      try {
        await aguiService.sendMessage(message, conversationId.value)
        
        // Simulate AI response (in real implementation, this comes via WebSocket)
        setTimeout(() => {
          addAIMessage(generateAIResponse(message))
          isTyping.value = false
        }, 2000)
        
      } catch (error) {
        console.error('Failed to send message:', error)
        addSystemMessage('Sorry, I didn\'t catch that. Can you try again?')
        isTyping.value = false
      }
    }

    const sendQuickAction = async (action) => {
      if (!currentArtist.value) return
      
      try {
        isTyping.value = true
        addUserMessage(`${action.emoji} ${action.text}`)
        
        await aguiService.getArtistInsights(currentArtist.value, action.action)
        
        // Simulate response
        setTimeout(() => {
          addAIMessage(generateInsightResponse(action.action))
          isTyping.value = false
        }, 2500)
        
      } catch (error) {
        console.error('Failed to send quick action:', error)
        isTyping.value = false
      }
    }

    // Message handling
    const addUserMessage = (content) => {
      messages.value.push({
        id: Date.now(),
        type: 'user',
        content: content,
        timestamp: new Date().toISOString()
      })
      scrollToBottom()
    }

    const addAIMessage = (content) => {
      messages.value.push({
        id: Date.now(),
        type: 'ai',
        content: content,
        timestamp: new Date().toISOString()
      })
      scrollToBottom()
    }

    const addSystemMessage = (content) => {
      messages.value.push({
        id: Date.now(),
        type: 'system',
        content: content,
        timestamp: new Date().toISOString()
      })
      scrollToBottom()
    }

    // Event handlers
    const handleIncomingMessage = (data) => {
      if (data.type === 'ai') {
        addAIMessage(data.content)
        isTyping.value = false
      }
    }

    const handleArtistInsight = (data) => {
      emit('insight-generated', data)
    }

    const handleGeneratedComponent = (data) => {
      // Handle dynamic UI components
      console.log('Generated component:', data)
    }

    const handleConnectionChange = (data) => {
      isConnected.value = data.status === 'connected'
    }

    // Utility functions
    const formatMessage = (content) => {
      // Simple formatting for now
      return content.replace(/\n/g, '<br>')
    }

    const formatTime = (timestamp) => {
      return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    }

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
        }
      })
    }

    // Temporary AI response generation (replace with real AG-UI responses)
    const generateAIResponse = (userMessage) => {
      const responses = [
        `That's such a great point about ${currentArtist.value?.name}! Their artistry really shines through in ways that most people don't notice.`,
        `I love how passionate you are! ${currentArtist.value?.name} has this incredible ability to connect with fans on such a deep level.`,
        `You're absolutely right! There's so much depth to explore in ${currentArtist.value?.name}'s work. What drew you to them initially?`,
        `Fascinating perspective! ${currentArtist.value?.name} really does have a unique approach that sets them apart from other artists.`
      ]
      return responses[Math.floor(Math.random() * responses.length)]
    }

    const generateInsightResponse = (actionType) => {
      const artist = currentArtist.value
      const insights = {
        'evolution': `${artist.name}'s evolution is absolutely fascinating! From their early ${artist.discography[0]?.genre} roots to their current sound, you can hear how they've grown as an artist while staying true to their core identity.`,
        'deep-cuts': `Oh, you want the hidden gems? ${artist.name} has some incredible deep cuts that deserve way more attention! Let me tell you about some tracks that really showcase their range...`,
        'themes': `The recurring themes in ${artist.name}'s work are so telling! You can see patterns of growth, love, loss, and self-discovery woven throughout their entire catalog.`,
        'collaborations': `${artist.name}'s collaborations reveal so much about their artistic vision! They choose partners who complement and challenge them in the best ways.`,
        'production': `${artist.name}'s production style is so distinctive! They have this incredible ear for creating atmosphere and emotion through sound design.`,
        'influences': `The influences that shaped ${artist.name} are so diverse and interesting! You can hear elements from various genres and eras in their work.`
      }
      return insights[actionType] || insights['evolution']
    }

    const cleanup = () => {
      aguiService.off('message', handleIncomingMessage)
      aguiService.off('insight', handleArtistInsight)
      aguiService.off('component', handleGeneratedComponent)
      aguiService.off('connection', handleConnectionChange)
    }

    return {
      messagesContainer,
      inputMessage,
      isConnected,
      isTyping,
      currentArtist,
      messages,
      quickActions,
      sendMessage,
      sendQuickAction,
      formatMessage,
      formatTime,
      scrollToBottom
    }
  }
}
</script>

<style scoped>
.music-bestie-chat {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.chat-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.bestie-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bestie-avatar {
  font-size: 2rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bestie-details h3 {
  margin: 0;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
}

.bestie-details p {
  margin: 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.connection-indicator {
  padding: 0.5rem;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  animation: slideIn 0.3s ease-out;
}

.message-avatar {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  max-width: 80%;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  text-align: right;
}

.user-message .message-avatar {
  background: rgba(255, 255, 255, 0.2);
}

.message-text {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  color: white;
  line-height: 1.4;
  backdrop-filter: blur(10px);
  word-wrap: break-word;
}

.user-message .message-text {
  background: rgba(255, 255, 255, 0.2);
}

.message-time {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
}

.typing-indicator {
  display: flex;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  backdrop-filter: blur(10px);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

.quick-actions {
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-action-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.quick-action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.chat-input-container {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.chat-input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.chat-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1.5rem;
  padding: 0.75rem 1rem;
  color: white;
  font-size: 1rem;
  backdrop-filter: blur(10px);
  outline: none;
  transition: all 0.2s ease;
}

.chat-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.chat-input:focus {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
}

.send-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1.2rem;
  backdrop-filter: blur(10px);
}

.send-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .chat-messages {
    padding: 0.75rem;
  }
  
  .quick-actions {
    padding: 0.75rem;
  }
  
  .chat-input-container {
    padding: 0.75rem;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style> 