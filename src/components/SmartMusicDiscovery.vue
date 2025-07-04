<template>
  <div class="smart-music-discovery">
    <!-- Header Section -->
    <div class="discovery-header">
      <h1 class="discovery-title">🎯 Smart Music Discovery</h1>
      <p class="discovery-subtitle">Find the perfect Taylor Swift song for any moment using AI-powered music taxonomy</p>
    </div>

    <!-- Filter Controls -->
    <div class="filter-section">
      <div class="filter-group">
        <label class="filter-label">🎵 Energy Level</label>
        <div class="filter-options">
          <button 
            v-for="energy in energyLevels" 
            :key="energy"
            @click="toggleFilter('energy', energy)"
            :class="{ active: filters.energy.includes(energy) }"
            class="filter-btn"
          >
            {{ energy }}
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">😊 Mood</label>
        <div class="filter-options">
          <button 
            v-for="mood in moods" 
            :key="mood"
            @click="toggleFilter('mood', mood)"
            :class="{ active: filters.mood.includes(mood) }"
            class="filter-btn"
          >
            {{ mood }}
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">🕐 Time of Day</label>
        <div class="filter-options">
          <button 
            v-for="time in timeContexts" 
            :key="time"
            @click="toggleFilter('time', time)"
            :class="{ active: filters.time.includes(time) }"
            class="filter-btn"
          >
            {{ time }}
          </button>
        </div>
      </div>

      <div class="filter-group">
        <label class="filter-label">🎯 Activity</label>
        <div class="filter-options">
          <button 
            v-for="activity in activities" 
            :key="activity"
            @click="toggleFilter('activity', activity)"
            :class="{ active: filters.activity.includes(activity) }"
            class="filter-btn"
          >
            {{ activity }}
          </button>
        </div>
      </div>

      <div class="filter-actions">
        <button @click="clearFilters" class="clear-btn">Clear All</button>
        <button @click="randomPick" class="random-btn">🎲 Surprise Me</button>
      </div>
    </div>

    <!-- Quick Presets -->
    <div class="presets-section">
      <h3>✨ Quick Presets</h3>
      <div class="presets-grid">
        <button 
          v-for="preset in quickPresets" 
          :key="preset.name"
          @click="applyPreset(preset)"
          class="preset-btn"
        >
          <span class="preset-icon">{{ preset.emoji }}</span>
          <span class="preset-name">{{ preset.name }}</span>
          <span class="preset-desc">{{ preset.description }}</span>
        </button>
      </div>
    </div>

    <!-- Results Section -->
    <div class="results-section">
      <div class="results-header">
        <h3>🎵 Discovered Songs</h3>
        <div class="results-meta">
          <span class="results-count">{{ filteredSongs.length }} songs found</span>
          <button @click="shuffleResults" class="shuffle-btn">🔀 Shuffle</button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Analyzing music taxonomy...</p>
      </div>

      <div v-else-if="filteredSongs.length === 0" class="empty-state">
        <div class="empty-icon">🎭</div>
        <h4>No songs match your current filters</h4>
        <p>Try adjusting your criteria or clearing some filters</p>
      </div>

      <div v-else class="songs-grid">
        <div 
          v-for="song in displayedSongs" 
          :key="song.id"
          class="song-card"
          @click="selectSong(song)"
        >
          <div class="song-header">
            <h4 class="song-title">{{ song.title }}</h4>
            <span class="song-album">{{ song.albumCode }}</span>
          </div>
          
          <div class="song-taxonomies">
            <div class="taxonomy-row">
              <span class="taxonomy-label">Energy:</span>
              <span class="taxonomy-value energy" :data-level="song.taxonomy_energy_label">
                {{ song.taxonomy_energy_label }}
              </span>
            </div>
            
            <div class="taxonomy-row">
              <span class="taxonomy-label">Mood:</span>
              <span class="taxonomy-value mood" :data-mood="song.taxonomy_emotional_label">
                {{ song.taxonomy_emotional_label }}
              </span>
            </div>
            
            <div class="taxonomy-row">
              <span class="taxonomy-label">Best for:</span>
              <span class="taxonomy-value activity">
                {{ song.taxonomy_time_primary }} • {{ song.taxonomy_activity_category }}
              </span>
            </div>
          </div>

          <div class="song-scores">
            <div class="score-item">
              <span class="score-label">Energy</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: (song.taxonomy_energy_level * 100) + '%' }"></div>
              </div>
              <span class="score-value">{{ (song.taxonomy_energy_level * 100).toFixed(0) }}%</span>
            </div>
            
            <div class="score-item">
              <span class="score-label">Positivity</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: (song.taxonomy_emotional_valence * 100) + '%' }"></div>
              </div>
              <span class="score-value">{{ (song.taxonomy_emotional_valence * 100).toFixed(0) }}%</span>
            </div>
          </div>

          <div class="song-actions">
            <button class="action-btn primary">🎵 Explore</button>
            <button class="action-btn secondary" @click.stop="shareSong(song)">📤 Share</button>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="filteredSongs.length > displayedSongs.length" class="load-more">
        <button @click="loadMore" class="load-more-btn">
          Load More Songs ({{ filteredSongs.length - displayedSongs.length }} remaining)
        </button>
      </div>
    </div>

    <!-- Selected Song Modal -->
    <div v-if="selectedSong" class="song-modal-overlay" @click="selectedSong = null">
      <div class="song-modal" @click.stop>
        <div class="modal-header">
          <h2>{{ selectedSong.title }}</h2>
          <button @click="selectedSong = null" class="close-btn">✕</button>
        </div>
        <div class="modal-content">
          <div class="song-details">
            <p><strong>Album:</strong> {{ selectedSong.albumCode }}</p>
            <p><strong>Energy Level:</strong> {{ selectedSong.taxonomy_energy_label }} ({{ (selectedSong.taxonomy_energy_level * 100).toFixed(1) }}%)</p>
            <p><strong>Emotional Tone:</strong> {{ selectedSong.taxonomy_emotional_label }} ({{ (selectedSong.taxonomy_emotional_valence * 100).toFixed(1) }}%)</p>
            <p><strong>Best Time:</strong> {{ selectedSong.taxonomy_time_primary }}</p>
            <p><strong>Activity Context:</strong> {{ selectedSong.taxonomy_activity_category }}</p>
            <p><strong>Intimacy Level:</strong> {{ (selectedSong.taxonomy_intimacy_level * 100).toFixed(1) }}%</p>
            <p><strong>Danceability:</strong> {{ (selectedSong.taxonomy_danceability * 100).toFixed(1) }}%</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SmartMusicDiscovery',
  data() {
    return {
      loading: true,
      songs: [],
      filteredSongs: [],
      displayedSongs: [],
      selectedSong: null,
      songsPerPage: 12,
      
      filters: {
        energy: [],
        mood: [],
        time: [],
        activity: []
      },
      
      energyLevels: ['Chill', 'Moderate', 'Energetic', 'High Energy'],
      moods: ['Melancholic', 'Reflective', 'Neutral', 'Uplifting', 'Euphoric'],
      timeContexts: ['Morning', 'Any Time', 'Night'],
      activities: ['Study', 'Workout', 'Social', 'General'],
      
      quickPresets: [
        {
          name: '3AM Thoughts',
          emoji: '🌙',
          description: 'Late night introspection',
          filters: { energy: ['Chill'], mood: ['Melancholic', 'Reflective'], time: ['Night'] }
        },
        {
          name: 'Morning Motivation',
          emoji: '☀️',
          description: 'Start your day right',
          filters: { energy: ['Energetic', 'High Energy'], mood: ['Uplifting', 'Euphoric'], time: ['Morning'] }
        },
        {
          name: 'Study Session',
          emoji: '📚',
          description: 'Focus and concentration',
          filters: { energy: ['Chill', 'Moderate'], activity: ['Study'] }
        },
        {
          name: 'Workout Power',
          emoji: '💪',
          description: 'High energy fitness',
          filters: { energy: ['Energetic', 'High Energy'], activity: ['Workout'] }
        },
        {
          name: 'Emotional Deep Dive',
          emoji: '💭',
          description: 'Feel all the feelings',
          filters: { mood: ['Melancholic', 'Reflective'] }
        },
        {
          name: 'Party Vibes',
          emoji: '🎉',
          description: 'Social and danceable',
          filters: { energy: ['Energetic', 'High Energy'], activity: ['Social'] }
        }
      ]
    }
  },
  
  computed: {
    hasActiveFilters() {
      return Object.values(this.filters).some(arr => arr.length > 0)
    }
  },
  
  mounted() {
    this.loadSongs()
  },
  
  methods: {
    async loadSongs() {
      this.loading = true
      try {
        // Generate sample taxonomy data for development
        this.loadSampleData()
      } catch (error) {
        console.error('Failed to load songs:', error)
        this.loadSampleData()
      }
      this.loading = false
    },
    
    loadSampleData() {
      // Generate sample taxonomy data based on our Phase 1 implementation
      this.songs = [
        { 
          id: 1, title: "Anti-Hero", albumCode: "MIDNIGHTS", 
          taxonomy_energy_level: 0.6, taxonomy_energy_label: "Moderate", 
          taxonomy_emotional_valence: 0.3, taxonomy_emotional_label: "Reflective", 
          taxonomy_time_primary: "Night", taxonomy_activity_category: "General", 
          taxonomy_intimacy_level: 0.7, taxonomy_danceability: 0.5 
        },
        { 
          id: 2, title: "Shake It Off", albumCode: "1989", 
          taxonomy_energy_level: 0.9, taxonomy_energy_label: "High Energy", 
          taxonomy_emotional_valence: 0.8, taxonomy_emotional_label: "Euphoric", 
          taxonomy_time_primary: "Any Time", taxonomy_activity_category: "Social", 
          taxonomy_intimacy_level: 0.2, taxonomy_danceability: 0.9 
        },
        { 
          id: 3, title: "All Too Well", albumCode: "RED", 
          taxonomy_energy_level: 0.4, taxonomy_energy_label: "Moderate", 
          taxonomy_emotional_valence: 0.2, taxonomy_emotional_label: "Melancholic", 
          taxonomy_time_primary: "Night", taxonomy_activity_category: "General", 
          taxonomy_intimacy_level: 0.9, taxonomy_danceability: 0.3 
        },
        { 
          id: 4, title: "22", albumCode: "RED", 
          taxonomy_energy_level: 0.8, taxonomy_energy_label: "Energetic", 
          taxonomy_emotional_valence: 0.9, taxonomy_emotional_label: "Euphoric", 
          taxonomy_time_primary: "Any Time", taxonomy_activity_category: "Social", 
          taxonomy_intimacy_level: 0.3, taxonomy_danceability: 0.8 
        },
        { 
          id: 5, title: "cardigan", albumCode: "FOLKLORE", 
          taxonomy_energy_level: 0.3, taxonomy_energy_label: "Chill", 
          taxonomy_emotional_valence: 0.4, taxonomy_emotional_label: "Reflective", 
          taxonomy_time_primary: "Night", taxonomy_activity_category: "Study", 
          taxonomy_intimacy_level: 0.8, taxonomy_danceability: 0.2 
        },
        { 
          id: 6, title: "ME!", albumCode: "LOVER", 
          taxonomy_energy_level: 0.9, taxonomy_energy_label: "High Energy", 
          taxonomy_emotional_valence: 0.9, taxonomy_emotional_label: "Euphoric", 
          taxonomy_time_primary: "Morning", taxonomy_activity_category: "Workout", 
          taxonomy_intimacy_level: 0.2, taxonomy_danceability: 0.9 
        },
        { 
          id: 7, title: "folklore", albumCode: "FOLKLORE", 
          taxonomy_energy_level: 0.25, taxonomy_energy_label: "Chill", 
          taxonomy_emotional_valence: 0.3, taxonomy_emotional_label: "Reflective", 
          taxonomy_time_primary: "Night", taxonomy_activity_category: "Study", 
          taxonomy_intimacy_level: 0.9, taxonomy_danceability: 0.15 
        },
        { 
          id: 8, title: "Blank Space", albumCode: "1989", 
          taxonomy_energy_level: 0.7, taxonomy_energy_label: "Energetic", 
          taxonomy_emotional_valence: 0.6, taxonomy_emotional_label: "Neutral", 
          taxonomy_time_primary: "Any Time", taxonomy_activity_category: "Social", 
          taxonomy_intimacy_level: 0.4, taxonomy_danceability: 0.7 
        }
      ]
      
      this.applyFilters()
    },
    
    toggleFilter(category, value) {
      const filterArray = this.filters[category]
      const index = filterArray.indexOf(value)
      
      if (index > -1) {
        filterArray.splice(index, 1)
      } else {
        filterArray.push(value)
      }
      
      this.applyFilters()
    },
    
    applyFilters() {
      this.filteredSongs = this.songs.filter(song => {
        // Energy filter
        if (this.filters.energy.length > 0 && !this.filters.energy.includes(song.taxonomy_energy_label)) {
          return false
        }
        
        // Mood filter
        if (this.filters.mood.length > 0 && !this.filters.mood.includes(song.taxonomy_emotional_label)) {
          return false
        }
        
        // Time filter
        if (this.filters.time.length > 0 && !this.filters.time.includes(song.taxonomy_time_primary)) {
          return false
        }
        
        // Activity filter
        if (this.filters.activity.length > 0 && !this.filters.activity.includes(song.taxonomy_activity_category)) {
          return false
        }
        
        return true
      })
      
      this.updateDisplayedSongs()
    },
    
    updateDisplayedSongs() {
      this.displayedSongs = this.filteredSongs.slice(0, this.songsPerPage)
    },
    
    loadMore() {
      const currentLength = this.displayedSongs.length
      const nextSongs = this.filteredSongs.slice(currentLength, currentLength + this.songsPerPage)
      this.displayedSongs.push(...nextSongs)
    },
    
    clearFilters() {
      this.filters = {
        energy: [],
        mood: [],
        time: [],
        activity: []
      }
      this.applyFilters()
    },
    
    applyPreset(preset) {
      this.filters = { ...preset.filters }
      this.applyFilters()
    },
    
    randomPick() {
      if (this.songs.length === 0) return
      
      const randomSong = this.songs[Math.floor(Math.random() * this.songs.length)]
      this.selectedSong = randomSong
    },
    
    shuffleResults() {
      this.filteredSongs = [...this.filteredSongs].sort(() => Math.random() - 0.5)
      this.updateDisplayedSongs()
    },
    
    selectSong(song) {
      this.selectedSong = song
    },
    
    shareSong(song) {
      const text = `Check out "${song.title}" by Taylor Swift - perfect for ${song.taxonomy_time_primary.toLowerCase()} ${song.taxonomy_activity_category.toLowerCase()} vibes! Energy: ${song.taxonomy_energy_label}, Mood: ${song.taxonomy_emotional_label}`
      
      if (navigator.share) {
        navigator.share({
          title: `${song.title} - Taylor Swift`,
          text: text,
          url: window.location.href
        })
      } else {
        navigator.clipboard.writeText(text)
        alert('Song info copied to clipboard!')
      }
    }
  }
}
</script>

