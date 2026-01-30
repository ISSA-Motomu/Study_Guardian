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

        <!-- Weekly Stacked Bar Chart by Subject -->
        <div class="h-48 flex items-end gap-2 pt-6">
          <div
            v-for="(item, idx) in currentWeekData"
            :key="idx"
            class="flex-1 flex flex-col items-center min-w-0"
          >
            <!-- Stacked Bar -->
            <div class="w-full relative flex flex-col-reverse">
              <div 
                v-for="(seg, sidx) in item.segments"
                :key="sidx"
                class="w-full first:rounded-t-lg transition-all duration-500"
                :style="{ 
                  height: getWeeklyStackedHeight(seg.minutes, item.total) + 'px',
                  backgroundColor: seg.color,
                  minHeight: seg.minutes > 0 ? '4px' : '0'
                }"
              />
              <!-- Minutes label on top -->
              <span 
                v-if="item.total > 0"
                class="absolute -top-5 left-1/2 -translate-x-1/2 text-xs font-bold text-indigo-600 whitespace-nowrap"
              >
                {{ item.total }}分
              </span>
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

        <!-- Weekly Legend -->
        <div class="mt-3 flex flex-wrap gap-2 justify-center">
          <div 
            v-for="(sub, idx) in subjectLegend"
            :key="idx"
            class="flex items-center gap-1"
          >
            <div 
              class="w-2.5 h-2.5 rounded-full"
              :style="{ backgroundColor: sub.color }"
            />
            <span class="text-[10px] text-gray-600">{{ sub.name }}</span>
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

    <!-- Subject Breakdown - Weekly -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📚 今週の科目別時間</h3>
      <div v-if="weeklySubjectData.length === 0" class="text-center text-gray-500 py-4">
        今週の記録はありません
      </div>
      <SubjectChart v-else :data="weeklySubjectData" />
    </GlassPanel>

    <!-- Subject Breakdown - Monthly -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📆 今月の科目別時間</h3>
      <div v-if="monthlySubjectData.length === 0" class="text-center text-gray-500 py-4">
        今月の記録はありません
      </div>
      <SubjectChart v-else :data="monthlySubjectData" />
    </GlassPanel>

    <!-- Subject Breakdown - Total -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📊 累計科目別時間</h3>
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

    <!-- Global Activity Board -->
    <GlassPanel>
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-gray-700">🌍 みんなの活動</h3>
        <button @click="fetchGlobalActivity" class="text-xs text-blue-500 hover:text-blue-700">🔄 更新</button>
      </div>
      <div v-if="loadingActivity" class="text-center py-4">
        <span class="text-gray-400 animate-pulse">読み込み中...</span>
      </div>
      <div v-else-if="globalActivity.length === 0" class="text-center text-gray-500 py-4">
        活動履歴がありません
      </div>
      <div v-else class="space-y-2" :class="showAllActivity ? 'max-h-none' : 'max-h-72'" style="overflow-y: auto;">
        <div 
          v-for="(item, idx) in displayedActivity" 
          :key="idx"
          class="py-2 px-3 border-b last:border-0 border-gray-100 bg-gradient-to-r from-white to-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <!-- Icon -->
            <div class="text-2xl flex-shrink-0">
              {{ item.icon }}
            </div>
            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-bold text-indigo-600 truncate">{{ item.user_name }}</span>
                <span 
                  class="text-xs px-2 py-0.5 rounded-full"
                  :class="item.type === 'study' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'"
                >
                  {{ item.type === 'study' ? '勉強' : 'お手伝い' }}
                </span>
              </div>
              <p class="text-sm text-gray-600 truncate">{{ item.description }}</p>
              <p class="text-xs text-gray-400">{{ formatTimestamp(item.timestamp) }}</p>
            </div>
          </div>
          <!-- Comment (expandable) -->
          <div v-if="item.comment" class="mt-2 ml-10">
            <p class="text-xs text-gray-500 bg-gray-100 rounded-lg px-3 py-2 italic">
              💬 {{ item.comment }}
            </p>
          </div>
        </div>
      </div>
      <!-- Show More / Less Button -->
      <div v-if="globalActivity.length > 5" class="mt-3 text-center">
        <button 
          @click="showAllActivity = !showAllActivity"
          class="text-sm text-indigo-500 hover:text-indigo-700 font-medium"
        >
          {{ showAllActivity ? '▲ 閉じる' : '▼ もっと見る (' + globalActivity.length + '件)' }}
        </button>
      </div>
    </GlassPanel>

    <!-- Weekly Ranking -->
    <GlassPanel>
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-gray-700">🏆 週間XPランキング</h3>
        <button @click="fetchWeeklyRanking" class="text-xs text-blue-500 hover:text-blue-700">🔄 更新</button>
      </div>
      <div v-if="loadingRanking" class="text-center py-4">
        <span class="text-gray-400 animate-pulse">読み込み中...</span>
      </div>
      <div v-else-if="weeklyRanking.length === 0" class="text-center text-gray-500 py-4">
        ランキングデータがありません
      </div>
      <div v-else class="space-y-2">
        <div 
          v-for="(user, idx) in weeklyRanking" 
          :key="idx"
          :class="[
            'flex items-center gap-3 py-3 px-4 rounded-xl transition-all',
            idx === 0 ? 'bg-gradient-to-r from-yellow-50 to-amber-50 border-2 border-yellow-400' :
            idx === 1 ? 'bg-gradient-to-r from-gray-50 to-slate-100 border border-gray-300' :
            idx === 2 ? 'bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-300' :
            'bg-gray-50',
            user.user_id === userStore.currentUserId && 'ring-2 ring-indigo-400'
          ]"
        >
          <!-- Rank -->
          <div class="w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg"
            :class="[
              idx === 0 ? 'bg-yellow-400 text-yellow-900' :
              idx === 1 ? 'bg-gray-300 text-gray-700' :
              idx === 2 ? 'bg-orange-400 text-orange-900' :
              'bg-gray-200 text-gray-600'
            ]"
          >
            {{ idx === 0 ? '👑' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : user.rank }}
          </div>
          <!-- User Info -->
          <div class="flex-1 min-w-0">
            <p class="font-bold text-gray-800 truncate">
              {{ user.display_name }}
              <span v-if="user.user_id === userStore.currentUserId" class="text-xs text-indigo-500">(あなた)</span>
            </p>
            <p class="text-xs text-gray-500">Lv.{{ user.level || 1 }}</p>
          </div>
          <!-- XP -->
          <div class="text-right">
            <p class="font-bold text-lg" :class="idx < 3 ? 'text-amber-600' : 'text-gray-700'">
              {{ user.weekly_exp?.toLocaleString() || 0 }}
            </p>
            <p class="text-[10px] text-gray-400">XP</p>
          </div>
        </div>
      </div>
    </GlassPanel>

    <!-- Everyone's Goals (Horizontal Scroll) -->
    <GlassPanel>
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-gray-700">🎯 みんなの目標</h3>
        <button @click="fetchAllGoals" class="text-xs text-blue-500 hover:text-blue-700">🔄 更新</button>
      </div>
      <div v-if="loadingGoals" class="text-center py-4">
        <span class="text-gray-400 animate-pulse">読み込み中...</span>
      </div>
      <div v-else-if="allGoals.length === 0" class="text-center text-gray-500 py-4">
        目標がまだありません
      </div>
      <div v-else class="overflow-x-auto pb-2 -mx-4 px-4">
        <div class="flex gap-3" :style="{ width: 'max-content' }">
          <div 
            v-for="goal in allGoals" 
            :key="goal.id"
            class="w-64 flex-shrink-0 bg-gradient-to-br from-white to-gray-50 rounded-xl p-4 border border-gray-200 shadow-sm"
            :class="{ 'ring-2 ring-indigo-400': goal.user_id === userStore.currentUserId }"
          >
            <!-- User & Date -->
            <div class="flex justify-between items-start mb-2">
              <span class="text-sm font-bold text-indigo-600 truncate flex-1">
                {{ goal.user_name }}
              </span>
              <span 
                class="text-xs px-2 py-0.5 rounded-full flex-shrink-0 ml-2"
                :class="getDaysUntilClass(goal.target_date)"
              >
                {{ formatDaysUntil(goal.target_date) }}
              </span>
            </div>
            <!-- Title -->
            <h4 class="font-bold text-gray-800 text-sm mb-1 line-clamp-2">{{ goal.title }}</h4>
            <!-- Description -->
            <p v-if="goal.description" class="text-xs text-gray-500 line-clamp-2 mb-2">
              {{ goal.description }}
            </p>
            <!-- Target Date -->
            <div class="flex items-center gap-1 text-xs text-gray-400">
              <span>🗓️</span>
              <span>{{ formatDate(goal.target_date) }}</span>
            </div>
            <!-- Actions for own goals -->
            <div v-if="goal.user_id === userStore.currentUserId" class="mt-3 flex gap-2">
              <button 
                @click="completeGoal(goal.id)"
                class="flex-1 text-xs py-1.5 rounded-lg bg-green-100 text-green-600 font-medium hover:bg-green-200 transition-colors"
              >
                ✅ 達成
              </button>
              <button 
                @click="deleteGoal(goal.id)"
                class="flex-1 text-xs py-1.5 rounded-lg bg-red-50 text-red-500 font-medium hover:bg-red-100 transition-colors"
              >
                🗑️ 削除
              </button>
            </div>
          </div>
        </div>
      </div>
    </GlassPanel>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useCache, CACHE_KEYS } from '@/composables/useCache'
