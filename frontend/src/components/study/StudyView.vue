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
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'
import { useShopStore } from '@/stores/shop'
import { useSound } from '@/composables/useSound'
import GlassPanel from '@/components/common/GlassPanel.vue'

const userStore = useUserStore()
const studyStore = useStudyStore()
const shopStore = useShopStore()
const { playSound } = useSound()

const emit = defineEmits(['timer'])

const defaultAvatar = 'https://cdn-icons-png.flaticon.com/512/4333/4333609.png'

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
</script>
