<template>
  <div class="space-y-4 mt-8 pb-8">
    <!-- Header with Admin Button -->
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-white">📊 学習データ</h2>
      <button
        v-if="userStore.isAdmin"
        @click="emit('admin')"
        class="text-white/70 hover:text-white text-sm underline"
      >
        管理者メニュー
      </button>
    </div>

    <!-- Tab Navigation -->
    <div class="flex gap-2 bg-black/20 p-1 rounded-xl">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        :class="[
          'flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-all',
          activeTab === tab.key 
            ? 'bg-white text-indigo-600 shadow-sm' 
            : 'text-white/70 hover:text-white'
        ]"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- Weekly View -->
    <div v-if="activeTab === 'weekly'">
      <GlassPanel>
        <!-- Week Navigation -->
        <div class="flex justify-between items-center mb-4">
          <button 
            @click="weekOffset++"
            class="p-2 rounded-lg bg-indigo-100 text-indigo-600 hover:bg-indigo-200 active:scale-95 transition-all"
          >
            <span class="text-lg">←</span>
          </button>
          <h3 class="font-bold text-gray-700">
            {{ weekLabel }}
          </h3>
          <button 
            @click="weekOffset = Math.max(0, weekOffset - 1)"
            :disabled="weekOffset === 0"
            :class="[
              'p-2 rounded-lg transition-all',
              weekOffset === 0 
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200 active:scale-95'
            ]"
          >
            <span class="text-lg">→</span>
          </button>
        </div>

        <!-- Weekly Bar Chart -->
        <div class="h-48 flex items-end gap-2 pt-6">
          <div
            v-for="(item, idx) in currentWeekData"
            :key="idx"
            class="flex-1 flex flex-col items-center min-w-0"
          >
            <!-- Bar -->
            <div class="w-full relative">
              <div 
                class="w-full rounded-t-lg transition-all duration-500 ease-out"
                :class="getBarGradient(item.minutes)"
                :style="{ height: getBarHeight(item.minutes) + 'px', minHeight: item.minutes > 0 ? '8px' : '4px' }"
              >
                <!-- Minutes label on top -->
                <span 
                  v-if="item.minutes > 0"
                  class="absolute -top-5 left-1/2 -translate-x-1/2 text-xs font-bold text-indigo-600 whitespace-nowrap"
                >
                  {{ item.minutes }}分
                </span>
              </div>
            </div>
            <!-- Day Label -->
            <p 
              class="text-xs mt-2 font-medium"
              :class="item.isToday ? 'text-indigo-600' : 'text-gray-500'"
            >
              {{ item.day }}
            </p>
          </div>
        </div>

        <!-- Weekly Summary -->
        <div class="mt-4 pt-4 border-t border-gray-200 flex justify-around text-center">
          <div>
            <p class="text-2xl font-bold text-indigo-600">{{ weeklyTotal }}分</p>
            <p class="text-xs text-gray-500">週合計</p>
          </div>
          <div>
            <p class="text-2xl font-bold text-green-600">{{ weeklyAverage }}分</p>
            <p class="text-xs text-gray-500">平均/日</p>
          </div>
        </div>
      </GlassPanel>
    </div>

    <!-- Monthly View -->
    <div v-if="activeTab === 'monthly'">
      <GlassPanel>
        <!-- Month Navigation -->
        <div class="flex justify-between items-center mb-4">
          <button 
            @click="monthOffset++"
            class="p-2 rounded-lg bg-indigo-100 text-indigo-600 hover:bg-indigo-200 active:scale-95 transition-all"
          >
            <span class="text-lg">←</span>
          </button>
          <h3 class="font-bold text-gray-700">
            {{ monthLabel }}
          </h3>
          <button 
            @click="monthOffset = Math.max(0, monthOffset - 1)"
            :disabled="monthOffset === 0"
            :class="[
              'p-2 rounded-lg transition-all',
              monthOffset === 0 
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200 active:scale-95'
            ]"
          >
            <span class="text-lg">→</span>
          </button>
        </div>

        <!-- Monthly Stacked Bar Chart (by week) -->
        <div class="h-52 flex items-end gap-3 pt-6">
          <div
            v-for="(week, idx) in currentMonthWeeks"
            :key="idx"
            class="flex-1 flex flex-col items-center"
          >
            <!-- Stacked Bar -->
            <div class="w-full relative flex flex-col-reverse">
              <div 
                v-for="(seg, sidx) in week.segments"
                :key="sidx"
                class="w-full first:rounded-t-lg transition-all duration-500"
                :style="{ 
                  height: getStackedHeight(seg.minutes, week.total) + 'px',
                  backgroundColor: seg.color,
                  minHeight: seg.minutes > 0 ? '4px' : '0'
                }"
              />
              <!-- Total on top -->
              <span 
                v-if="week.total > 0"
                class="absolute -top-5 left-1/2 -translate-x-1/2 text-xs font-bold text-gray-700 whitespace-nowrap"
              >
                {{ Math.round(week.total / 60 * 10) / 10 }}h
              </span>
            </div>
            <!-- Week Label -->
            <p class="text-xs mt-2 text-gray-500">{{ week.label }}</p>
          </div>
        </div>

        <!-- Monthly Legend -->
        <div class="mt-4 pt-4 border-t border-gray-200">
          <div class="flex flex-wrap gap-3 justify-center">
            <div 
              v-for="(sub, idx) in subjectLegend"
              :key="idx"
              class="flex items-center gap-1.5"
            >
              <div 
                class="w-3 h-3 rounded-full"
                :style="{ backgroundColor: sub.color }"
              />
              <span class="text-xs text-gray-600">{{ sub.name }}</span>
            </div>
          </div>
          <div class="text-center mt-3">
            <p class="text-2xl font-bold text-indigo-600">{{ monthlyTotal }}分</p>
            <p class="text-xs text-gray-500">月合計 ({{ Math.round(monthlyTotal / 60 * 10) / 10 }}時間)</p>
          </div>
        </div>
      </GlassPanel>
    </div>

    <!-- Subject Breakdown (always visible) -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📚 科目別時間</h3>
      <SubjectChart :data="subjectData" />
    </GlassPanel>

    <!-- Recent Activity -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">🕐 最近の記録</h3>
      <div v-if="recentActivity.length === 0" class="text-center text-gray-500 py-4">
        記録がありません
      </div>
      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div 
          v-for="(item, idx) in recentActivity" 
          :key="idx"
          class="flex justify-between items-center py-2 border-b last:border-0 border-gray-100"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-2 h-8 rounded-full"
              :style="{ backgroundColor: getSubjectColor(item.subject) }"
            />
            <div>
              <p class="font-medium text-gray-800">{{ item.subject }}</p>
              <p class="text-xs text-gray-500">{{ item.date }}</p>
            </div>
          </div>
          <span class="font-bold text-indigo-600">{{ item.minutes }}分</span>
        </div>
      </div>
    </GlassPanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import GlassPanel from '@/components/common/GlassPanel.vue'
