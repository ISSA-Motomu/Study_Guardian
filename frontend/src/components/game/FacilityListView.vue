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

      <!-- Multiplier Bar -->
      <div class="px-4 pb-3 flex items-center gap-3">
        <div class="flex-1 bg-white/10 rounded-xl p-3 flex items-center justify-between">
          <span class="text-xs text-white/60">研究効率</span>
          <span class="text-xl font-bold text-cyan-300 tabular-nums">×{{ evolutionStore.totalMultiplier.toFixed(1) }}</span>
        </div>
        <div class="flex-1 bg-white/10 rounded-xl p-3 flex items-center justify-between">
          <span class="text-xs text-white/60">所持レベル</span>
          <span class="text-xl font-bold text-purple-300 tabular-nums">{{ stats.totalOwned }}</span>
        </div>
      </div>
      
      <!-- Buy Amount Selector -->
      <div class="px-4 pb-4">
        <div class="flex items-center gap-2 bg-black/30 rounded-xl p-2">
          <span class="text-xs text-white/60 px-2">購入数:</span>
          <button
            v-for="opt in buyOptions"
            :key="opt.value"
            @click="selectedBuyAmount = opt.value"
            :class="[
              'flex-1 py-2 px-3 rounded-lg text-sm font-bold transition-all',
              selectedBuyAmount === opt.value 
                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg' 
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            ]"
          >
            {{ opt.label }}
          </button>
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
          class="sticky top-[140px] z-20 -mx-2 px-4 py-3 rounded-2xl mb-4 backdrop-blur-md"
          :class="getTierHeaderClass(tierGroup.tier)"
        >
          <div class="flex items-center gap-3">
            <!-- Tier Badge -->
            <div 
              class="w-12 h-12 rounded-2xl bg-gradient-to-br flex items-center justify-center text-white font-bold shadow-lg text-lg"
              :class="tierGroup.color"
            >
              {{ tierGroup.tier }}
            </div>
            <!-- Tier Info -->
            <div class="flex-1">
              <p class="font-bold text-white text-lg">{{ tierGroup.name }}</p>
              <p class="text-xs text-white/60">
                {{ tierGroup.facilities.filter(f => f.state === 'unlocked').length }}/{{ tierGroup.facilities.length }} 解放
              </p>
            </div>
            <!-- Tier Progress -->
            <div class="text-right">
              <CircularProgress 
                :progress="getTierProgress(tierGroup)" 
                :size="44"
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
            :buyAmount="selectedBuyAmount"
            @buy="handleBuy"
          />
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
import { ref, computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { soundManager } from '@/utils/sound'
import AnimatedCounter from './AnimatedCounter.vue'
import FacilityCardAdvanced from './FacilityCardAdvanced.vue'
import CircularProgress from './CircularProgress.vue'

const evolutionStore = useEvolutionStore()

const emit = defineEmits(['navigate'])

const navigate = (view) => {
  soundManager.play('click')
  emit('navigate', view)
}

const stats = computed(() => evolutionStore.stats)

// 購入数選択
const selectedBuyAmount = ref(1)
const buyOptions = [
  { label: '×1', value: 1 },
  { label: '×10', value: 10 },
  { label: '×100', value: 100 },
  { label: 'MAX', value: -1 }  // -1 = MAX
]

const handleBuy = ({ facilityId, amount }) => {
  if (amount === -1) {
    // MAX購入: 買えるだけ買う
    evolutionStore.buyFacility(facilityId, 1000)
  } else {
    evolutionStore.buyFacility(facilityId, amount)
  }
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
</style>
