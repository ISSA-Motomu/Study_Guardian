<template>
  <div class="facility-list-view min-h-screen pb-32">
    <!-- Space Background (Subtle) -->
    <div class="fixed inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900" />
      <div class="star-layer-subtle" />
    </div>

    <!-- Header - iOS Safe Area -->
    <div class="sticky top-0 z-30 bg-slate-900/95 backdrop-blur-lg border-b border-white/10 ios-safe-top">
      <div class="p-4 flex items-center gap-3">
        <button 
          @click="navigate('main')"
          class="w-12 h-12 rounded-2xl bg-white/15 flex items-center justify-center text-white active:bg-white/30 active:scale-95 transition-all text-lg"
        >
          ←
        </button>
        <div class="flex-1">
          <h1 class="text-xl font-bold text-white">研究施設</h1>
          <p class="text-xs text-white/60 mt-0.5">{{ stats.unlockedCount }}/{{ stats.totalFacilities }} 解放済み</p>
        </div>
        <!-- Current KP -->
        <div class="bg-white/15 rounded-2xl px-4 py-2.5 flex items-center gap-2 border border-white/10">
          <span class="text-xl">💡</span>
          <AnimatedCounter 
            :value="evolutionStore.knowledgePoints"
            class="text-xl font-bold text-yellow-300 tabular-nums"
          />
        </div>
      </div>

      <!-- Production Stats Bar -->
      <div class="px-4 pb-3 flex items-center gap-2">
        <div class="flex-1 bg-gradient-to-r from-green-900/50 to-emerald-900/50 rounded-xl p-3 border border-green-400/20">
          <div class="flex items-center justify-between">
            <span class="text-xs text-green-300/80">⚡ 総生産</span>
            <span class="text-lg font-bold text-green-400 tabular-nums">+{{ evolutionStore.formatNumber(evolutionStore.currentProduction) }}/分</span>
          </div>
        </div>
        <div class="bg-white/10 rounded-xl p-3">
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs text-white/60">×</span>
            <span class="text-lg font-bold text-cyan-300 tabular-nums">{{ evolutionStore.totalMultiplier.toFixed(1) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Facility List by Tier - Horizontal Scroll -->
    <div class="py-4 space-y-6">
      <div
        v-for="tierGroup in evolutionStore.facilitiesByTier"
        :key="tierGroup.tier"
        class="tier-section"
      >
        <!-- Tier Header -->
        <div class="px-4 mb-3">
          <div class="flex items-center gap-3">
            <!-- Tier Badge -->
            <div 
              class="w-10 h-10 rounded-xl bg-gradient-to-br flex items-center justify-center text-white font-bold shadow-lg"
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
            <!-- Tier Production -->
            <div class="text-right">
              <p class="text-xs text-white/50">Tier生産</p>
              <p class="text-sm font-bold text-green-400">+{{ getTierProduction(tierGroup) }}/分</p>
            </div>
          </div>
        </div>

        <!-- Horizontal Scroll Facility Cards -->
        <div class="overflow-x-auto scrollbar-hide">
          <div class="flex gap-3 px-4 pb-2" style="min-width: min-content;">
            <FacilityCardHorizontal
              v-for="facility in tierGroup.facilities"
              :key="facility.id"
              :facility="facility"
              @buy="handleBuy"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation - iOS Safe Area -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-slate-900 via-slate-900/95 to-transparent ios-safe-bottom">
      <div class="flex gap-3 max-w-md mx-auto">
        <button 
          @click="navigate('main')"
          class="flex-1 py-4 bg-white/15 backdrop-blur-xl rounded-2xl text-white font-bold flex items-center justify-center gap-2 border border-white/20 active:bg-white/30 active:scale-95 transition-all text-base"
        >
          <span class="text-xl">🌍</span>
          <span>メイン</span>
        </button>
        <button 
          @click="navigate('tree')"
          class="flex-1 py-4 bg-white/15 backdrop-blur-xl rounded-2xl text-white font-bold flex items-center justify-center gap-2 border border-white/20 active:bg-white/30 active:scale-95 transition-all text-base"
        >
          <span class="text-xl">🌳</span>
          <span>ツリー</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { soundManager } from '@/utils/sound'
import AnimatedCounter from './AnimatedCounter.vue'
import FacilityCardHorizontal from './FacilityCardHorizontal.vue'

const evolutionStore = useEvolutionStore()

const emit = defineEmits(['navigate'])

const navigate = (view) => {
  soundManager.play('click')
  emit('navigate', view)
}

const stats = computed(() => evolutionStore.stats)

const handleBuy = ({ facilityId, amount }) => {
  if (amount === -1) {
    // MAX購入: 買えるだけ買う
    evolutionStore.buyFacility(facilityId, 1000)
  } else {
    evolutionStore.buyFacility(facilityId, amount)
  }
}

// Tier別の総生産量を計算
const getTierProduction = (tierGroup) => {
  const total = tierGroup.facilities
    .filter(f => f.state === 'unlocked' && f.level > 0)
    .reduce((sum, f) => sum + f.production, 0)
  return evolutionStore.formatNumber(total)
}
</script>

<style scoped>
.facility-list-view {
  -webkit-overflow-scrolling: touch;
}

.ios-safe-top {
  padding-top: max(env(safe-area-inset-top, 0px), 8px);
}

.ios-safe-bottom {
  padding-bottom: max(env(safe-area-inset-bottom, 0px), 16px);
}

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

/* Hide scrollbar but keep scroll functionality */
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
