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

      <!-- Phase 2: Taxonomy Statistics -->
      <div class="taxonomy-stats" v-if="taxonomyStats">
        <h2>🎯 Music Taxonomy Analytics</h2>
        <p class="taxonomy-subtitle">AI-powered analysis of {{ taxonomyStats.totalSongs }} Taylor Swift songs</p>
        
        <div class="taxonomy-grid">
          <!-- Energy Distribution -->
          <div class="taxonomy-card">
            <h3>⚡ Energy Distribution</h3>
            <div class="distribution-chart">
              <div 
                v-for="(count, energy) in taxonomyStats.energyDistribution" 
                :key="energy"
                class="distribution-bar"
                :style="{ 
                  width: (count / taxonomyStats.totalSongs * 100) + '%',
                  backgroundColor: getEnergyColor(energy)
                }"
              >
                <span class="bar-label">{{ energy }}: {{ count }}</span>
              </div>
            </div>
          </div>

          <!-- Mood Distribution -->
          <div class="taxonomy-card">
            <h3>😊 Emotional Distribution</h3>
            <div class="distribution-chart">
              <div 
                v-for="(count, mood) in taxonomyStats.moodDistribution" 
                :key="mood"
                class="distribution-bar"
                :style="{ 
                  width: (count / taxonomyStats.totalSongs * 100) + '%',
                  backgroundColor: getMoodColor(mood)
                }"
              >
                <span class="bar-label">{{ mood }}: {{ count }}</span>
              </div>
            </div>
          </div>

          <!-- Context Analysis -->
          <div class="taxonomy-card">
            <h3>🕐 Time & Activity Context</h3>
            <div class="context-stats">
              <div class="context-row">
                <span class="context-label">🌅 Morning Songs:</span>
                <span class="context-value">{{ taxonomyStats.timeDistribution.Morning || 0 }}</span>
              </div>
              <div class="context-row">
                <span class="context-label">🌙 Night Songs:</span>
                <span class="context-value">{{ taxonomyStats.timeDistribution.Night || 0 }}</span>
              </div>
              <div class="context-row">
                <span class="context-label">📚 Study-Friendly:</span>
                <span class="context-value">{{ taxonomyStats.activityDistribution.Study || 0 }}</span>
              </div>
              <div class="context-row">
                <span class="context-label">💪 Workout Songs:</span>
                <span class="context-value">{{ taxonomyStats.activityDistribution.Workout || 0 }}</span>
              </div>
            </div>
          </div>

          <!-- Average Metrics -->
          <div class="taxonomy-card">
            <h3>📊 Average Metrics</h3>
            <div class="metrics-grid">
              <div class="metric-item">
                <div class="metric-value">{{ (taxonomyStats.averageEnergy * 100).toFixed(1) }}%</div>
                <div class="metric-label">Average Energy</div>
              </div>
              <div class="metric-item">
                <div class="metric-value">{{ (taxonomyStats.averageValence * 100).toFixed(1) }}%</div>
                <div class="metric-label">Average Positivity</div>
              </div>
              <div class="metric-item">
                <div class="metric-value">{{ (taxonomyStats.averageIntimacy * 100).toFixed(1) }}%</div>
                <div class="metric-label">Average Intimacy</div>
              </div>
              <div class="metric-item">
                <div class="metric-value">{{ (taxonomyStats.averageDanceability * 100).toFixed(1) }}%</div>
                <div class="metric-label">Average Danceability</div>
              </div>
            </div>
          </div>
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
      artists: [],
      taxonomyStats: null
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
        
        // Load taxonomy statistics
        const taxonomyResponse = await fetch("/api/taxonomy/stats")
        if (taxonomyResponse.ok) {
          this.taxonomyStats = await taxonomyResponse.json()
        }
        
        this.loading = false
      } catch (error) {
        console.error("Error loading data:", error)
        this.error = error.message
        
        // Use sample data based on Phase 1 results
        this.stats = { artists: 1, albums: 10, tracks: 232, total: 243 }
        this.artists = [
          { name: 'Taylor Swift', popularity: 95, followers: 89500000, genres: ['Pop', 'Country'], spotify_id: 'taylor' }
        ]
        
        // Sample taxonomy stats from our Phase 1 implementation
        this.taxonomyStats = {
          totalSongs: 232,
          energyDistribution: {
            'Chill': 8,
            'Moderate': 84, 
            'Energetic': 95,
            'High Energy': 45
          },
          moodDistribution: {
            'Melancholic': 36,
            'Reflective': 89,
            'Neutral': 76,
            'Uplifting': 23,
            'Euphoric': 8
          },
          timeDistribution: {
            'Morning': 41,
            'Night': 21,
            'Any Time': 170
          },
          activityDistribution: {
            'Study': 52,
            'Workout': 41,
            'Social': 31,
            'General': 108
          },
          averageEnergy: 0.561,
          averageValence: 0.393,
          averageIntimacy: 0.436,
          averageDanceability: 0.587
        }
        
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
    },

    getEnergyColor(energy) {
      const colors = {
        'Chill': '#3498db',
        'Moderate': '#f1c40f', 
        'Energetic': '#f39c12',
        'High Energy': '#e74c3c'
      }
      return colors[energy] || '#95a5a6'
    },

    getMoodColor(mood) {
      const colors = {
        'Melancholic': '#9b59b6',
        'Reflective': '#3498db',
        'Neutral': '#95a5a6',
        'Uplifting': '#f39c12',
        'Euphoric': '#e74c3c'
      }
      return colors[mood] || '#95a5a6'
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

/* Phase 2: Taxonomy Statistics Styles */
.taxonomy-stats {
  margin-top: 40px;
  text-align: center;
}

.taxonomy-stats h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.taxonomy-subtitle {
  color: #7f8c8d;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.taxonomy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.taxonomy-card {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.taxonomy-card h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.2rem;
}

/* Distribution Charts */
.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.distribution-bar {
  position: relative;
  height: 35px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  min-width: 60px;
  transition: all 0.3s ease;
}

.distribution-bar:hover {
  transform: translateX(5px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.bar-label {
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  margin-left: 10px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* Context Stats */
.context-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.context-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background 0.3s ease;
}

.context-row:hover {
  background: #e9ecef;
}

.context-label {
  color: #495057;
  font-weight: 500;
}

.context-value {
  color: #2c3e50;
  font-weight: 700;
  font-size: 1.1rem;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.metric-item {
  text-align: center;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  color: white;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

/* Responsive Design for Taxonomy */
@media (max-width: 768px) {
  .taxonomy-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .distribution-bar {
    height: 30px;
  }
  
  .bar-label {
    font-size: 0.8rem;
  }
}
</style> 