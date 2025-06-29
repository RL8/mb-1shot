<template>
  <div class="treemap-sunburst-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls">
        <button 
          @click="switchToTreemap"
          :class="{ active: currentType === 'treemap' }"
          class="chart-type-btn"
        >
          🌳 Treemap
        </button>
        <button 
          @click="switchToSunburst"
          :class="{ active: currentType === 'sunburst' }"
          class="chart-type-btn"
        >
          ☀️ Sunburst
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
  title: { type: String, default: 'Treemap-Sunburst Transition' },
  data: { type: Array, default: () => [] }
})

const chartContainer = ref(null)
const currentType = ref('treemap')
let myChart = null

// Sample data structure for treemap/sunburst
const getDefaultData = () => ({
  name: 'Root',
  children: [
    {
      name: 'Technology',
      value: 40,
      children: [
        { name: 'JavaScript', value: 15 },
        { name: 'Python', value: 12 },
        { name: 'Java', value: 8 },
        { name: 'C++', value: 5 }
      ]
    },
    {
      name: 'Design',
      value: 30,
      children: [
        { name: 'UI/UX', value: 15 },
        { name: 'Graphic Design', value: 10 },
        { name: 'Branding', value: 5 }
      ]
    },
    {
      name: 'Marketing',
      value: 20,
      children: [
        { name: 'Digital Marketing', value: 12 },
        { name: 'Content', value: 8 }
      ]
    },
    {
      name: 'Sales',
      value: 10,
      children: [
        { name: 'B2B', value: 6 },
        { name: 'B2C', value: 4 }
      ]
    }
  ]
})

// Initialize chart
const initChart = () => {
  if (!chartContainer.value) return
  
  try {
    myChart = echarts.init(chartContainer.value)
    updateChart()
    window.addEventListener('resize', handleResize)
  } catch (error) {
    console.error('Failed to initialize chart:', error)
  }
}

// Handle resize
const handleResize = () => {
  if (myChart) {
    myChart.resize()
  }
}

// Switch to treemap
const switchToTreemap = () => {
  currentType.value = 'treemap'
  updateChart()
}

// Switch to sunburst
const switchToSunburst = () => {
  currentType.value = 'sunburst'
  updateChart()
}

// Update chart with current data and type
const updateChart = () => {
  if (!myChart) return
  
  try {
    const chartData = props.data && props.data.length > 0 ? props.data[0] : getDefaultData()
    
    let option = {}
    
    if (currentType.value === 'treemap') {
      option = getTreemapOption(chartData)
    } else {
      option = getSunburstOption(chartData)
    }
    
    myChart.setOption(option, true)
    
    nextTick(() => {
      if (myChart) {
        myChart.resize()
      }
    })
  } catch (error) {
    console.error('Failed to update chart:', error)
  }
}

// Treemap chart option
const getTreemapOption = (data) => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      return `
        <div style="padding: 8px;">
          <strong>${params.name}</strong><br/>
          Value: ${params.value || 'N/A'}
        </div>
      `
    }
  },
  series: [{
    type: 'treemap',
    id: 'treemap-series',
    animationDurationUpdate: 1000,
    roam: false,
    nodeClick: false,
    data: [data],
    universalTransition: true,
    label: {
      show: true,
      formatter: '{b}'
    },
    itemStyle: {
      borderColor: '#fff',
      borderWidth: 2
    },
    levels: [
      {
        itemStyle: {
          borderColor: '#777',
          borderWidth: 0,
          gapWidth: 1
        }
      },
      {
        itemStyle: {
          gapWidth: 1
        }
      },
      {
        colorSaturation: [0.35, 0.5],
        itemStyle: {
          gapWidth: 1,
          borderColorSaturation: 0.6
        }
      }
    ]
  }]
})

// Sunburst chart option
const getSunburstOption = (data) => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: function(params) {
      return `
        <div style="padding: 8px;">
          <strong>${params.name}</strong><br/>
          Value: ${params.value || 'N/A'}
        </div>
      `
    }
  },
  series: [{
    type: 'sunburst',
    id: 'sunburst-series',
    animationDurationUpdate: 1000,
    radius: [0, '90%'],
    data: [data],
    universalTransition: true,
    itemStyle: {
      borderColor: '#fff',
      borderWidth: 2
    },
    label: {
      show: true,
      rotate: 'radial'
    },
    levels: [
      {},
      {
        r0: '15%',
        r: '35%',
        itemStyle: {
          borderWidth: 2
        },
        label: {
          rotate: 'tangential'
        }
      },
      {
        r0: '35%',
        r: '70%',
        label: {
          position: 'outside',
          padding: 3,
          silent: false
        }
      },
      {
        r0: '70%',
        r: '72%',
        label: {
          position: 'outside',
          padding: 3,
          silent: false
        },
        itemStyle: {
          borderWidth: 3
        }
      }
    ]
  }]
})

// Lifecycle hooks
onMounted(() => {
  initChart()
})

onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
    window.removeEventListener('resize', handleResize)
  }
})

// Watch for data changes
watch(() => props.data, () => {
  updateChart()
}, { deep: true })
</script>

<style scoped>
.treemap-sunburst-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chart-type-btn {
  padding: 8px 16px;
  border: 2px solid #007AFF;
  background: rgba(255, 255, 255, 0.9);
  color: #007AFF;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.chart-type-btn:hover {
  background: rgba(0, 122, 255, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.chart-type-btn.active {
  background: #007AFF;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.4);
}

.chart-area {
  width: 100%;
  height: calc(100% - 80px);
  min-height: 350px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  backdrop-filter: blur(5px);
}

@media (max-width: 768px) {
  .treemap-sunburst-container {
    padding: 15px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-header h3 {
    font-size: 1.3rem;
  }
  
  .chart-controls {
    width: 100%;
    justify-content: center;
  }
  
  .chart-type-btn {
    flex: 1;
    min-width: 120px;
  }
}
</style> 