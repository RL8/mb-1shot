<template>
  <div class="mobile-app">
    <!-- Mobile header -->
    <header class="mobile-header">
      <div class="header-content">
        <h1>Mobile Vue App</h1>
        <div class="connection-status" :class="{ connected: backendConnected, loading: loading }">
          <span v-if="loading">⏳</span>
          <span v-else-if="backendConnected">🟢</span>
          <span v-else>🔴</span>
        </div>
      </div>
      <button class="menu-btn" @click="toggleMenu">☰</button>
    </header>

    <!-- Main content area -->
    <main class="mobile-main">
      <div class="content-card">
        <h2>Welcome to Your Mobile App</h2>
        <p>This app is designed exclusively for mobile devices with touch-optimized interactions.</p>
        
        <div class="status-info">
          <p v-if="loading" class="status-text loading">
            🔄 Loading app data...
          </p>
          <p v-else-if="backendConnected" class="status-text connected">
            ✅ Connected to backend API
          </p>
          <p v-else class="status-text offline">
            ⚠️ Running in offline mode
          </p>
        </div>
        
        <div class="action-buttons">
          <button class="primary-btn" @click="handleAction('primary')">
            Primary Action
          </button>
          <button class="secondary-btn" @click="handleAction('secondary')">
            Secondary Action
          </button>
        </div>

        <div class="feature-list">
          <div v-if="loading" class="loading-features">
            <div class="loading-item" v-for="n in 3" :key="n">
              <div class="loading-icon"></div>
              <div class="loading-text">
                <div class="loading-line"></div>
                <div class="loading-line short"></div>
              </div>
            </div>
          </div>
          <div v-else class="feature-item" v-for="feature in features" :key="feature.id" @click="selectFeature(feature)">
            <div class="feature-icon">{{ feature.icon }}</div>
            <div class="feature-text">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
              <small v-if="feature.details" class="feature-details">{{ feature.details }}</small>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Mobile navigation menu -->
    <nav class="mobile-nav" :class="{ active: menuOpen }">
      <ul>
        <li><a href="#" @click="navigate('home')">🏠 Home</a></li>
        <li><a href="#" @click="navigate('profile')">👤 Profile</a></li>
        <li><a href="#" @click="navigate('settings')">⚙️ Settings</a></li>
        <li><a href="#" @click="navigate('help')">❓ Help</a></li>
      </ul>
    </nav>

    <!-- Toast notification -->
    <div class="toast" :class="{ show: toast.show }">
      {{ toast.message }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import apiService from './services/api.js'

export default {
  name: 'App',
  setup() {
    const menuOpen = ref(false)
    const loading = ref(true)
    const backendConnected = ref(false)
    const toast = reactive({
      show: false,
      message: ''
    })

    const features = ref([])

    // Initialize app and load data from backend
    onMounted(async () => {
      await initializeApp()
    })

    const initializeApp = async () => {
      try {
        // Check backend health
        const health = await apiService.checkHealth()
        backendConnected.value = health.status === 'OK'
        
        // Load features from backend
        const featuresData = await apiService.getFeatures()
        features.value = featuresData
        
        // Track app startup
        await apiService.trackEvent('app_start', {
          timestamp: new Date().toISOString(),
          userAgent: navigator.userAgent
        })
        
        showToast('🚀 Connected to backend!')
      } catch (error) {
        console.error('Failed to connect to backend:', error)
        backendConnected.value = false
        
        // Fallback to local data
        features.value = [
          {
            id: 1,
            icon: '📱',
            title: 'Mobile First',
            description: 'Optimized for touch interactions',
            details: 'Built specifically for mobile devices'
          },
          {
            id: 2,
            icon: '⚡',
            title: 'Fast Loading',
            description: 'Built with Vite for speed',
            details: 'Lightning-fast development builds'
          },
          {
            id: 3,
            icon: '🎨',
            title: 'Modern UI',
            description: 'Clean and responsive design',
            details: 'Contemporary design patterns'
          }
        ]
        
        showToast('⚠️ Using offline mode')
      } finally {
        loading.value = false
      }
    }

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value
      
      // Track menu interaction
      if (backendConnected.value) {
        apiService.trackEvent('menu_toggle', { opened: menuOpen.value })
      }
    }

    const handleAction = async (type) => {
      showToast(`Processing ${type} action...`)
      
      try {
        if (backendConnected.value) {
          const response = await apiService.sendAction(type, {
            timestamp: new Date().toISOString(),
            source: 'mobile_app'
          })
          
          if (response.success) {
            showToast(`✅ ${response.message}`)
          }
        } else {
          showToast(`${type} action triggered (offline)`)
        }
      } catch (error) {
        console.error('Action failed:', error)
        showToast(`❌ ${type} action failed`)
      }
    }

    const selectFeature = async (feature) => {
      showToast(`Selected: ${feature.title}`)
      
      // Track feature selection
      if (backendConnected.value) {
        try {
          await apiService.trackEvent('feature_selected', {
            featureId: feature.id,
            featureTitle: feature.title
          })
        } catch (error) {
          console.error('Failed to track feature selection:', error)
        }
      }
    }

    const navigate = (section) => {
      menuOpen.value = false
      showToast(`Navigating to ${section}`)
      
      // Track navigation
      if (backendConnected.value) {
        apiService.trackEvent('navigation', { section })
      }
    }

    const showToast = (message) => {
      toast.message = message
      toast.show = true
      setTimeout(() => {
        toast.show = false
      }, 3000)
    }

    return {
      menuOpen,
      loading,
      backendConnected,
      toast,
      features,
      toggleMenu,
      handleAction,
      selectFeature,
      navigate
    }
  }
}
</script> 