import SubjectChart from './SubjectChart.vue'

const userStore = useUserStore()
const emit = defineEmits(['admin'])

// Tabs
const tabs = [
  { key: 'weekly', label: '週間', icon: '📈' },
  { key: 'monthly', label: '月別', icon: '📊' }
]
const activeTab = ref('weekly')

// Data
const allData = ref([])
const subjectData = ref([])
const recentActivity = ref([])

// Navigation offsets
const weekOffset = ref(0)
const monthOffset = ref(0)

// Subject colors
const subjectColors = {
  '国語': '#FF6B6B',
  '数学': '#4D96FF',
  '英語': '#FFD93D',
  '理科': '#6BCB77',
  '社会': '#9D4EDD',
  'その他': '#95A5A6',
  '勉強': '#7C3AED'
}

const subjectLegend = computed(() => {
  return Object.entries(subjectColors).map(([name, color]) => ({ name, color }))
})

const getSubjectColor = (subject) => {
  return subjectColors[subject] || subjectColors['その他']
}

// Week calculations
const weekLabel = computed(() => {
  if (weekOffset.value === 0) return '今週'
  if (weekOffset.value === 1) return '先週'
  
  const today = new Date()
  const startOfWeek = new Date(today)
  const dayOfWeek = today.getDay() || 7
  startOfWeek.setDate(today.getDate() - dayOfWeek + 1 - (weekOffset.value * 7))
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)
  
  return `${startOfWeek.getMonth() + 1}/${startOfWeek.getDate()} - ${endOfWeek.getMonth() + 1}/${endOfWeek.getDate()}`
})

const currentWeekData = computed(() => {
  const today = new Date()
  const days = ['月', '火', '水', '木', '金', '土', '日']
  const result = []
  
  // Get Monday of the target week
  const targetMonday = new Date(today)
  const dayOfWeek = today.getDay() || 7 // Sunday = 7
  targetMonday.setDate(today.getDate() - dayOfWeek + 1 - (weekOffset.value * 7))
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(targetMonday)
    date.setDate(targetMonday.getDate() + i)
    const dateStr = date.toISOString().split('T')[0]
    
    // Find matching data - sum all entries for same date
    const dayMinutes = allData.value
      .filter(d => d.date === dateStr)
      .reduce((sum, d) => sum + (d.minutes || 0), 0)
    
    const isToday = date.toDateString() === today.toDateString()
    
    result.push({
      day: days[i],
      date: dateStr,
      minutes: dayMinutes,
      isToday
    })
  }
  
  return result
})