import GlassPanel from '@/components/common/GlassPanel.vue'
import SubjectChart from './SubjectChart.vue'

const userStore = useUserStore()
const { getCache, setCache } = useCache()
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
const globalActivity = ref([])
const studyRecords = ref([]) // 全勉強ログ（日付・科目付き）
const weeklyRanking = ref([]) // 週間ランキング
const allGoals = ref([]) // みんなの目標
const showAllActivity = ref(false) // 「もっと見る」の展開状態

// Loading states
const loadingStats = ref(true)
const loadingActivity = ref(true)
const loadingRanking = ref(true)
const loadingGoals = ref(true)

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

// Display activity (with show more/less)
const displayedActivity = computed(() => {
  if (showAllActivity.value) {
    return globalActivity.value
  }
  return globalActivity.value.slice(0, 5)
})

// Weekly subject breakdown
const weeklySubjectData = computed(() => {
  const today = new Date()
  const targetMonday = new Date(today)
  const dayOfWeek = today.getDay() || 7
  targetMonday.setDate(today.getDate() - dayOfWeek + 1)
  const mondayStr = targetMonday.toISOString().split('T')[0]
  
  const subjectTotals = {}
  studyRecords.value.forEach(record => {
    if (record.date >= mondayStr) {
      const subj = record.subject || 'その他'
      subjectTotals[subj] = (subjectTotals[subj] || 0) + (record.minutes || 0)
    }
  })
  
  const total = Object.values(subjectTotals).reduce((a, b) => a + b, 0)
  return Object.entries(subjectTotals).map(([subject, minutes]) => ({
    subject,
    minutes,
    color: getSubjectColor(subject),
    percent: total > 0 ? (minutes / total * 100) : 0
  })).sort((a, b) => b.minutes - a.minutes)
})

