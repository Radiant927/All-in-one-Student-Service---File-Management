<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">工作台</h2>
      <el-button type="primary" :icon="CirclePlus" @click="router.push({ name: 'transfer-new' })">
        发起转交
      </el-button>
    </div>

    <el-row :gutter="16" class="card-gap">
      <el-col v-for="card in cards" :key="card.key" :xs="12" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card" @click="card.onClick && card.onClick()">
          <div class="stat-label">{{ card.label }}</div>
          <div class="stat-value" :style="{ color: card.color }">
            {{ stats[card.key] ?? '—' }}
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :xs="24" :md="14">
        <el-card v-loading="trendLoading" class="card-gap">
          <template #header>近 {{ TREND_DAYS }} 天交接统计</template>
          <div ref="chartRef" class="chart"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="10">
        <el-card v-loading="busLoading" class="card-gap">
          <template #header>
            <div class="bus-header">
              <span>今日校车班次</span>
              <el-radio-group v-model="busDirection" size="small">
                <el-radio-button value="out">发出</el-radio-button>
                <el-radio-button value="in">到达</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <el-empty v-if="!visibleBuses.length" description="暂无班次" :image-size="70" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="bus in visibleBuses"
              :key="bus.id"
              :timestamp="`${bus.depart_time} → ${bus.arrive_time}`"
              placement="top"
              :type="isPast(bus.depart_time) ? 'info' : 'primary'"
            >
              <div class="bus-name">{{ bus.name }}</div>
              <div class="text-muted bus-route">
                {{ campusLabel(bus.from_campus) }} → {{ campusLabel(bus.to_campus) }}
              </div>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { CirclePlus } from '@element-plus/icons-vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

import * as statsApi from '@/api/stats'
import * as busesApi from '@/api/buses'
import { useUserStore } from '@/stores/user'
import { campusLabel } from '@/utils/dict'

echarts.use([LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

const TREND_DAYS = 7

const router = useRouter()
const userStore = useUserStore()

const stats = ref({})
const trendLoading = ref(false)
const busLoading = ref(false)
const buses = ref([])
const busDirection = ref('out')

const chartRef = ref()
let chart = null

const cards = computed(() => [
  {
    key: 'pending_receive',
    label: '待我接收',
    color: '#f56c6c',
    onClick: () => router.push({ name: 'transfers', query: { role: 'received', status: 'pending' } }),
  },
  {
    key: 'my_pending_confirm',
    label: '我发起的待确认',
    color: '#e6a23c',
    onClick: () => router.push({ name: 'transfers', query: { role: 'sent', status: 'pending' } }),
  },
  {
    key: 'total_this_month',
    label: '本月转交总数',
    color: '#409eff',
    onClick: () => router.push({ name: 'transfers' }),
  },
  {
    key: 'confirmed_this_month',
    label: '本月已确认',
    color: '#67c23a',
    onClick: () => router.push({ name: 'transfers', query: { status: 'confirmed' } }),
  },
])

const visibleBuses = computed(() => {
  if (!userStore.campus) return buses.value
  return buses.value.filter((bus) =>
    busDirection.value === 'out'
      ? bus.from_campus === userStore.campus
      : bus.to_campus === userStore.campus,
  )
})

/** 班次时间是 "08:00" 这样的字符串，跟当前时间比一下好把已发车的置灰 */
function isPast(departTime) {
  const [hour, minute] = String(departTime).split(':').map(Number)
  const now = new Date()
  return now.getHours() * 60 + now.getMinutes() > hour * 60 + minute
}

function renderChart(trend) {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增转交', '确认签收'] },
    grid: { left: 40, right: 20, top: 40, bottom: 30 },
    xAxis: {
      type: 'category',
      data: trend.map((item) => item.date.slice(5)),
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '新增转交',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.12 },
        itemStyle: { color: '#409eff' },
        data: trend.map((item) => item.total),
      },
      {
        name: '确认签收',
        type: 'line',
        smooth: true,
        itemStyle: { color: '#67c23a' },
        data: trend.map((item) => item.confirmed),
      },
    ],
  })
}

const resizeChart = () => chart?.resize()

async function loadStats() {
  stats.value = await statsApi.getDashboard()
}

async function loadTrend() {
  trendLoading.value = true
  try {
    const trend = await statsApi.getTrend(TREND_DAYS)
    await nextTick()
    renderChart(trend)
  } finally {
    trendLoading.value = false
  }
}

async function loadBuses() {
  busLoading.value = true
  try {
    buses.value = await busesApi.listBuses({ only_active: true })
  } finally {
    busLoading.value = false
  }
}

onMounted(() => {
  loadStats()
  loadTrend()
  loadBuses()
  window.addEventListener('resize', resizeChart)
})

// 侧边栏折叠会改变容器宽度，图表要跟着重算
watch(visibleBuses, () => nextTick(resizeChart))

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.stat-card {
  cursor: pointer;
  margin-bottom: 16px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.stat-value {
  margin-top: 6px;
  font-size: 28px;
  font-weight: 600;
  line-height: 1.2;
}

.chart {
  height: 300px;
}

.bus-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.bus-name {
  font-weight: 500;
}

.bus-route {
  font-size: 12px;
}
</style>
