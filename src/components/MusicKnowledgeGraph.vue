<template>
  <div class="music-knowledge-graph">
    <div class="header-section">
      <h1 class="title">🎵 Music Knowledge Graph</h1>
      <div class="stats-grid" v-if="stats">
        <div class="stat-card">
          <div class="stat-number">{{ stats.artists }}</div>
          <div class="stat-label">Artists</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.albums }}</div>
          <div class="stat-label">Albums</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.tracks }}</div>
          <div class="stat-label">Tracks</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">Total Nodes</div>
        </div>
      </div>
    </div>

    <!-- Artists Grid -->
    <div class="artists-section">
      <h2>Artists</h2>
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="error" class="error">Error: {{ error }}</div>
      <div v-else class="artists-grid">
        <div 
          v-for="artist in artists" 
          :key="artist.spotify_id || artist.name"
          class="artist-card"
        >
          <h3>{{ artist.name }}</h3>
          <div v-if="artist.popularity" class="popularity">
            Popularity: {{ artist.popularity }}
          </div>
          <div v-if="artist.followers" class="followers">
            Followers: {{ formatNumber(artist.followers) }}
          </div>
          <div v-if="artist.genres" class="genres">
            <span v-for="genre in artist.genres" :key="genre" class="genre-tag">{{ genre }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MusicKnowledgeGraph",
  data() {
    return {
      loading: true,
      error: null,
      stats: null,
      artists: []
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        // Load stats
        const statsResponse = await fetch("/api/knowledge-graph/stats")
        if (statsResponse.ok) {
          this.stats = await statsResponse.json()
        }
        
        // Load artists
        const artistsResponse = await fetch("/api/artists")
        if (artistsResponse.ok) {
          const artistsData = await artistsResponse.json()
          this.artists = artistsData.artists || []
        } else {
          throw new Error('API not available')
        }
        
        this.loading = false
      } catch (error) {
        console.error("Error loading data:", error)
        this.error = error.message
        
        // Use sample data
        this.stats = { artists: 3, albums: 15, tracks: 45, total: 63 }
        this.artists = [
          { name: 'Taylor Swift', popularity: 95, followers: 89500000, genres: ['Pop', 'Country'], spotify_id: 'taylor' },
          { name: 'The Weeknd', popularity: 92, followers: 78200000, genres: ['R&B', 'Pop'], spotify_id: 'weeknd' },
          { name: 'Billie Eilish', popularity: 88, followers: 45600000, genres: ['Alternative Pop'], spotify_id: 'billie' }
        ]
        
        this.loading = false
      }
    },

    formatNumber(num) {
      if (!num) return '0'
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    }
  }
}
</script>

<style scoped>
.music-knowledge-graph {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.artists-section h2 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.loading, .error {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  color: #dc3545;
}

.artists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.artist-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.artist-card h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

.popularity, .followers {
  margin: 5px 0;
  color: #666;
  font-size: 14px;
}

.genres {
  margin-top: 10px;
}

.genre-tag {
  display: inline-block;
  background: #e9ecef;
  color: #495057;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  margin: 2px;
}
</style> 