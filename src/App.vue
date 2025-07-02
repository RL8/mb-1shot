<template>
  <div class="mobile-app">
    <!-- Mobile header -->
    <header class="mobile-header">
      <div class="header-content">
        <h1>🎵 Music Besties</h1>
        <div class="connection-status" :class="{ connected: backendConnected, loading: loading }">
          <span v-if="loading">⏳</span>
          <span v-else-if="backendConnected">🟢</span>
          <span v-else>🔴</span>
        </div>
      </div>
      <button class="menu-btn" @click="toggleMenu">☰</button>
    </header>

    <!-- Main content area -->
    <main class="mobile-main" v-if="currentView === 'artists'">
      <!-- Artist Selection -->
      <div class="content-card">
        <h2>Choose Your Artist</h2>
        <p>Select an artist to start a deep conversation with your Music Bestie!</p>
        
        <div class="artist-selector">
          <button 
            v-for="artist in artists" 
            :key="artist.id"
            @click="selectArtist(artist)"
            :class="{ active: selectedArtist?.id === artist.id }"
            class="artist-btn"
          >
            {{ artist.emoji }} {{ artist.name }}
          </button>
        </div>
      </div>

      <!-- AG-UI Chat Interface (NEW) -->
      <div v-if="selectedArtist && showChat" class="content-card chat-container">
        <div class="chat-header">
          <h3>🎵 Music Bestie Chat</h3>
          <button @click="toggleChat" class="chat-toggle">
            {{ showChat ? '📊 Show Charts' : '💬 Start Chat' }}
          </button>
        </div>
        
        <!-- This is where MusicBestieChat component would go -->
        <MusicBestieChat :artist="selectedArtist" />
      </div>

      <!-- Traditional Artist Discography Chart (when chat is hidden) -->
      <div v-if="selectedArtist && selectedArtist.discography.length > 0 && !showChat">
        <MusicChart 
          :title="`${selectedArtist.name} Discography`"
          :data="selectedArtist.discography"
        />
      </div>

      <!-- Artist Info Card -->
      <div v-if="selectedArtist" class="content-card">
        <div class="artist-info">
          <div class="artist-header">
            <span class="artist-emoji">{{ selectedArtist.emoji }}</span>
            <div class="artist-details">
              <h3>{{ selectedArtist.name }}</h3>
              <p>{{ selectedArtist.discography.length }} Albums • {{ selectedArtist.genre }} • {{ selectedArtist.activeYears }}</p>
            </div>
          </div>
          
          <!-- AG-UI Integration Preview -->
          <div class="agui-preview">
            <h4>🚀 AG-UI Enhanced Features (Coming Soon)</h4>
            <div class="feature-grid">
              <div class="feature-item">
                <span class="feature-icon">🎭</span>
                <span>Creative Evolution Analysis</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🌟</span>
                <span>Hidden Gems Discovery</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">💭</span>
                <span>Lyrical Theme Exploration</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🔗</span>
                <span>Influence Network Mapping</span>
              </div>
            </div>
          </div>
          
          <div class="album-list">
            <div 
              v-for="album in selectedArtist.discography" 
              :key="album.id"
              @click="selectAlbum(album)"
              class="album-item"
            >
              <div class="album-info">
                <strong>{{ album.album }}</strong>
                <span class="album-year">{{ album.year }}</span>
              </div>
              <div class="album-meta">
                <span class="album-genre">{{ album.genre }}</span>
                <span class="album-popularity">⭐ {{ album.popularity }}/100</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Info -->
      <div class="content-card">
        <div class="status-info">
          <p v-if="loading" class="status-text loading">
            🔄 Loading artist data...
          </p>
          <p v-else-if="backendConnected" class="status-text connected">
            ✅ Connected to music database
          </p>
          <p v-else class="status-text offline">
            ⚠️ Using offline artist data
          </p>
          
          <!-- AG-UI Status -->
          <div class="agui-status">
            <p class="status-text">
              🎵 AG-UI Integration: <span class="status-ready">Ready to implement</span>
            </p>
            <small>Follow the integration guide to activate conversational features</small>
          </div>
        </div>
      </div>
    </main>

    <!-- Knowledge Graph Section (NEW) -->
    <div v-if="currentView === 'knowledge-graph'" class="content-card knowledge-graph-container">
      <MusicKnowledgeGraph />
    </div>

    <!-- Reddit Analysis Admin Section (NEW) -->
    <div v-if="currentView === 'reddit-admin'" class="admin-container">
      <RedditAnalysisAdmin />
    </div>

    <!-- Mobile navigation menu -->
    <nav class="mobile-nav" :class="{ active: menuOpen }">
      <ul>
        <li><a href="#" @click="navigate('artists')">🎤 Artists</a></li>
        <li><a href="#" @click="navigate('knowledge-graph')">🕸️ Knowledge Graph</a></li>
        <li><a href="#" @click="navigate('reddit-admin')">🔧 Reddit Admin</a></li>
        <li><a href="#" @click="navigate('favorites')">❤️ Favorites</a></li>
        <li><a href="#" @click="navigate('charts')">📊 Charts</a></li>
        <li><a href="#" @click="navigate('settings')">⚙️ Settings</a></li>
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
import MusicBestieChat from './components/MusicBestieChat.vue'
import MusicChart from './components/MusicChart.vue'
import MusicKnowledgeGraph from './components/MusicKnowledgeGraph.vue'
import RedditAnalysisAdmin from './components/RedditAnalysisAdmin.vue'

