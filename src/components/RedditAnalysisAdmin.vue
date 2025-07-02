<template>
  <div class="reddit-admin">
    <!-- Header Section -->
    <div class="admin-header">
      <h1>🎵 Reddit Analysis Admin Dashboard</h1>
      <div class="stats-summary">
        <div class="stat-card">
          <div class="stat-number">{{ stats.total }}</div>
          <div class="stat-label">Total Artists</div>
        </div>
        <div class="stat-card success">
          <div class="stat-number">{{ stats.withPresence }}</div>
          <div class="stat-label">With Reddit Presence</div>
        </div>
        <div class="stat-card neutral">
          <div class="stat-number">{{ stats.withoutPresence }}</div>
          <div class="stat-label">No Presence</div>
        </div>
        <div class="stat-card highlight">
          <div class="stat-number">{{ stats.coveragePercent }}%</div>
          <div class="stat-label">Coverage</div>
        </div>
      </div>
    </div>

    <!-- Controls Section -->
    <div class="controls-section">
      <div class="control-group">
        <label>🔍 Search Artists:</label>
        <input 
          v-model="searchTerm" 
          type="text" 
          placeholder="Search by artist name or subreddit..."
          class="search-input"
        />
      </div>
      
      <div class="control-group">
        <label>📊 Filter by Tier:</label>
        <select v-model="tierFilter" class="tier-select">
          <option value="">All Tiers</option>
          <option value="🔥 Viral">🔥 Viral (19)</option>
          <option value="⚡ Popular">⚡ Popular (10)</option>
          <option value="📊 Present">📊 Present (18)</option>
          <option value="💤 Minimal">💤 Minimal (4)</option>
          <option value="❌ No Presence">❌ No Presence (49)</option>
        </select>
      </div>

      <div class="control-group">
        <label>📈 Min Score:</label>
        <input 
          v-model.number="minScore" 
          type="number" 
          step="0.1" 
          min="0"
          class="score-input"
        />
      </div>

      <div class="control-group">
        <button @click="exportData" class="export-btn">📄 Export CSV</button>
        <button @click="resetFilters" class="reset-btn">🔄 Reset</button>
      </div>
    </div>

    <!-- Tier Distribution -->
    <div class="tier-distribution">
      <h3>Tier Distribution:</h3>
      <div class="tier-bars">
        <div v-for="(count, tier) in tierDistribution" :key="tier" class="tier-bar">
          <span class="tier-label">{{ tier }}</span>
          <div class="bar-container">
            <div 
              class="bar-fill" 
              :class="getTierClass(tier)"
              :style="{width: (count / stats.total * 100) + '%'}"
            ></div>
            <span class="tier-count">{{ count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Summary -->
    <div class="results-summary">
      <span>Showing {{ filteredArtists.length }} of {{ stats.total }} artists</span>
      <span v-if="filteredArtists.length !== stats.total">
        ({{ Math.round((filteredArtists.length / stats.total) * 100) }}% of total)
      </span>
    </div>

    <!-- Main Data Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th @click="sortBy('index')" class="sortable">
              # <span v-if="sortField === 'index'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('artist')" class="sortable">
              Artist <span v-if="sortField === 'artist'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('tier')" class="sortable">
              Tier <span v-if="sortField === 'tier'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('popularity_score')" class="sortable">
              Score <span v-if="sortField === 'popularity_score'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('primary_subreddit')" class="sortable">
              Subreddit <span v-if="sortField === 'primary_subreddit'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('subscribers')" class="sortable">
              Subscribers <span v-if="sortField === 'subscribers'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('posts_last_month')" class="sortable">
              Posts <span v-if="sortField === 'posts_last_month'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('comments_last_month')" class="sortable">
              Comments <span v-if="sortField === 'comments_last_month'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('total_activity')" class="sortable">
              Activity <span v-if="sortField === 'total_activity'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('relevance_score')" class="sortable">
              Relevance <span v-if="sortField === 'relevance_score'">{{ sortDirection === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th class="reasons-col">Relevance Reasons</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(artist, index) in paginatedArtists" 
            :key="artist.artist + index"
            :class="getRowClass(artist.tier)"
          >
            <td class="index-col">{{ getOriginalIndex(artist) }}</td>
            <td class="artist-col">
              <strong>{{ artist.artist }}</strong>
            </td>
            <td class="tier-col">
              <span :class="getTierBadgeClass(artist.tier)">{{ artist.tier }}</span>
            </td>
            <td class="score-col">
              <span :class="getScoreClass(artist.popularity_score)">
                {{ artist.popularity_score.toFixed(2) }}
              </span>
            </td>
            <td class="subreddit-col">
              <a 
                v-if="artist.primary_subreddit" 
                :href="artist.subreddit_url" 
                target="_blank"
                class="subreddit-link"
              >
                r/{{ artist.primary_subreddit }}
              </a>
              <span v-else class="no-subreddit">—</span>
            </td>
            <td class="subscribers-col">
              {{ formatNumber(artist.subscribers) }}
            </td>
            <td class="posts-col">{{ artist.posts_last_month }}</td>
            <td class="comments-col">{{ formatNumber(artist.comments_last_month) }}</td>
            <td class="activity-col">
              <strong>{{ formatNumber(artist.total_activity) }}</strong>
            </td>
            <td class="relevance-col">{{ artist.relevance_score }}</td>
            <td class="reasons-col">
              <div class="reasons-text">{{ artist.relevance_reasons }}</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="currentPage = 1" 
        :disabled="currentPage === 1"
        class="page-btn"
      >First</button>
      <button 
        @click="currentPage--" 
        :disabled="currentPage === 1"
        class="page-btn"
      >Previous</button>
      
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }} 
        ({{ filteredArtists.length }} total results)
      </span>
      
      <button 
        @click="currentPage++" 
        :disabled="currentPage === totalPages"
        class="page-btn"
      >Next</button>
      <button 
        @click="currentPage = totalPages" 
        :disabled="currentPage === totalPages"
        class="page-btn"
      >Last</button>
    </div>

    <!-- Debug Info -->
    <div class="debug-info">
      <details>
        <summary>🔧 Debug Information</summary>
        <div class="debug-content">
          <p><strong>Analysis Date:</strong> {{ analysisData?.analysis_date }}</p>
          <p><strong>Methodology:</strong> {{ analysisData?.methodology }}</p>
          <p><strong>Data Sources:</strong></p>
          <ul>
            <li v-for="(source, key) in analysisData?.data_sources" :key="key">
              {{ key }}: {{ source }}
            </li>
          </ul>
          <p><strong>Scoring Criteria:</strong></p>
          <ul>
            <li v-for="(value, key) in analysisData?.scoring_criteria" :key="key">
              {{ key }}: {{ value }}
            </li>
          </ul>
        </div>
      </details>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RedditAnalysisAdmin',
  data() {
    return {
      analysisData: null,
      searchTerm: '',
      tierFilter: '',
      minScore: 0,
      sortField: '',
      sortDirection: 'desc',
      currentPage: 1,
      itemsPerPage: 25,
      loading: true,
      error: null
    }
  },
  
  async mounted() {
    await this.loadData()
  },
  
  computed: {
    stats() {
      if (!this.analysisData) return { total: 0, withPresence: 0, withoutPresence: 0, coveragePercent: 0 }
      
      return {
        total: this.analysisData.summary.total_artists_analyzed,
        withPresence: this.analysisData.summary.artists_with_reddit_presence,
        withoutPresence: this.analysisData.summary.artists_without_presence,
        coveragePercent: Math.round((this.analysisData.summary.artists_with_reddit_presence / this.analysisData.summary.total_artists_analyzed) * 100)
      }
    },
    
    tierDistribution() {
      return this.analysisData?.summary?.tier_distribution || {}
    },
    
    allArtists() {
      if (!this.analysisData) return []
      return this.analysisData.artists_in_original_order.map((artist, index) => ({
        ...artist,
        originalIndex: index + 1
      }))
    },
    
    filteredArtists() {
      let filtered = this.allArtists
      
      // Search filter
      if (this.searchTerm) {
        const term = this.searchTerm.toLowerCase()
        filtered = filtered.filter(artist => 
          artist.artist.toLowerCase().includes(term) ||
          (artist.primary_subreddit && artist.primary_subreddit.toLowerCase().includes(term))
        )
      }
      
      // Tier filter
      if (this.tierFilter) {
        filtered = filtered.filter(artist => artist.tier === this.tierFilter)
      }
      
      // Score filter
      if (this.minScore > 0) {
        filtered = filtered.filter(artist => artist.popularity_score >= this.minScore)
      }
      
      // Sort
      if (this.sortField) {
        filtered.sort((a, b) => {
          let aVal = a[this.sortField] || 0
          let bVal = b[this.sortField] || 0
          
          // Handle special cases
          if (this.sortField === 'artist' || this.sortField === 'primary_subreddit' || this.sortField === 'tier') {
            aVal = (aVal || '').toString().toLowerCase()
            bVal = (bVal || '').toString().toLowerCase()
          }
          
          if (this.sortDirection === 'asc') {
            return aVal > bVal ? 1 : -1
          } else {
            return aVal < bVal ? 1 : -1
          }
        })
      }
      
      return filtered
    },
    
    totalPages() {
      return Math.ceil(this.filteredArtists.length / this.itemsPerPage)
    },
    
    paginatedArtists() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredArtists.slice(start, end)
    }
  },
  
  methods: {
    async loadData() {
      try {
        const response = await fetch('/data/reddit_analysis.json')
        if (!response.ok) {
          throw new Error(`Failed to load Reddit analysis data: ${response.status}`)
        }
        this.analysisData = await response.json()
        this.loading = false
      } catch (error) {
        this.error = error.message
        this.loading = false
        console.error('Error loading data:', error)
      }
    },
    
    sortBy(field) {
      if (this.sortField === field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortField = field
        this.sortDirection = field === 'artist' ? 'asc' : 'desc'
      }
      this.currentPage = 1
    },
    
    resetFilters() {
      this.searchTerm = ''
      this.tierFilter = ''
      this.minScore = 0
      this.sortField = ''
      this.sortDirection = 'desc'
      this.currentPage = 1
    },
    
    getOriginalIndex(artist) {
      return artist.originalIndex
    },
    
    getRowClass(tier) {
      return {
        'row-viral': tier === '🔥 Viral',
        'row-popular': tier === '⚡ Popular',
        'row-present': tier === '📊 Present',
        'row-minimal': tier === '💤 Minimal',
        'row-none': tier === '❌ No Presence'
      }
    },
    
    getTierClass(tier) {
      return {
        'tier-viral': tier === '🔥 Viral',
        'tier-popular': tier === '⚡ Popular',
        'tier-present': tier === '📊 Present',
        'tier-minimal': tier === '💤 Minimal',
        'tier-none': tier === '❌ No Presence'
      }
    },
    
    getTierBadgeClass(tier) {
      return {
        'badge': true,
        'badge-viral': tier === '🔥 Viral',
        'badge-popular': tier === '⚡ Popular',
        'badge-present': tier === '📊 Present',
        'badge-minimal': tier === '💤 Minimal',
        'badge-none': tier === '❌ No Presence'
      }
    },
    
    getScoreClass(score) {
      if (score >= 5) return 'score-viral'
      if (score >= 2) return 'score-popular'
      if (score >= 0.5) return 'score-present'
      if (score > 0) return 'score-minimal'
      return 'score-none'
    },
    
    formatNumber(num) {
      if (num === 0) return '—'
      if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
      if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
      return num.toString()
    },
    
    exportData() {
      const headers = ['Index', 'Artist', 'Tier', 'Score', 'Subreddit', 'Subscribers', 'Posts', 'Comments', 'Activity', 'Relevance', 'Reasons']
      const rows = this.filteredArtists.map(artist => [
        artist.originalIndex,
        artist.artist,
        artist.tier,
        artist.popularity_score,
        artist.primary_subreddit || '',
        artist.subscribers,
        artist.posts_last_month,
        artist.comments_last_month,
        artist.total_activity,
        artist.relevance_score,
        artist.relevance_reasons
      ])
      
      const csvContent = [headers, ...rows]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n')
      
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `reddit_analysis_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style scoped>
.reddit-admin {
  padding: 20px;
  max-width: 100%;
  font-family: 'Courier New', monospace;
  background: #1a1a1a;
  color: #e0e0e0;
  min-height: 100vh;
}

.admin-header h1 {
  margin: 0 0 20px 0;
  color: #00ff88;
  font-size: 24px;
}

.stats-summary {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.stat-card {
  background: #2a2a2a;
  border: 1px solid #444;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
  min-width: 120px;
}

.stat-card.success { border-color: #00ff88; }
.stat-card.neutral { border-color: #ffaa00; }
.stat-card.highlight { border-color: #00aaff; }

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

.controls-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.control-group label {
  font-size: 12px;
  color: #888;
}

.search-input, .tier-select, .score-input {
  background: #2a2a2a;
  border: 1px solid #444;
  color: #e0e0e0;
  padding: 8px;
  border-radius: 4px;
}

.search-input {
  width: 250px;
}

.export-btn, .reset-btn, .page-btn {
  background: #333;
  border: 1px solid #555;
  color: #e0e0e0;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.export-btn:hover, .reset-btn:hover, .page-btn:hover:not(:disabled) {
  background: #444;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.tier-distribution {
  margin-bottom: 20px;
}

.tier-distribution h3 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.tier-bars {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tier-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tier-label {
  width: 120px;
  font-size: 12px;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #2a2a2a;
  border-radius: 3px;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
}

.tier-count {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: #fff;
  text-shadow: 1px 1px 1px rgba(0,0,0,0.8);
}

.tier-viral { background: #ff4444; }
.tier-popular { background: #ffaa00; }
.tier-present { background: #00aaff; }
.tier-minimal { background: #888; }
.tier-none { background: #444; }

.results-summary {
  margin-bottom: 15px;
  font-size: 14px;
  color: #888;
}

.table-container {
  overflow-x: auto;
  border: 1px solid #444;
  border-radius: 4px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.data-table th {
  background: #333;
  padding: 10px 8px;
  text-align: left;
  border-bottom: 1px solid #444;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #444;
}

.data-table td {
  padding: 8px;
  border-bottom: 1px solid #333;
  vertical-align: top;
}

.row-viral { background: rgba(255, 68, 68, 0.1); }
.row-popular { background: rgba(255, 170, 0, 0.1); }
.row-present { background: rgba(0, 170, 255, 0.1); }
.row-minimal { background: rgba(136, 136, 136, 0.1); }
.row-none { background: rgba(68, 68, 68, 0.1); }

.index-col { width: 50px; text-align: center; }
.artist-col { width: 200px; min-width: 150px; }
.tier-col { width: 100px; }
.score-col { width: 80px; text-align: right; }
.subreddit-col { width: 150px; }
.subscribers-col { width: 100px; text-align: right; }
.posts-col { width: 70px; text-align: right; }
.comments-col { width: 80px; text-align: right; }
.activity-col { width: 80px; text-align: right; }
.relevance-col { width: 80px; text-align: center; }
.reasons-col { min-width: 200px; }

.badge {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: bold;
}

.badge-viral { background: #ff4444; color: white; }
.badge-popular { background: #ffaa00; color: white; }
.badge-present { background: #00aaff; color: white; }
.badge-minimal { background: #888; color: white; }
.badge-none { background: #444; color: #ccc; }

.score-viral { color: #ff4444; font-weight: bold; }
.score-popular { color: #ffaa00; font-weight: bold; }
.score-present { color: #00aaff; font-weight: bold; }
.score-minimal { color: #888; }
.score-none { color: #555; }

.subreddit-link {
  color: #00aaff;
  text-decoration: none;
}

.subreddit-link:hover {
  text-decoration: underline;
}

.no-subreddit {
  color: #555;
}

.reasons-text {
  font-size: 11px;
  line-height: 1.3;
  opacity: 0.8;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.page-info {
  margin: 0 15px;
  font-size: 14px;
}

.debug-info {
  margin-top: 30px;
  border-top: 1px solid #444;
  padding-top: 20px;
}

.debug-info summary {
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 10px;
}

.debug-content {
  background: #2a2a2a;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.debug-content ul {
  margin: 5px 0;
  padding-left: 20px;
}

.debug-content li {
  margin: 3px 0;
}
</style> 