const weeklyTotal = computed(() => {
  return currentWeekData.value.reduce((sum, d) => sum + d.minutes, 0)
})

const weeklyAverage = computed(() => {
  return Math.round(weeklyTotal.value / 7)
})

// Month calculations
const monthLabel = computed(() => {
  const today = new Date()
  const targetDate = new Date(today.getFullYear(), today.getMonth() - monthOffset.value, 1)
  return `${targetDate.getFullYear()}年${targetDate.getMonth() + 1}月`
})

const currentMonthWeeks = computed(() => {
  const today = new Date()
  const targetMonth = today.getMonth() - monthOffset.value
  const targetYear = today.getFullYear() + Math.floor(targetMonth / 12)
  const actualMonth = ((targetMonth % 12) + 12) % 12
  
  const firstDay = new Date(targetYear, actualMonth, 1)
  const lastDay = new Date(targetYear, actualMonth + 1, 0)
  
  const weeks = []
  let currentWeekStart = new Date(firstDay)
  
  // Adjust to Monday
  const dayOfWeek = currentWeekStart.getDay() || 7
  if (dayOfWeek !== 1) {
    currentWeekStart.setDate(currentWeekStart.getDate() - dayOfWeek + 1)
  }
  
  let weekNum = 1
  while (currentWeekStart <= lastDay || weeks.length < 4) {
    const weekEnd = new Date(currentWeekStart)
    weekEnd.setDate(currentWeekStart.getDate() + 6)
    
    // Calculate totals by subject for this week
    const subjectTotals = {}
    for (let d = new Date(currentWeekStart); d <= weekEnd; d.setDate(d.getDate() + 1)) {
      const dateStr = d.toISOString().split('T')[0]
      const dayEntries = allData.value.filter(item => item.date === dateStr)
      dayEntries.forEach(entry => {
        const subj = entry.subject || 'その他'
        subjectTotals[subj] = (subjectTotals[subj] || 0) + (entry.minutes || 0)
      })
    }
    
    const segments = Object.entries(subjectTotals).map(([subject, minutes]) => ({
      subject,
      minutes,
      color: getSubjectColor(subject)
    }))
    
    const total = segments.reduce((sum, s) => sum + s.minutes, 0)
    
    weeks.push({
      label: `W${weekNum}`,
      start: new Date(currentWeekStart),
      end: new Date(weekEnd),
      segments: segments.length > 0 ? segments : [{ subject: 'なし', minutes: 0, color: '#E5E7EB' }],
      total
    })
    
    currentWeekStart = new Date(currentWeekStart)
    currentWeekStart.setDate(currentWeekStart.getDate() + 7)
    weekNum++
    
    if (weeks.length >= 5) break
  }
  
  return weeks
})

const monthlyTotal = computed(() => {
  return currentMonthWeeks.value.reduce((sum, w) => sum + w.total, 0)
})

// Chart helpers
const maxWeeklyMinutes = computed(() => {
  return Math.max(...currentWeekData.value.map(d => d.minutes), 60)
})

const getBarHeight = (minutes) => {
  const maxHeight = 120
  return Math.max(4, (minutes / maxWeeklyMinutes.value) * maxHeight)
}

const getBarGradient = (minutes) => {
  if (minutes === 0) return 'bg-gray-200'
  if (minutes >= 60) return 'bg-gradient-to-t from-indigo-600 to-purple-500'
  if (minutes >= 30) return 'bg-gradient-to-t from-indigo-500 to-indigo-400'
  return 'bg-gradient-to-t from-indigo-400 to-indigo-300'
}

const maxMonthlyTotal = computed(() => {
  return Math.max(...currentMonthWeeks.value.map(w => w.total), 60)
})

const getStackedHeight = (minutes, total) => {
  const maxHeight = 140
  if (total === 0) return 4
  const totalHeight = (total / maxMonthlyTotal.value) * maxHeight
  return Math.max(0, (minutes / total) * totalHeight)
}

// Fetch data
const fetchData = async () => {
  if (!userStore.currentUserId) return
  
  try {
    const res = await fetch(`/api/user/${userStore.currentUserId}/stats`)
    const data = await res.json()
    
    // Store all data with dates for calculations
    if (data.weekly) {
      allData.value = data.weekly.map(d => ({
        date: d.date,
        minutes: d.minutes,
        day: d.day,
        subject: d.subject || 'その他'
      }))
    }
    
    subjectData.value = data.subject || []
    recentActivity.value = data.recent || []
    
  } catch (e) {
    console.error('Failed to fetch stats:', e)
  }
}

onMounted(() => {
  fetchData()
})
</script>
