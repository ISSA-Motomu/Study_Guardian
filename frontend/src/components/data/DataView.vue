<template>
  <div class="space-y-4 mt-8">
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

    <!-- Weekly Chart -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📈 週間推移</h3>
      <WeeklyChart :data="weeklyData" />
    </GlassPanel>

    <!-- Subject Breakdown -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📚 科目別時間</h3>
      <SubjectChart :data="subjectData" />
    </GlassPanel>

    <!-- Recent Activity -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">🕐 最近の記録</h3>
      <div class="space-y-2">
        <div 
          v-for="(item, idx) in recentActivity" 
          :key="idx"
          class="flex justify-between items-center py-2 border-b last:border-0"
        >
          <div>
            <p class="font-medium text-gray-800">{{ item.subject }}</p>
            <p class="text-xs text-gray-500">{{ item.date }}</p>
          </div>
          <span class="font-bold text-indigo-600">{{ item.minutes }}分</span>
        </div>
      </div>
    </GlassPanel>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import GlassPanel from '@/components/common/GlassPanel.vue'
import WeeklyChart from './WeeklyChart.vue'
import SubjectChart from './SubjectChart.vue'

const userStore = useUserStore()
const emit = defineEmits(['admin'])

// Mock data - replace with API calls
const weeklyData = ref([
  { day: '月', minutes: 45 },
  { day: '火', minutes: 30 },
  { day: '水', minutes: 60 },
  { day: '木', minutes: 25 },
  { day: '金', minutes: 50 },
  { day: '土', minutes: 90 },
  { day: '日', minutes: 40 }
])

const subjectData = ref([
  { subject: '数学', minutes: 120, color: '#6366f1' },
  { subject: '英語', minutes: 90, color: '#f59e0b' },
  { subject: '国語', minutes: 60, color: '#10b981' },
  { subject: '理科', minutes: 45, color: '#ef4444' }
])

const recentActivity = ref([
  { subject: '数学', date: '今日 15:30', minutes: 45 },
  { subject: '英語', date: '昨日 20:00', minutes: 30 },
  { subject: '国語', date: '3日前', minutes: 25 }
])
</script>