export default {
  name: 'MusicBesties',
  components: {
    MusicBestieChat,
    MusicChart,
    MusicKnowledgeGraph,
    RedditAnalysisAdmin
  },
  setup() {
    const menuOpen = ref(false)
    const loading = ref(true)
    const backendConnected = ref(false)
    const selectedArtist = ref(null)
    const showChat = ref(false)
    const currentView = ref('artists')
    const toast = reactive({
      show: false,
      message: ''
    })

    const artists = ref([
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
    ])

    // Initialize app and load data from backend
    onMounted(async () => {
      await initializeApp()
    })

    const initializeApp = async () => {
      try {
        // Check backend health
        const health = await apiService.checkHealth()
        backendConnected.value = health.status === 'OK'
        
        // Try to load artists from backend
        try {
          const backendArtists = await apiService.getFeatures()
          if (backendArtists && backendArtists.length > 0) {
            // Backend has artist data, could integrate here
            console.log('Backend features available:', backendArtists)
          }
        } catch (error) {
          console.log('Using local artist data')
        }
        
        // Track app startup
        await apiService.trackEvent('music_app_start', {
          timestamp: new Date().toISOString(),
          totalArtists: artists.value.length
        })
        
        showToast('🎵 Welcome to Music Besties!')
      } catch (error) {
        console.error('Failed to connect to backend:', error)
        backendConnected.value = false
        showToast('🎵 Exploring artists offline')
      } finally {
        loading.value = false
      }
    }

    const selectArtist = async (artist) => {
      selectedArtist.value = artist
      showChat.value = true
      showToast(`Selected ${artist.name} ${artist.emoji} - Ready to chat!`)
      
      // Track artist selection
      if (backendConnected.value) {
        try {
          await apiService.trackEvent('artist_selected', {
            artistId: artist.id,
            artistName: artist.name,
            albumCount: artist.discography.length
          })
        } catch (error) {
          console.error('Failed to track artist selection:', error)
        }
      }
    }

    const selectAlbum = async (album) => {
      showToast(`🎵 Selected: ${album.album} (${album.year})`)
      
      // Track album selection
      if (backendConnected.value) {
        try {
          await apiService.trackEvent('album_selected', {
            albumId: album.id,
            albumName: album.album,
            year: album.year,
            artistName: selectedArtist.value?.name
          })
        } catch (error) {
          console.error('Failed to track album selection:', error)
        }
      }
    }

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value
      
      // Track menu interaction
      if (backendConnected.value) {
        apiService.trackEvent('menu_toggle', { opened: menuOpen.value })
      }
    }

    const navigate = (section) => {
      menuOpen.value = false
      currentView.value = section
      showToast(`📱 Navigating to ${section}`)
      
      if (backendConnected.value) {
        apiService.trackEvent('navigation', { section })
      }
    }

    const toggleChat = () => {
      showChat.value = !showChat.value
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
      selectedArtist,
      showChat,
      currentView,
      toast,
      artists,
      toggleMenu,
      navigate,
      selectArtist,
      selectAlbum,
      showToast,
      toggleChat
    }
  }
}
</script> 