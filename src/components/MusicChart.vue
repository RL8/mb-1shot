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
let myChart = null

const chartTypes = [
  { value: 'timeline', icon: '' },
  { value: 'popularity', icon: '' },
  { value: 'genre', icon: '' }
]

// Simple mobile detection
const isMobile = () => window.innerWidth < 768

// Get responsive font size
const getResponsiveFontSize = (baseSize) => {
  return isMobile() ? Math.max(16, baseSize) : baseSize
}

// Initialize chart
const initChart = () => {
  if (!chartContainer.value) return
  
  try {
    // Create chart instance
    myChart = echarts.init(chartContainer.value)
    
    // Set initial chart
    updateChart()
    
    // Add resize listener
    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('Failed to initialize chart:', error)
  }
}

// Update chart with current data and type
const updateChart = () => {
  if (!myChart) return
  
  try {
    // Use fallback data if props.data is empty
    const chartData = props.data && props.data.length > 0 ? props.data : getDefaultData()
    
    let option = {}
    
    switch (currentType.value) {
      case 'timeline':
        option = getTimelineOption(chartData)
        break
      case 'popularity':
        option = getPopularityOption(chartData)
        break
      case 'genre':
        option = getGenreOption(chartData)
        break
    }
    
    myChart.setOption(option, true)
    
    // Resize chart to fit container
    nextTick(() => {
      if (myChart) {
        myChart.resize()
      }
    })
  } catch (error) {
    console.error('Failed to update chart:', error)
  }
}

// Default data fallback
const getDefaultData = () => [
  { album: 'Taylor Swift', year: '2006', genre: 'Country', popularity: 75 },
  { album: 'Fearless', year: '2008', genre: 'Country', popularity: 85 },
  { album: 'Speak Now', year: '2010', genre: 'Country', popularity: 80 }
]

// Timeline chart option
const getTimelineOption = (data) => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: getResponsiveFontSize(14)
    },
    formatter: function(params) {
      const item = data[params[0].dataIndex]
      return `
        <div style="padding: 8px;">
          <strong>${item.album}</strong><br/>
          Year: ${item.year}<br/>
          Genre: ${item.genre}<br/>
          Popularity: ${item.popularity}/100
        </div>
      `
    }
  },
  grid: {
    left: '10%',
    right: '10%',
    top: '15%',
    bottom: isMobile() ? '25%' : '20%'
  },
  xAxis: {
    type: 'category',
    data: data.map(item => item.year),
    axisLabel: { 
      color: '#86868b', 
      fontSize: getResponsiveFontSize(14),
      rotate: isMobile() ? 30 : 0,
      interval: isMobile() ? 'auto' : 0
    },
    axisLine: { 
      lineStyle: { color: '#d1d1d6' }
    }
  },
  yAxis: { 
    show: false
  },
  series: [{
    type: 'line',
    data: data.map((item, index) => index + 1),
    lineStyle: { 
      color: '#007AFF', 
      width: 3
    },
    symbol: 'circle',
    symbolSize: isMobile() ? 10 : 8,
    smooth: true,
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

// Popularity chart option
const getPopularityOption = (data) => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: getResponsiveFontSize(14)
    },
    formatter: function(params) {
      const item = data[params[0].dataIndex]
      return `
        <div style="padding: 8px;">
          <strong>${item.album}</strong><br/>
          ${item.year}  ${item.genre}<br/>
           ${item.popularity}/100
        </div>
      `
    }
  },
  grid: {
    left: '8%',
    right: '8%',
    top: '15%',
    bottom: isMobile() ? '35%' : '25%'
  },
  xAxis: {
    type: 'category',
    data: data.map(item => {
      const maxLength = isMobile() ? 8 : 12
      return item.album.length > maxLength ? 
        item.album.slice(0, maxLength) + '..' : item.album
    }),
    axisLabel: { 
      rotate: isMobile() ? 45 : 30, 
      color: '#86868b', 
      fontSize: getResponsiveFontSize(12),
      interval: 0
    },
    axisLine: { 
      lineStyle: { color: '#d1d1d6' }
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: { 
      color: '#86868b', 
      fontSize: getResponsiveFontSize(12)
    },
    splitLine: { 
      lineStyle: { color: '#f5f5f5' }
    },
    axisLine: { show: false }
  },
  series: [{
    type: 'bar',
    data: data.map(item => ({
      value: item.popularity || 50,
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
    barWidth: isMobile() ? '70%' : '60%'
  }]
})

// Genre chart option
const getGenreOption = (data) => {
  const genres = {}
  data.forEach(item => {
    const genre = item.genre || 'Pop'
    genres[genre] = (genres[genre] || 0) + 1
  })
  
  const colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE']
  const genreData = Object.entries(genres).map(([genre, count], index) => ({
    value: count,
    name: genre,
    itemStyle: { color: colors[index % colors.length] }
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: '#ffffff',
      borderColor: '#d1d1d6',
      textStyle: { 
        color: '#1d1d1f',
        fontSize: getResponsiveFontSize(14)
      },
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      show: !isMobile(), // Hide legend on mobile to save space
      bottom: '5%',
      textStyle: {
        color: '#86868b',
        fontSize: getResponsiveFontSize(12)
      }
    },
    series: [{
      name: 'Genres',
      type: 'pie',
      radius: isMobile() ? '60%' : '50%',
      center: ['50%', '45%'],
      data: genreData,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        show: !isMobile(), // Simplified labels on mobile
        fontSize: getResponsiveFontSize(12),
        color: '#86868b'
      },
      labelLine: {
        show: !isMobile()
      }
    }]
  }
}

// Handle chart type change
const changeChartType = (type) => {
  currentType.value = type
  updateChart()
}

// Handle window resize
const handleResize = () => {
  if (myChart) {
    myChart.resize()
  }
}

// Watch for data changes
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// Lifecycle hooks
onMounted(() => {
  nextTick(() => {
    initChart()
  })
})

onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
    myChart = null
  }
  window.removeEventListener('resize', handleResize)
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
  padding: 10px 14px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-type-btn.active {
  background: var(--primary-color);
  color: white;
  transform: scale(1.05);
}

.chart-type-btn:hover {
  background: var(--primary-color);
  color: white;
  opacity: 0.8;
}

.chart-area {
  width: 100%;
  height: 400px;
  position: relative;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .chart-area {
    height: 350px;
  }
  
  .music-chart-container {
    padding: 16px;
  }
  
  .chart-header h3 {
    font-size: 16px;
  }
  
  .chart-type-btn {
    min-width: 40px;
    min-height: 40px;
    padding: 8px 12px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .chart-area {
    height: 300px;
  }
  
  .music-chart-container {
    padding: 12px;
  }
  
  .chart-header h3 {
    font-size: 15px;
  }
  
  .chart-type-btn {
    min-width: 38px;
    min-height: 38px;
    padding: 6px 10px;
  }
}
</style>
