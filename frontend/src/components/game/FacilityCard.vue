<template>
  <div 
    class="relative rounded-xl overflow-hidden transition-all duration-300"
    :class="cardClass"
  >
    <!-- Locked Overlay (Heavy blur) -->
    <div 
      v-if="facility.state === 'locked'"
      class="absolute inset-0 bg-gray-900/60 backdrop-blur-lg z-10 flex items-center justify-center"
    >
      <div class="text-center text-white/50">
        <span class="text-4xl">🔒</span>
        <p class="text-xs mt-1">未発見</p>
      </div>
    </div>

    <!-- Hint Overlay (Medium blur) -->
    <div 
      v-if="facility.state === 'hint'"
      class="absolute inset-0 bg-gray-800/40 backdrop-blur-md z-10 flex items-center justify-center"
    >
      <div class="text-center text-white/70">
        <span class="text-4xl filter blur-sm">{{ facility.icon }}</span>
        <p class="text-sm mt-2 font-medium">???</p>
        <p class="text-xs text-white/50">{{ formatNumber(facility.unlockCondition) }}pt で解放</p>
        <div class="mt-2 w-24 h-1.5 bg-white/20 rounded-full overflow-hidden mx-auto">
          <div 
            class="h-full bg-white/50 transition-all"
            :style="{ width: facility.progressToUnlock + '%' }"
          />
        </div>
      </div>
    </div>

    <!-- Revealed Overlay (Light effect) -->
    <div 
      v-if="facility.state === 'revealed'"
      class="absolute inset-0 bg-gradient-to-r from-amber-500/20 to-yellow-500/20 z-10 flex items-center justify-center backdrop-blur-[2px]"
    >
      <div class="text-center">
        <span class="text-5xl animate-pulse">{{ facility.icon }}</span>
        <p class="text-lg font-bold text-amber-700 mt-2">{{ facility.name }}</p>
        <p class="text-xs text-amber-600">あと {{ formatNumber(facility.unlockCondition - currentTotalPoints) }}pt</p>
        <div class="mt-2 w-32 h-2 bg-amber-200 rounded-full overflow-hidden mx-auto">
          <div 
            class="h-full bg-gradient-to-r from-amber-400 to-yellow-400 transition-all"
            :style="{ width: facility.progressToUnlock + '%' }"
          />
        </div>
      </div>
    </div>

    <!-- Main Card Content -->
    <div class="p-4" :class="{ 'opacity-30': facility.state !== 'unlocked' }">
      <div class="flex items-start gap-3">
        <!-- Icon -->
        <div 
          class="w-14 h-14 rounded-xl flex items-center justify-center text-3xl shrink-0"
          :class="iconBgClass"
        >
          {{ facility.icon }}
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="font-bold text-gray-800 truncate">{{ facility.name }}</h3>
            <span 
              v-if="facility.level > 0"
              class="px-2 py-0.5 text-xs font-bold rounded-full bg-indigo-100 text-indigo-600"
            >
              Lv.{{ facility.level }}
            </span>
          </div>
          <p class="text-xs text-gray-500 mt-0.5 line-clamp-2">{{ facility.description }}</p>
          
          <!-- Stats -->
          <div class="flex items-center gap-4 mt-2 text-xs">
            <div class="flex items-center gap-1">
              <span class="text-green-500">↑</span>
              <span class="text-gray-600">+{{ facility.production.toFixed(1) }}/分</span>
            </div>
            <div class="flex items-center gap-1">
              <span class="text-indigo-500">💡</span>
              <span class="text-gray-600">{{ formatNumber(facility.currentCost) }} KP</span>
            </div>
          </div>
        </div>

        <!-- Buy Button -->
        <button
          v-if="facility.state === 'unlocked'"
          @click="$emit('buy', facility.id)"
          :disabled="!facility.canAfford"
          class="px-4 py-2 rounded-xl font-bold text-sm transition-all shrink-0"
          :class="facility.canAfford 
            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg hover:shadow-xl active:scale-95' 
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'"
        >
          {{ facility.level === 0 ? '解放' : 'UP' }}
        </button>
      </div>

      <!-- Level Progress (if owned) -->
      <div v-if="facility.level > 0" class="mt-3">
        <div class="flex justify-between text-xs text-gray-500 mb-1">
          <span>次のレベル効果</span>
          <span>+{{ (facility.baseMultiplier).toFixed(1) }} KP/分</span>
        </div>
        <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-indigo-400 to-purple-400"
            :style="{ width: Math.min(100, (facility.level % 10) * 10) + '%' }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'

const props = defineProps({
  facility: {
    type: Object,
    required: true
  }
})

defineEmits(['buy'])

const evolutionStore = useEvolutionStore()
const currentTotalPoints = computed(() => evolutionStore.totalEarnedPoints)

const cardClass = computed(() => {
  const base = 'bg-white shadow-md'
  switch (props.facility.state) {
    case 'unlocked':
      return props.facility.level > 0 
        ? `${base} ring-2 ring-indigo-300` 
        : base
    case 'revealed':
      return 'bg-gradient-to-r from-amber-50 to-yellow-50 shadow-lg ring-2 ring-amber-300'
    case 'hint':
      return 'bg-gray-100 shadow-sm'
    default:
      return 'bg-gray-200 shadow-sm'
  }
})

const iconBgClass = computed(() => {
  const tier = props.facility.tier
  const tierColors = {
    1: 'bg-slate-100',
    2: 'bg-blue-100',
    3: 'bg-purple-100',
    4: 'bg-orange-100',
    5: 'bg-pink-100',
    6: 'bg-amber-100'
  }
  return tierColors[tier] || 'bg-gray-100'
})

const formatNumber = (num) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return Math.floor(num).toLocaleString()
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