// Monthly subject breakdown
const monthlySubjectData = computed(() => {
  const today = new Date()
  const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
  const firstStr = firstOfMonth.toISOString().split('T')[0]
  
  const subjectTotals = {}
  studyRecords.value.forEach(record => {
    if (record.date >= firstStr) {
      const subj = record.subject || 'その他'
      subjectTotals[subj] = (subjectTotals[subj] || 0) + (record.minutes || 0)
    }
  })
  
  const total = Object.values(subjectTotals).reduce((a, b) => a + b, 0)
  return Object.entries(subjectTotals).map(([subject, minutes]) => ({
    subject,
    minutes,
    color: getSubjectColor(subject),
    percent: total > 0 ? (minutes / total * 100) : 0
  })).sort((a, b) => b.minutes - a.minutes)
})

// Format timestamp for display
const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  try {
    const parts = timestamp.split(' ')
    const datePart = parts[0] || ''
    const timePart = parts[1] || ''
    
    // Parse date
    if (datePart) {
      const today = new Date()
      const targetDate = new Date(datePart)
      const diffDays = Math.floor((today - targetDate) / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return timePart ? `今日 ${timePart.substring(0, 5)}` : '今日'
      } else if (diffDays === 1) {
        return timePart ? `昨日 ${timePart.substring(0, 5)}` : '昨日'
      } else if (diffDays < 7) {
        return `${diffDays}日前`
      } else {
        return datePart.substring(5) // MM-DD
      }
    }
    return timestamp
  } catch {
    return timestamp
  }
}

