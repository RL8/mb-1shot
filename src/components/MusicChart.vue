<template>
  <div class="music-chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <button 
          v-for="type in chartTypes" 
          :key="type.value"
          @click="changeChartType(type.value)"
          :class="{ active: currentType === type.value }"
          class="chart-type-btn"
        >
          {{ type.icon }}
        </button>
      </div>
    </div>
    <div ref="chartContainer" class="chart-area"></div>
    
    <!-- Mobile fallback card layout for very small screens -->
    <div v-if="showMobileFallback" class="mobile-data-cards">
      <div v-for="(item, index) in props.data" :key="index" class="data-card">
        <div class="card-header">
          <span class="album-name">{{ item.album }}</span>
          <span class="year">{{ item.year }}</span>
        </div>
        <div class="card-content">
          <span class="genre">{{ item.genre }}</span>
          <span class="popularity">⭐ {{ item.popularity || 'N/A' }}/100</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Artist Timeline' },
  data: { type: Array, default: () => [] }
})

const chartContainer = ref(null)
const currentType = ref('timeline')
const showMobileFallback = ref(false)
let myChart = null

const chartTypes = [
  { value: 'timeline', icon: '📅' },
  { value: 'popularity', icon: '⭐' },
  { value: 'genre', icon: '🎵' }
]

// Mobile detection utilities
const isMobile = () => window.innerWidth < 768
const isTinyScreen = () => window.innerWidth < 480
const isTablet = () => window.innerWidth >= 768 && window.innerWidth < 1024

// Responsive configuration getters
const getMobileFontSize = (baseSize) => {
  if (isTinyScreen()) return Math.max(16, baseSize)
  if (isMobile()) return Math.max(16, baseSize)
  if (isTablet()) return Math.max(14, baseSize)
  return baseSize
}

const getResponsiveSymbolSize = () => {
  if (isMobile()) return 12
  return 10
}

const getResponsiveChartHeight = () => {
  if (isTinyScreen()) return 280
  if (isMobile()) return 320
  if (isTablet()) return 350
  return 400
}

const getResponsiveGrid = () => {
  if (isMobile()) {
    return {
      left: '12%',
      right: '12%',
      top: '15%',
      bottom: '25%'
    }
  }
  return {
    left: '10%',
    right: '10%',
    top: '10%',
    bottom: '20%'
  }
}

// Debounced resize handler
let resizeTimer = null
const debouncedResize = () => {
  clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    handleResize()
  }, 300)
}

const handleResize = () => {
  if (!myChart) return
  
  // Check if we should show mobile fallback
  showMobileFallback.value = isTinyScreen() && currentType.value === 'genre'
  
  if (showMobileFallback.value) {
    myChart.dispose()
    myChart = null
    return
  }
  
  // Reinitialize with proper renderer for current screen size
  const currentOption = myChart.getOption()
  myChart.dispose()
  initChart()
  
  // Apply responsive configuration
  updateChart()
}

const initChart = () => {
  if (!chartContainer.value || showMobileFallback.value) return
  
  // Use SVG renderer for mobile to reduce memory usage
  const renderer = isMobile() ? 'svg' : 'canvas'
  
  myChart = echarts.init(chartContainer.value, null, {
    renderer: renderer,
    useDirtyRect: !isMobile() // Disable dirty rect on mobile for simplicity
  })
  
  updateChart()
  window.addEventListener('resize', debouncedResize)
}

const updateChart = async () => {
  if (!myChart || !props.data.length) return

  await nextTick()
  
  // Update chart area height responsively
  if (chartContainer.value) {
    chartContainer.value.style.height = `${getResponsiveChartHeight()}px`
  }

  let option = {}
  
  switch (currentType.value) {
    case 'timeline':
      option = getTimelineOption()
      break
    case 'popularity':
      option = getPopularityOption()
      break
    case 'genre':
      option = getGenreOption()
      break
  }
  
  myChart.setOption(option, true)
  myChart.resize()
}

const getTimelineOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { 
    color: '#1d1d1f',
    fontSize: getMobileFontSize(14),
    fontWeight: 500
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: getMobileFontSize(16)
    },
    formatter: function(params) {
      const data = params[0]
      const albumData = props.data[data.dataIndex]
      const fontSize = getMobileFontSize(16)
      const subFontSize = getMobileFontSize(14)
      return `
        <div style="padding: 12px; max-width: 280px;">
          <strong style="font-size: ${fontSize}px; line-height: 1.4;">${albumData.album}</strong><br/>
          <span style="color: #666; font-size: ${subFontSize}px; line-height: 1.3;">Year: ${albumData.year}</span><br/>
          <span style="color: #666; font-size: ${subFontSize}px; line-height: 1.3;">Genre: ${albumData.genre}</span><br/>
          <span style="color: #007AFF; font-size: ${subFontSize}px; font-weight: 600; line-height: 1.3;">Popularity: ${albumData.popularity}/100</span>
        </div>
      `
    }
  },
  grid: getResponsiveGrid(),
  xAxis: {
    type: 'category',
    data: props.data.map(item => item.year),
    axisLine: { 
      lineStyle: { color: '#d1d1d6', width: 2 }
    },
    axisLabel: { 
      color: '#86868b', 
      fontSize: getMobileFontSize(16),
      fontWeight: 500,
      interval: isMobile() ? 'auto' : 0, // Let ECharts optimize spacing on mobile
      rotate: isMobile() ? 45 : 0, // Rotate labels on mobile to prevent overlap
      margin: isMobile() ? 15 : 12,
      formatter: function(value) {
        // Smart truncation for mobile
        if (isMobile() && value.toString().length > 4) {
          return "'" + value.toString().slice(-2)
        }
        return value
      }
    },
    axisTick: {
      show: true,
      length: isMobile() ? 8 : 6,
      lineStyle: { color: '#d1d1d6' }
    }
  },
  yAxis: { 
    show: false
  },
  series: [{
    type: 'line',
    data: props.data.map((item, index) => ({
      value: index + 1,
      name: item.album,
      itemStyle: { color: '#007AFF' }
    })),
    lineStyle: { 
      color: '#007AFF', 
      width: isMobile() ? 3 : 4
    },
    symbol: 'circle',
    symbolSize: getResponsiveSymbolSize(),
    smooth: true,
    emphasis: {
      scale: isMobile() ? 1.3 : 1.2, // Larger emphasis for touch
      itemStyle: {
        shadowBlur: 8,
        shadowColor: 'rgba(0, 122, 255, 0.3)'
      }
    },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(0, 122, 255, 0.3)' },
          { offset: 1, color: 'rgba(0, 122, 255, 0.1)' }
        ]
      }
    }
  }]
})

const getPopularityOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { 
    color: '#1d1d1f',
    fontSize: getMobileFontSize(14),
    fontWeight: 500
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: getMobileFontSize(16)
    },
    formatter: function(params) {
      const data = params[0]
      const albumData = props.data[data.dataIndex]
      const fontSize = getMobileFontSize(16)
      const subFontSize = getMobileFontSize(14)
      return `
        <div style="padding: 12px; max-width: 280px;">
          <strong style="font-size: ${fontSize}px; line-height: 1.4;">${albumData.album}</strong><br/>
          <span style="color: #666; font-size: ${subFontSize}px; line-height: 1.3;">${albumData.year} • ${albumData.genre}</span><br/>
          <span style="color: #34C759; font-size: ${fontSize}px; font-weight: 600; line-height: 1.3;">⭐ ${albumData.popularity}/100</span>
        </div>
      `
    }
  },
  grid: {
    left: isMobile() ? '8%' : '5%',
    right: isMobile() ? '8%' : '5%',
    top: '15%',
    bottom: isMobile() ? '40%' : '35%' // Extra space for rotated labels
  },
  xAxis: {
    type: 'category',
    data: props.data.map(item => {
      // Smart truncation based on screen size
      const maxLength = isTinyScreen() ? 8 : isMobile() ? 10 : 12
      return item.album.length > maxLength ? 
        item.album.slice(0, maxLength) + '..' : item.album
    }),
    axisLabel: { 
      rotate: isMobile() ? 45 : 35, 
      color: '#86868b', 
      fontSize: getMobileFontSize(14),
      fontWeight: 500,
      interval: 0,
      margin: isMobile() ? 12 : 8
    },
    axisLine: { 
      lineStyle: { color: '#d1d1d6', width: 2 }
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: { 
      color: '#86868b', 
      fontSize: getMobileFontSize(14),
      fontWeight: 500
    },
    splitLine: { 
      lineStyle: { color: '#f5f5f5', width: 1 }
    },
    axisLine: { show: false }
  },
  series: [{
    type: 'bar',
    data: props.data.map(item => ({
      value: item.popularity || Math.floor(Math.random() * 100),
      itemStyle: { 
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#34C759' },
            { offset: 1, color: '#30D158' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      }
    })),
    barWidth: isMobile() ? '80%' : '70%',
    emphasis: {
      itemStyle: {
        shadowBlur: 8,
        shadowColor: 'rgba(52, 199, 89, 0.3)'
      }
    }
  }]
})

