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
      <h3 class="font-bold text-gray-700 mb-4">📚 科目別時間 (割合)</h3>
      <SubjectChart :data="subjectData" />
    </GlassPanel>

    <!-- Recent Activity -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">🕐 最近の記録</h3>
      <div v-if="recentActivity.length === 0" class="text-center text-gray-500 py-4">
        記録がありません
      </div>
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
import { useApi } from '@/composables/useApi'
import GlassPanel from '@/components/common/GlassPanel.vue'
import WeeklyChart from './WeeklyChart.vue'
import SubjectChart from './SubjectChart.vue'

const userStore = useUserStore()
const { get } = useApi()
const emit = defineEmits(['admin'])

const weeklyData = ref([])
const subjectData = ref([])
const recentActivity = ref([])

onMounted(async () => {
  if (userStore.currentUserId) {
    try {
      const data = await get(`/api/user/${userStore.currentUserId}/stats`)
      weeklyData.value = data.weekly
      subjectData.value = data.subject
      recentActivity.value = data.recent
    } catch (e) {
      console.error('Failed to fetch stats:', e)
    }
  }
})
</script>