// Week calculations
const weekLabel = computed(() => {
  const today = new Date()
  const startOfWeek = new Date(today)
  const dayOfWeek = today.getDay() || 7
  startOfWeek.setDate(today.getDate() - dayOfWeek + 1 - (weekOffset.value * 7))
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)
  
  const formatDate = (d) => `${d.getMonth() + 1}/${d.getDate()}`
  const dateRange = `${formatDate(startOfWeek)} - ${formatDate(endOfWeek)}`
  
  if (weekOffset.value === 0) return `今週 (${dateRange})`
  if (weekOffset.value === 1) return `先週 (${dateRange})`
  return dateRange
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
    
    // Group by subject for this day
    const subjectTotals = {}
    allData.value
      .filter(d => d.date === dateStr)
      .forEach(d => {
        const subj = d.subject || 'その他'
        subjectTotals[subj] = (subjectTotals[subj] || 0) + (d.minutes || 0)
      })
    
    const segments = Object.entries(subjectTotals).map(([subject, minutes]) => ({
      subject,
      minutes,
      color: getSubjectColor(subject)
    }))
    
    const total = segments.reduce((sum, s) => sum + s.minutes, 0)
    const isToday = date.toDateString() === today.toDateString()
    
    result.push({
      day: days[i],
      date: dateStr,
      segments: segments.length > 0 ? segments : [{ subject: 'なし', minutes: 0, color: '#E5E7EB' }],
      total,
      isToday
    })
  }
  
  return result
})

const weeklyTotal = computed(() => {
  return currentWeekData.value.reduce((sum, d) => sum + d.total, 0)
})

const weeklyAverage = computed(() => {
  return Math.round(weeklyTotal.value / 7)
})

// Month calculations
const monthLabel = computed(() => {
  const today = new Date()
  const targetDate = new Date(today.getFullYear(), today.getMonth() - monthOffset.value, 1)
  const lastDay = new Date(targetDate.getFullYear(), targetDate.getMonth() + 1, 0)
  
  const monthName = `${targetDate.getFullYear()}年${targetDate.getMonth() + 1}月`
  const dateRange = `${targetDate.getMonth() + 1}/1 - ${targetDate.getMonth() + 1}/${lastDay.getDate()}`
  
  if (monthOffset.value === 0) return `今月 (${dateRange})`
  if (monthOffset.value === 1) return `先月 (${dateRange})`
  return `${monthName} (${dateRange})`
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
  return Math.max(...currentWeekData.value.map(d => d.total), 60)
})

const getWeeklyStackedHeight = (minutes, total) => {
  const maxHeight = 120
  if (total === 0) return 4
  const totalHeight = (total / maxWeeklyMinutes.value) * maxHeight
  return Math.max(0, (minutes / total) * totalHeight)
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
    
    // Use all_records for weekly/monthly charts (has subject info)
    if (data.all_records && data.all_records.length > 0) {
      allData.value = data.all_records.map(r => ({
        date: r.date,
        minutes: r.minutes,
        subject: r.subject || 'その他'
      }))
      studyRecords.value = data.all_records.map(r => ({
        date: r.date,
        subject: r.subject,
        minutes: r.minutes
      }))
    } else if (data.weekly) {
      // Fallback to weekly data if all_records not available
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
  } finally {
    loadingStats.value = false
  }
}