<style scoped>
.smart-music-discovery {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.discovery-header {
  text-align: center;
  margin-bottom: 40px;
}

.discovery-title {
  font-size: 2.5rem;
  color: #2c3e50;
  margin-bottom: 10px;
}

.discovery-subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.filter-group {
  margin-bottom: 25px;
}

.filter-label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-btn {
  padding: 8px 16px;
  border: 2px solid #e9ecef;
  background: white;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.filter-btn:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: #667eea;
  color: white;
}

.filter-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
  justify-content: center;
}

.clear-btn, .random-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.clear-btn {
  background: #e9ecef;
  color: #495057;
}

.clear-btn:hover {
  background: #dee2e6;
}

.random-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.random-btn:hover {
  transform: translateY(-2px);
}

/* Presets Section */
.presets-section {
  margin-bottom: 30px;
}

.presets-section h3 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.preset-btn {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 15px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.preset-btn:hover {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.preset-icon {
  font-size: 1.5rem;
  display: block;
  margin-bottom: 8px;
}

.preset-name {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.preset-desc {
  display: block;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Results Section */
.results-section {
  background: white;
  border-radius: 15px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.results-header h3 {
  color: #2c3e50;
  margin: 0;
}

.results-meta {
  display: flex;
  align-items: center;
  gap: 15px;
}

.results-count {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.shuffle-btn {
  padding: 6px 12px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

/* Songs Grid */
.songs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.song-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.song-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.song-header {
  margin-bottom: 15px;
}

.song-title {
  color: #2c3e50;
  margin: 0 0 5px 0;
  font-size: 1.1rem;
}

.song-album {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.song-taxonomies {
  margin-bottom: 15px;
}

.taxonomy-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.taxonomy-label {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.taxonomy-value {
  font-weight: 600;
  font-size: 0.9rem;
}

.taxonomy-value.energy[data-level="High Energy"] { color: #e74c3c; }
.taxonomy-value.energy[data-level="Energetic"] { color: #f39c12; }
.taxonomy-value.energy[data-level="Moderate"] { color: #f1c40f; }
.taxonomy-value.energy[data-level="Chill"] { color: #3498db; }

.taxonomy-value.mood[data-mood="Euphoric"] { color: #e74c3c; }
.taxonomy-value.mood[data-mood="Uplifting"] { color: #f39c12; }
.taxonomy-value.mood[data-mood="Neutral"] { color: #95a5a6; }
.taxonomy-value.mood[data-mood="Reflective"] { color: #3498db; }
.taxonomy-value.mood[data-mood="Melancholic"] { color: #9b59b6; }

/* Score Bars */
.song-scores {
  margin-bottom: 15px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.score-label {
  font-size: 0.8rem;
  color: #7f8c8d;
  width: 60px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.score-value {
  font-size: 0.8rem;
  color: #495057;
  width: 35px;
  text-align: right;
}

/* Song Actions */
.song-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.secondary {
  background: #e9ecef;
  color: #495057;
}

.action-btn:hover {
  transform: translateY(-1px);
}

/* Loading and Empty States */
.loading-state, .empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

/* Load More */
.load-more {
  text-align: center;
  margin-top: 30px;
}

.load-more-btn {
  padding: 12px 24px;
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.load-more-btn:hover {
  border-color: #667eea;
  background: #f8f9ff;
}

/* Song Modal */
.song-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.song-modal {
  background: white;
  border-radius: 15px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 15px;
}

.modal-header h2 {
  color: #2c3e50;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.song-details p {
  margin: 10px 0;
  color: #495057;
}

/* Responsive Design */
@media (max-width: 768px) {
  .filter-options {
    flex-direction: column;
  }
  
  .presets-grid {
    grid-template-columns: 1fr;
  }
  
  .songs-grid {
    grid-template-columns: 1fr;
  }
  
  .results-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .filter-actions {
    flex-direction: column;
  }
}
</style> 