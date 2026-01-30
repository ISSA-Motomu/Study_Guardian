<template>
  <div class="space-y-6">
    <!-- User Profile Card -->
    <GlassPanel class="text-center">
      <div class="flex items-center gap-4">
        <img 
          :src="userStore.user.avatar_url || defaultAvatar"
          class="w-16 h-16 rounded-full border-2 border-indigo-300"
          alt="avatar"
        >
        <div class="text-left flex-1">
          <h2 class="font-bold text-lg text-gray-800">{{ userStore.user.name }}</h2>
          <p class="text-sm text-gray-500">{{ userStore.user.rank_name }}</p>
          
          <!-- EXP Bar -->
          <div class="mt-2">
            <div class="flex justify-between text-xs text-gray-600 mb-1">
              <span>Lv.{{ userStore.user.level }}</span>
              <span>{{ userStore.user.exp }} / {{ userStore.user.next_exp }} XP</span>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                :style="{ width: userStore.expPercentage + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </GlassPanel>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 gap-4">
      <GlassPanel class="text-center">
        <p class="text-3xl font-bold text-indigo-600">
          {{ userStore.user.total_hours?.toFixed(1) || '0' }}
        </p>
        <p class="text-sm text-gray-500">累計時間</p>
      </GlassPanel>
      
      <GlassPanel class="text-center">
        <p class="text-3xl font-bold text-amber-500">
          {{ userStore.user.xp || 0 }}
        </p>
        <p class="text-sm text-gray-500">所持 XP</p>
      </GlassPanel>
    </div>

    <!-- Session Resume Card -->
    <GlassPanel v-if="studyStore.inSession" class="border-2 border-amber-300 animate-pulse">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-amber-600 font-bold">⏸️ 勉強中断中</p>
          <p class="text-sm text-gray-600">
            {{ studyStore.currentSubject }} - {{ studyStore.lastSessionTime }}
          </p>
        </div>
        <button 
          @click="emit('timer')"
          class="bg-amber-500 text-white px-4 py-2 rounded-lg font-bold"
        >
          再開
        </button>
      </div>
    </GlassPanel>

    <!-- Today's Goal -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-2">📌 今日の目標</h3>
      <div class="flex items-center gap-3">
        <div class="flex-1 h-3 bg-gray-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-green-400 to-emerald-500"
            :style="{ width: dailyProgress + '%' }"
          />
        </div>
        <span class="text-sm font-medium text-gray-600">{{ todayMinutes }}/60分</span>
      </div>
    </GlassPanel>

    <!-- My Goals Section -->
    <GlassPanel>
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-bold text-gray-700">🎯 マイ目標</h3>
        <button 
          @click="emit('openGoalModal')"
          class="text-xs px-3 py-1.5 rounded-lg bg-indigo-100 text-indigo-600 font-medium hover:bg-indigo-200 transition-colors"
        >
          + 追加
        </button>
      </div>
      
      <div v-if="myGoals.length === 0" class="text-center text-gray-400 py-4 text-sm">
        目標を設定してモチベーションアップ！
      </div>
      
      <div v-else class="space-y-2">
        <div 
          v-for="goal in myGoals" 
          :key="goal.id"
          class="p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <h4 class="font-bold text-gray-800 text-sm truncate">{{ goal.title }}</h4>
              <p v-if="goal.description" class="text-xs text-gray-500 truncate">{{ goal.description }}</p>
            </div>
            <span 
              class="text-xs px-2 py-0.5 rounded-full ml-2 flex-shrink-0"
              :class="getGoalUrgencyClass(goal.target_date)"
            >
              {{ formatGoalDays(goal.target_date) }}
            </span>
          </div>
          <div class="flex justify-between items-center mt-2">
            <span class="text-xs text-gray-400">🗓️ {{ formatGoalDate(goal.target_date) }}</span>
            <button 
              @click="completeGoal(goal.id)"
              class="text-xs px-2 py-1 rounded bg-green-100 text-green-600 font-medium hover:bg-green-200"
            >
              ✅ 達成
            </button>
          </div>
        </div>
      </div>
    </GlassPanel>

    <!-- Menu Grid -->
    <div class="grid grid-cols-2 gap-4">
      <button 
        @click="openShop"
        class="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg flex flex-col items-center justify-center gap-2 transition-transform active:scale-95 border-b-4 border-amber-200"
      >
        <span class="text-4xl">🏪</span>
        <span class="font-bold text-gray-700">ショップ</span>
      </button>

      <button 
        @click="openGacha"
        class="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg flex flex-col items-center justify-center gap-2 transition-transform active:scale-95 border-b-4 border-purple-200"
      >
        <span class="text-4xl">🔮</span>
        <span class="font-bold text-gray-700">ガチャ</span>
        <span class="text-xs text-red-500 font-bold bg-red-100 px-2 py-0.5 rounded-full">準備中</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'
import { useShopStore } from '@/stores/shop'
import { useSound } from '@/composables/useSound'
import GlassPanel from '@/components/common/GlassPanel.vue'

const userStore = useUserStore()
const studyStore = useStudyStore()
const shopStore = useShopStore()
const { playSound } = useSound()

const emit = defineEmits(['timer', 'openGoalModal'])

const defaultAvatar = 'https://cdn-icons-png.flaticon.com/512/4333/4333609.png'

// Goal data
const myGoals = ref([])

// TODO: Fetch from API
const todayMinutes = computed(() => Math.min(60, Math.floor(Math.random() * 60)))
const dailyProgress = computed(() => (todayMinutes.value / 60) * 100)

const openShop = () => {
  playSound('select1')
  shopStore.openShopList()
}

const openGacha = () => {
  playSound('select2') // Using a different sound just to acknowledge tap
  alert('ガチャは現在準備中です！\nアップデートをお楽しみに！')
}

// Goal functions
const fetchMyGoals = async () => {
  if (!userStore.currentUserId) return
  try {
    const res = await fetch(`/api/goals/user/${userStore.currentUserId}`)
    const data = await res.json()
    if (data.status === 'ok') {
      myGoals.value = data.goals || []
    }
  } catch (e) {
    console.error('Failed to fetch goals:', e)
  }
}

const formatGoalDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const formatGoalDays = (targetDate) => {
  if (!targetDate) return ''
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  const days = Math.ceil((target - today) / (1000 * 60 * 60 * 24))
  if (days < 0) return '期限切れ'
  if (days === 0) return '今日!'
  if (days === 1) return '明日'
  return `あと${days}日`
}

const getGoalUrgencyClass = (targetDate) => {
  if (!targetDate) return 'bg-gray-100 text-gray-600'
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  const days = Math.ceil((target - today) / (1000 * 60 * 60 * 24))
  if (days < 0) return 'bg-red-100 text-red-600'
  if (days <= 3) return 'bg-orange-100 text-orange-600'
  if (days <= 7) return 'bg-yellow-100 text-yellow-600'
  return 'bg-green-100 text-green-600'
}

const completeGoal = async (goalId) => {
  if (!confirm('この目標を達成済みにしますか？🎉')) return
  
  try {
    const res = await fetch(`/api/goals/${goalId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userStore.currentUserId })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      playSound('success')
      await fetchMyGoals()
    } else {
      alert('完了処理に失敗しました')
    }
  } catch (e) {
    console.error('Complete goal error:', e)
    alert('完了処理に失敗しました')
  }
}

const onGoalCreated = () => {
  fetchMyGoals()
}

onMounted(() => {
  fetchMyGoals()
})

// Expose for parent component
defineExpose({ fetchMyGoals })
</script>