// Fetch global activity
const fetchGlobalActivity = async () => {
  // Check cache first (3 minute TTL)
  const cached = getCache(CACHE_KEYS.ACTIVITY)
  if (cached) {
    globalActivity.value = cached
    loadingActivity.value = false
    return
  }

  loadingActivity.value = true
  try {
    const res = await fetch('/api/activity/recent')
    const data = await res.json()
    if (data.status === 'ok') {
      globalActivity.value = data.data || []
      // Cache for 3 minutes
      setCache(CACHE_KEYS.ACTIVITY, globalActivity.value, 3 * 60 * 1000)
    }
  } catch (e) {
    console.error('Failed to fetch global activity:', e)
  } finally {
    loadingActivity.value = false
  }
}

// Fetch weekly ranking
const fetchWeeklyRanking = async () => {
  // Check cache first (5 minute TTL)
  const cached = getCache(CACHE_KEYS.RANKINGS)
  if (cached) {
    weeklyRanking.value = cached
    loadingRanking.value = false
    return
  }

  loadingRanking.value = true
  try {
    const res = await fetch('/api/ranking/weekly')
    const data = await res.json()
    if (data.status === 'ok') {
      weeklyRanking.value = data.data || []
      // Cache for 5 minutes
      setCache(CACHE_KEYS.RANKINGS, weeklyRanking.value, 5 * 60 * 1000)
    }
  } catch (e) {
    console.error('Failed to fetch weekly ranking:', e)
  } finally {
    loadingRanking.value = false
  }
}

// Fetch all goals
const fetchAllGoals = async () => {
  loadingGoals.value = true
  try {
    const res = await fetch('/api/goals')
    const data = await res.json()
    if (data.status === 'ok') {
      allGoals.value = data.goals || []
    }
  } catch (e) {
    console.error('Failed to fetch goals:', e)
  } finally {
    loadingGoals.value = false
  }
}

// Goal helper functions
const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const getDaysUntil = (targetDate) => {
  if (!targetDate) return -999
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return Math.ceil((target - today) / (1000 * 60 * 60 * 24))
}

const formatDaysUntil = (targetDate) => {
  const days = getDaysUntil(targetDate)
  if (days < 0) return '期限切れ'
  if (days === 0) return '今日!'
  if (days === 1) return '明日'
  return `あと${days}日`
}

const getDaysUntilClass = (targetDate) => {
  const days = getDaysUntil(targetDate)
  if (days < 0) return 'bg-red-100 text-red-600'
  if (days <= 3) return 'bg-orange-100 text-orange-600'
  if (days <= 7) return 'bg-yellow-100 text-yellow-600'
  return 'bg-green-100 text-green-600'
}

const completeGoal = async (goalId) => {
  if (!confirm('この目標を達成済みにしますか？')) return
  
  try {
    const res = await fetch(`/api/goals/${goalId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userStore.currentUserId })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      await fetchAllGoals()
    } else {
      alert('完了処理に失敗しました')
    }
  } catch (e) {
    console.error('Complete goal error:', e)
    alert('完了処理に失敗しました')
  }
}

const deleteGoal = async (goalId) => {
  if (!confirm('この目標を削除しますか？')) return
  
  try {
    const res = await fetch(`/api/goals/${goalId}?user_id=${userStore.currentUserId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    if (data.status === 'ok') {
      await fetchAllGoals()
    } else {
      alert('削除に失敗しました')
    }
  } catch (e) {
    console.error('Delete goal error:', e)
    alert('削除に失敗しました')
  }
}

onMounted(() => {
  fetchData()
  fetchGlobalActivity()
  fetchWeeklyRanking()
  fetchAllGoals()
})
</script>
