<template>
  <div class="space-y-6 mt-8 pb-8">
    <!-- Currency Display Header -->
    <div class="sticky top-0 z-20 -mx-6 px-6 py-3 bg-gradient-to-r from-indigo-600/90 to-purple-600/90 backdrop-blur-lg rounded-b-2xl shadow-lg">
      <!-- Dual Currency Display -->
      <div class="grid grid-cols-2 gap-3 mb-3">
        <!-- KP (Game Currency) -->
        <div class="bg-white/20 rounded-xl p-2 text-center">
          <div class="flex items-center justify-center gap-1">
            <span class="text-lg">💡</span>
            <span class="text-xs text-white/80">KP</span>
          </div>
          <p class="text-xl font-bold text-white">{{ formatNumber(evolutionStore.knowledgePoints) }}</p>
          <p class="text-[10px] text-white/60">ゲーム内専用</p>
        </div>
        <!-- XP (Shop Currency) - Read Only Display -->
        <div class="bg-black/20 rounded-xl p-2 text-center">
          <div class="flex items-center justify-center gap-1">
            <span class="text-lg">⭐</span>
            <span class="text-xs text-white/80">XP</span>
          </div>
          <p class="text-xl font-bold text-amber-300">{{ formatNumber(userStore.user.xp || 0) }}</p>
          <p class="text-[10px] text-white/60">ショップ用</p>
        </div>
      </div>

      <!-- Multiplier & Stats -->
      <div class="flex items-center justify-between text-white">
        <div class="flex items-center gap-2">
          <span class="text-lg">🔬</span>
          <div>
            <p class="text-xs opacity-80">研究効率</p>
            <p class="text-lg font-semibold">×{{ evolutionStore.totalMultiplier.toFixed(1) }}</p>
          </div>
        </div>
        <div class="text-right">
          <p class="text-xs opacity-80">累計KP</p>
          <p class="text-lg font-semibold">{{ formatNumber(evolutionStore.totalEarnedPoints) }}</p>
        </div>
      </div>
      
      <!-- Progress to next unlock -->
      <div v-if="evolutionStore.nextUnlock" class="mt-3">
        <div class="flex justify-between text-xs text-white/70 mb-1">
          <span>次の解放: {{ evolutionStore.nextUnlock.state === 'revealed' ? evolutionStore.nextUnlock.name : '???' }}</span>
          <span>{{ Math.floor(evolutionStore.nextUnlock.progressToUnlock) }}%</span>
        </div>
        <div class="h-2 bg-white/20 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-amber-400 to-yellow-300 transition-all duration-500"
            :style="{ width: evolutionStore.nextUnlock.progressToUnlock + '%' }"
          />
        </div>
      </div>
    </div>

    <!-- Currency Info Card -->
    <GlassPanel class="!p-3">
      <div class="flex items-start gap-3">
        <span class="text-2xl">💡</span>
        <div class="flex-1">
          <p class="text-sm font-bold text-gray-800">KP（Knowledge Points）とは？</p>
          <p class="text-xs text-gray-500 mt-1">
            勉強時間で獲得できるゲーム内専用通貨。施設のアップグレードにのみ使用可能。
            <span class="text-amber-600 font-medium">ショップのXPとは別物です。</span>
          </p>
        </div>
      </div>
    </GlassPanel>

    <!-- Summary Card -->
    <GlassPanel class="text-center">
      <div class="grid grid-cols-3 gap-4">
        <div>
          <p class="text-3xl font-bold text-indigo-600">{{ evolutionStore.stats.unlockedCount }}</p>
          <p class="text-xs text-gray-500">解放済み</p>
        </div>
        <div>
          <p class="text-3xl font-bold text-purple-600">{{ evolutionStore.stats.totalOwned }}</p>
          <p class="text-xs text-gray-500">所持レベル</p>
        </div>
        <div>
          <p class="text-3xl font-bold text-amber-500">{{ evolutionStore.stats.totalFacilities }}</p>
          <p class="text-xs text-gray-500">全施設</p>
        </div>
      </div>
    </GlassPanel>

    <!-- Facility List by Tier (Scrollable) -->
    <div class="space-y-6">
      <div
        v-for="tierGroup in evolutionStore.facilitiesByTier"
        :key="tierGroup.tier"
        class="relative"
      >
        <!-- Tier Header -->
        <div 
          class="sticky top-[100px] z-10 -mx-2 px-3 py-2 rounded-lg mb-3"
          :class="tierGroup.bgColor"
        >
          <div class="flex items-center gap-2">
            <div 
              class="w-8 h-8 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold text-sm"
              :class="tierGroup.color"
            >
              {{ tierGroup.tier }}
            </div>
            <div>
              <p class="font-bold text-gray-800">{{ tierGroup.name }}</p>
              <p class="text-xs text-gray-500">
                {{ tierGroup.facilities.filter(f => f.state === 'unlocked').length }}/{{ tierGroup.facilities.length }} 解放
              </p>
            </div>
          </div>
        </div>

        <!-- Facilities -->
        <div class="space-y-3">
          <FacilityCard
            v-for="facility in tierGroup.facilities"
            :key="facility.id"
            :facility="facility"
            @buy="handleBuy"
          />
        </div>
      </div>
    </div>

    <!-- Debug Button (Dev only) -->
    <div v-if="isDev" class="fixed bottom-24 right-4">
      <button
        @click="evolutionStore.debugAddPoints(1000)"
        class="p-3 bg-red-500 text-white rounded-full shadow-lg"
      >
        +1000
      </button>
    </div>

    <!-- Unsaved indicator -->
    <transition name="fade">
      <div
        v-if="evolutionStore.isDirty"
        class="fixed bottom-24 left-1/2 -translate-x-1/2 px-4 py-2 bg-amber-500 text-white text-sm rounded-full shadow-lg"
      >
        ⚠️ 未保存の変更あり
      </div>
    </transition>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { useUserStore } from '@/stores/user'
import GlassPanel from '@/components/common/GlassPanel.vue'
import FacilityCard from './FacilityCard.vue'

const evolutionStore = useEvolutionStore()
const userStore = useUserStore()
const isDev = ref(import.meta.env.DEV)

onMounted(async () => {
  await evolutionStore.initialize()
})

const formatNumber = (num) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return Math.floor(num).toLocaleString()
}

const handleBuy = (facilityId) => {
  const success = evolutionStore.buyFacility(facilityId)
  if (success) {
    // 購入成功時のフィードバック（将来的にサウンド等）
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