const getGenreOption = () => {
  // Show card layout for tiny screens
  if (isTinyScreen()) {
    showMobileFallback.value = true
    return {}
  }

  return {
    backgroundColor: 'transparent',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: getMobileFontSize(14),
      fontWeight: 500
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: '#ffffff',
      borderColor: '#d1d1d6',
      textStyle: { 
        color: '#1d1d1f',
        fontSize: getMobileFontSize(16)
      },
      formatter: function(params) {
        const fontSize = getMobileFontSize(16)
        const subFontSize = getMobileFontSize(14)
        return `
          <div style="padding: 12px; max-width: 200px;">
            <strong style="font-size: ${fontSize}px; line-height: 1.4;">${params.name}</strong><br/>
            <span style="color: #666; font-size: ${subFontSize}px; line-height: 1.3;">${params.value} albums</span><br/>
            <span style="color: #007AFF; font-size: ${subFontSize}px; line-height: 1.3;">${params.percent}% of discography</span>
          </div>
        `
      }
    },
    legend: {
      show: !isMobile(), // Hide legend on mobile to save space
      bottom: 10,
      textStyle: {
        fontSize: getMobileFontSize(12)
      }
    },
    series: [{
      type: 'pie',
      radius: isMobile() ? ['25%', '70%'] : ['30%', '75%'],
      center: ['50%', '50%'],
      data: getGenreData(),
      itemStyle: {
        borderRadius: isMobile() ? 6 : 8,
        borderColor: '#fff',
        borderWidth: isMobile() ? 2 : 3
      },
      label: {
        show: true,
        position: isMobile() ? 'inside' : 'outside',
        color: '#1d1d1f',
        fontSize: getMobileFontSize(12),
        fontWeight: 600,
        formatter: function(params) {
          if (isMobile()) {
            // Show only value inside on mobile
            return params.value.toString()
          } else {
            // Show abbreviated genre names for desktop
            const shortName = params.name.length > 8 ? 
              params.name.split(' ')[0] : params.name
            return `${shortName}\n${params.value}`
          }
        }
      },
      labelLine: {
        show: !isMobile(), // Hide label lines on mobile
        length: 15,
        length2: 10,
        lineStyle: {
          color: '#d1d1d6',
          width: 2
        }
      },
      emphasis: {
        scale: isMobile() ? 1.05 : 1.1,
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        }
      },
      avoidLabelOverlap: true,
      labelLayout: {
        hideOverlap: true
      }
    }]
  }
}

const getGenreData = () => {
  const genres = {}
  props.data.forEach(item => {
    const genre = item.genre || 'Pop'
    genres[genre] = (genres[genre] || 0) + 1
  })
  
  const colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE', '#ff6b6b']
  
  return Object.entries(genres).map(([genre, count], index) => ({
    value: count,
    name: genre,
    itemStyle: { color: colors[index % colors.length] }
  }))
}

const changeChartType = (type) => {
  currentType.value = type
  showMobileFallback.value = false
  
  if (type === 'genre' && isTinyScreen()) {
    showMobileFallback.value = true
    if (myChart) {
      myChart.dispose()
      myChart = null
    }
    return
  }
  
  if (!myChart) {
    initChart()
  } else {
    updateChart()
  }
}

watch(() => props.data, () => {
  if (!showMobileFallback.value) {
    updateChart()
  }
}, { deep: true })

onMounted(() => {
  // Initial mobile fallback check
  showMobileFallback.value = isTinyScreen() && currentType.value === 'genre'
  
  if (!showMobileFallback.value) {
    initChart()
  }
})

onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
    window.removeEventListener('resize', debouncedResize)
  }
  if (resizeTimer) {
    clearTimeout(resizeTimer)
  }
})
</script>

<style scoped>
.music-chart-container {
  background-color: var(--card-background);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow);
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-type-btn {
  background: var(--background-color);
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 48px;  /* Increased for better touch targets */
  min-height: 48px; /* Increased for better touch targets */
  display: flex;
  align-items: center;
  justify-content: center;
  touch-action: manipulation; /* Optimize for touch */
}

.chart-type-btn.active {
  background: var(--primary-color);
  transform: scale(1.05);
}

.chart-type-btn:hover {
  background: var(--primary-color);
  opacity: 0.8;
}

.chart-area {
  width: 100%;
  height: 400px; /* Default height, will be overridden by JS */
  position: relative;
  transition: height 0.3s ease;
}

/* Mobile fallback cards */
.mobile-data-cards {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.data-card {
  background: var(--background-color);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.album-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 16px;
}

.year {
  color: var(--text-secondary);
  font-size: 14px;
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.genre {
  color: var(--text-secondary);
  font-size: 14px;
}

.popularity {
  color: var(--primary-color);
  font-weight: 600;
  font-size: 14px;
}

/* Mobile-specific optimizations */
@media (max-width: 768px) {
  .chart-area {
    height: 320px;
  }
  
  .music-chart-container {
    padding: 16px;
  }
  
  .chart-header h3 {
    font-size: 16px;
  }
  
  .chart-controls {
    gap: 6px;
  }
  
  .chart-type-btn {
    min-width: 44px;
    min-height: 44px;
    padding: 6px 10px;
  }
}

@media (max-width: 480px) {
  .chart-area {
    height: 280px;
  }
  
  .music-chart-container {
    padding: 12px;
  }
  
  .chart-header {
    margin-bottom: 12px;
  }
  
  .chart-header h3 {
    font-size: 15px;
  }
  
  .chart-type-btn {
    min-width: 42px;
    min-height: 42px;
    font-size: 14px;
  }
}

/* Touch-specific improvements */
@media (pointer: coarse) {
  .chart-type-btn {
    min-width: 48px;
    min-height: 48px;
  }
  
  .chart-type-btn:active {
    transform: scale(0.95);
  }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .music-chart-container {
    border: 2px solid var(--text-primary);
  }
  
  .chart-type-btn {
    border: 1px solid var(--text-primary);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  .chart-type-btn {
    transition: none;
  }
  
  .chart-area {
    transition: none;
  }
}
</style> 