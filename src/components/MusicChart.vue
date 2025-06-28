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
import { ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: 'Artist Timeline' },
  data: { type: Array, default: () => [] }
})

const chartContainer = ref(null)
const currentType = ref('timeline')
let myChart = null

const chartTypes = [
  { value: 'timeline', icon: '📅' },
  { value: 'popularity', icon: '⭐' },
  { value: 'genre', icon: '🎵' }
]

const initChart = () => {
  if (chartContainer.value) {
    myChart = echarts.init(chartContainer.value)
    updateChart()
    window.addEventListener('resize', resizeChart)
  }
}

const updateChart = () => {
  if (!myChart || !props.data.length) return

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
  
  myChart.setOption(option)
}

const getTimelineOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { 
    color: '#1d1d1f',
    fontSize: 14,
    fontWeight: 500
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: 16
    },
    formatter: function(params) {
      const data = params[0]
      const albumData = props.data[data.dataIndex]
      return `
        <div style="padding: 8px;">
          <strong style="font-size: 16px;">${albumData.album}</strong><br/>
          <span style="color: #666; font-size: 14px;">Year: ${albumData.year}</span><br/>
          <span style="color: #666; font-size: 14px;">Genre: ${albumData.genre}</span><br/>
          <span style="color: #007AFF; font-size: 14px;">Popularity: ${albumData.popularity}/100</span>
        </div>
      `
    }
  },
  grid: {
    left: '15%',
    right: '15%',
    top: '15%',
    bottom: '25%'
  },
  xAxis: {
    type: 'category',
    data: props.data.map(item => item.year),
    axisLine: { 
      lineStyle: { color: '#d1d1d6', width: 2 }
    },
    axisLabel: { 
      color: '#86868b', 
      fontSize: 16,
      fontWeight: 500,
      interval: 0,
      rotate: 0,
      margin: 12
    },
    axisTick: {
      show: true,
      length: 6,
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
      width: 4
    },
    symbol: 'circle',
    symbolSize: 12,
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

const getPopularityOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { 
    color: '#1d1d1f',
    fontSize: 14,
    fontWeight: 500
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: 16
    },
    formatter: function(params) {
      const data = params[0]
      const albumData = props.data[data.dataIndex]
      return `
        <div style="padding: 8px;">
          <strong style="font-size: 16px;">${albumData.album}</strong><br/>
          <span style="color: #666; font-size: 14px;">${albumData.year} • ${albumData.genre}</span><br/>
          <span style="color: #34C759; font-size: 16px; font-weight: 600;">⭐ ${albumData.popularity}/100</span>
        </div>
      `
    }
  },
  grid: {
    left: '5%',
    right: '5%',
    top: '15%',
    bottom: '35%'
  },
  xAxis: {
    type: 'category',
    data: props.data.map(item => {
      // Truncate long album names for mobile
      return item.album.length > 12 ? item.album.slice(0, 12) + '..' : item.album
    }),
    axisLabel: { 
      rotate: 45, 
      color: '#86868b', 
      fontSize: 12,
      fontWeight: 500,
      interval: 0,
      margin: 8
    },
    axisLine: { 
      lineStyle: { color: '#d1d1d6', width: 2 }
    }
  },
  yAxis: {
    type: 'value',
    axisLabel: { 
      color: '#86868b', 
      fontSize: 14,
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
    barWidth: '70%'
  }]
})

const getGenreOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { 
    color: '#1d1d1f',
    fontSize: 14,
    fontWeight: 500
  },
  tooltip: {
    trigger: 'item',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { 
      color: '#1d1d1f',
      fontSize: 16
    },
    formatter: function(params) {
      return `
        <div style="padding: 8px;">
          <strong style="font-size: 16px;">${params.name}</strong><br/>
          <span style="color: #666; font-size: 14px;">${params.value} albums</span><br/>
          <span style="color: #007AFF; font-size: 14px;">${params.percent}% of discography</span>
        </div>
      `
    }
  },
  legend: {
    show: false  // Hide legend to save space on mobile
  },
  series: [{
    type: 'pie',
    radius: ['30%', '75%'],
    center: ['50%', '50%'],
    data: getGenreData(),
    itemStyle: {
      borderRadius: 8,
      borderColor: '#fff',
      borderWidth: 3
    },
    label: {
      show: true,
      position: 'outside',
      color: '#1d1d1f',
      fontSize: 14,
      fontWeight: 600,
      formatter: function(params) {
        // Show abbreviated genre names for mobile
        const shortName = params.name.length > 8 ? 
          params.name.split(' ')[0] : params.name
        return `${shortName}\n${params.value}`
      }
    },
    labelLine: {
      show: true,
      length: 15,
      length2: 10,
      lineStyle: {
        color: '#d1d1d6',
        width: 2
      }
    },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.2)'
      }
    }
  }]
})

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
  updateChart()
}

const resizeChart = () => {
  if (myChart) {
    setTimeout(() => {
      myChart.resize()
    }, 100)
  }
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
    window.removeEventListener('resize', resizeChart)
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
  min-width: 44px;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-type-btn.active {
  background: var(--primary-color);
  transform: scale(1.05);
}

.chart-area {
  width: 100%;
  height: 350px;
  position: relative;
}

/* Mobile-specific chart optimizations */
@media (max-width: 480px) {
  .chart-area {
    height: 320px;
  }
  
  .music-chart-container {
    padding: 16px;
  }
  
  .chart-header h3 {
    font-size: 16px;
  }
}
</style> 