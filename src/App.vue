<template>
  <div class="mobile-app">
    <!-- Mobile header -->
    <header class="mobile-header">
      <h1>Mobile Vue App</h1>
      <button class="menu-btn" @click="toggleMenu">☰</button>
    </header>

    <!-- Main content area -->
    <main class="mobile-main">
      <div class="content-card">
        <h2>Welcome to Your Mobile App</h2>
        <p>This app is designed exclusively for mobile devices with touch-optimized interactions.</p>
        
        <div class="action-buttons">
          <button class="primary-btn" @click="handleAction('primary')">
            Primary Action
          </button>
          <button class="secondary-btn" @click="handleAction('secondary')">
            Secondary Action
          </button>
        </div>

        <div class="feature-list">
          <div class="feature-item" v-for="feature in features" :key="feature.id" @click="selectFeature(feature)">
            <div class="feature-icon">{{ feature.icon }}</div>
            <div class="feature-text">
              <h3>{{ feature.title }}</h3>
              <p>{{ feature.description }}</p>
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
import { ref, reactive } from 'vue'

export default {
  name: 'App',
  setup() {
    const menuOpen = ref(false)
    const toast = reactive({
      show: false,
      message: ''
    })

    const features = ref([
      {
        id: 1,
        icon: '📱',
        title: 'Mobile First',
        description: 'Optimized for touch interactions'
      },
      {
        id: 2,
        icon: '⚡',
        title: 'Fast Loading',
        description: 'Built with Vite for speed'
      },
      {
        id: 3,
        icon: '🎨',
        title: 'Modern UI',
        description: 'Clean and responsive design'
      }
    ])

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value
    }

    const handleAction = (type) => {
      showToast(`${type} action triggered!`)
    }

    const selectFeature = (feature) => {
      showToast(`Selected: ${feature.title}`)
    }

    const navigate = (section) => {
      menuOpen.value = false
      showToast(`Navigating to ${section}`)
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