<template>
  <div class="facility-list-view min-h-screen pb-24">
    <!-- Space Background (Subtle) -->
    <div class="fixed inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900" />
      <div class="star-layer-subtle" />
    </div>

    <!-- Header -->
    <div class="sticky top-0 z-30 bg-slate-900/95 backdrop-blur-lg border-b border-white/10">
      <div class="p-4 flex items-center gap-4">
        <button 
          @click="$emit('navigate', 'main')"
          class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition-all"
        >
          ←
        </button>
        <div class="flex-1">
          <h1 class="text-lg font-bold text-white">研究施設</h1>
          <p class="text-xs text-white/60">{{ stats.unlockedCount }}/{{ stats.totalFacilities }} 解放済み</p>
        </div>
        <!-- Current KP -->
        <div class="bg-white/10 rounded-xl px-3 py-2 flex items-center gap-2">
          <span class="text-lg">💡</span>
          <AnimatedCounter 
            :value="evolutionStore.knowledgePoints"
            class="text-lg font-bold text-yellow-300"
          />
        </div>
      </div>

      <!-- Multiplier Bar -->
      <div class="px-4 pb-3 flex items-center gap-3">
        <div class="flex-1 bg-white/10 rounded-lg p-2 flex items-center justify-between">
          <span class="text-xs text-white/60">研究効率</span>
          <span class="text-lg font-bold text-cyan-300">×{{ evolutionStore.totalMultiplier.toFixed(1) }}</span>
        </div>
        <div class="flex-1 bg-white/10 rounded-lg p-2 flex items-center justify-between">
          <span class="text-xs text-white/60">所持レベル</span>
          <span class="text-lg font-bold text-purple-300">{{ stats.totalOwned }}</span>
        </div>
      </div>
    </div>

    <!-- Facility List by Tier -->
    <div class="p-4 space-y-6">
      <div
        v-for="tierGroup in evolutionStore.facilitiesByTier"
        :key="tierGroup.tier"
        class="tier-section"
      >
        <!-- Tier Header -->
        <div 
          class="sticky top-[120px] z-20 -mx-2 px-3 py-2 rounded-lg mb-3 backdrop-blur-md"
          :class="getTierHeaderClass(tierGroup.tier)"
        >
          <div class="flex items-center gap-3">
            <!-- Tier Badge -->
            <div 
              class="w-10 h-10 rounded-full bg-gradient-to-br flex items-center justify-center text-white font-bold shadow-lg"
              :class="tierGroup.color"
            >
              {{ tierGroup.tier }}
            </div>
            <!-- Tier Info -->
            <div class="flex-1">
              <p class="font-bold text-white">{{ tierGroup.name }}</p>
              <p class="text-xs text-white/60">
                {{ tierGroup.facilities.filter(f => f.state === 'unlocked').length }}/{{ tierGroup.facilities.length }} 解放
              </p>
            </div>
            <!-- Tier Progress -->
            <div class="text-right">
              <CircularProgress 
                :progress="getTierProgress(tierGroup)" 
                :size="36"
                :color="getTierColor(tierGroup.tier)"
              />
            </div>
          </div>
        </div>

        <!-- Facility Cards -->
        <div class="space-y-3">
          <FacilityCardAdvanced
            v-for="facility in tierGroup.facilities"
            :key="facility.id"
            :facility="facility"
            @buy="handleBuy"
          />
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-slate-900 to-transparent">
      <div class="flex gap-3 max-w-md mx-auto">
        <button 
          @click="$emit('navigate', 'main')"
          class="flex-1 py-3 bg-white/10 backdrop-blur rounded-xl text-white font-semibold flex items-center justify-center gap-2"
        >
          <span>🌍</span>
          <span>メイン</span>
        </button>
        <button 
          @click="$emit('navigate', 'tree')"
          class="flex-1 py-3 bg-white/10 backdrop-blur rounded-xl text-white font-semibold flex items-center justify-center gap-2"
        >
          <span>🌳</span>
          <span>ツリー</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import AnimatedCounter from './AnimatedCounter.vue'
import FacilityCardAdvanced from './FacilityCardAdvanced.vue'
import CircularProgress from './CircularProgress.vue'

const evolutionStore = useEvolutionStore()

defineEmits(['navigate'])

const stats = computed(() => evolutionStore.stats)

const handleBuy = (facilityId) => {
  evolutionStore.buyFacility(facilityId)
}

const getTierHeaderClass = (tier) => {
  const classes = {
    1: 'bg-slate-700/80',
    2: 'bg-blue-900/80',
    3: 'bg-purple-900/80',
    4: 'bg-orange-900/80',
    5: 'bg-pink-900/80',
    6: 'bg-amber-900/80'
  }
  return classes[tier] || 'bg-slate-700/80'
}

const getTierColor = (tier) => {
  const colors = {
    1: '#64748b',
    2: '#3b82f6',
    3: '#8b5cf6',
    4: '#f97316',
    5: '#ec4899',
    6: '#f59e0b'
  }
  return colors[tier] || '#64748b'
}

const getTierProgress = (tierGroup) => {
  const unlocked = tierGroup.facilities.filter(f => f.state === 'unlocked').length
  return (unlocked / tierGroup.facilities.length) * 100
}
</script>

<style scoped>
.star-layer-subtle {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.3) 100%, transparent),
    radial-gradient(1px 1px at 60% 70%, rgba(255,255,255,0.2) 100%, transparent),
    radial-gradient(1px 1px at 80% 20%, rgba(255,255,255,0.3) 100%, transparent);
  background-size: 200px 200px;
  opacity: 0.5;
}
</style>
