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
  textStyle: { color: '#1d1d1f' },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6',
    textStyle: { color: '#1d1d1f' }
  },
  xAxis: {
    type: 'category',
    data: props.data.map(item => item.year),
    axisLine: { lineStyle: { color: '#d1d1d6' } },
    axisLabel: { color: '#86868b', fontSize: 12 }
  },
  yAxis: { show: false },
  series: [{
    type: 'line',
    data: props.data.map((item, index) => ({
      value: index + 1,
      name: item.album,
      itemStyle: { color: '#007AFF' }
    })),
    lineStyle: { color: '#007AFF', width: 3 },
    symbol: 'circle',
    symbolSize: 8,
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
  textStyle: { color: '#1d1d1f' },
  tooltip: {
    trigger: 'axis',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6'
  },
  xAxis: {
    type: 'category',
    data: props.data.map(item => item.album.length > 20 ? item.album.slice(0, 20) + '...' : item.album),
    axisLabel: { 
      rotate: 45, 
      color: '#86868b', 
      fontSize: 10 
    },
    axisLine: { lineStyle: { color: '#d1d1d6' } }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#86868b', fontSize: 12 },
    splitLine: { lineStyle: { color: '#f5f5f5' } }
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
        }
      }
    })),
    barWidth: '60%',
    borderRadius: [4, 4, 0, 0]
  }]
})

const getGenreOption = () => ({
  backgroundColor: 'transparent',
  textStyle: { color: '#1d1d1f' },
  tooltip: {
    trigger: 'item',
    backgroundColor: '#ffffff',
    borderColor: '#d1d1d6'
  },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    center: ['50%', '50%'],
    data: getGenreData(),
    itemStyle: {
      borderRadius: 8,
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      color: '#1d1d1f',
      fontSize: 12
    }
  }]
})

const getGenreData = () => {
  const genres = {}
  props.data.forEach(item => {
    const genre = item.genre || 'Pop'
    genres[genre] = (genres[genre] || 0) + 1
  })
  
  const colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE']
  
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
  if (myChart) myChart.resize()
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
  height: 300px;
}
</style> 