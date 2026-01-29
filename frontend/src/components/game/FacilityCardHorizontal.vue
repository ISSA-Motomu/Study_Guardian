<template>
  <div 
    class="facility-card-horizontal relative rounded-2xl overflow-hidden transition-all duration-300 flex-shrink-0"
    :class="cardClass"
    :style="{ width: '160px' }"
  >
    <!-- Locked State -->
    <template v-if="facility.state === 'locked'">
      <div class="p-3 flex flex-col items-center justify-center h-[180px]">
        <div class="relative w-14 h-14 mb-2">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4"/>
            <circle
              cx="32" cy="32" r="28" fill="none" stroke="rgba(100,116,139,0.5)" stroke-width="4"
              stroke-linecap="round" :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - facility.progressToUnlock / 100)"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl filter grayscale blur-[2px] opacity-30">{{ facility.icon }}</span>
          </div>
        </div>
        <p class="text-gray-400 font-semibold text-sm">???</p>
        <p class="text-[10px] text-gray-500">{{ formatNumber(facility.unlockCondition) }} KP</p>
      </div>
    </template>

    <!-- Hint State -->
    <template v-else-if="facility.state === 'hint'">
      <div class="p-3 flex flex-col items-center justify-center h-[180px]">
        <div class="relative w-14 h-14 mb-2">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4"/>
            <circle
              cx="32" cy="32" r="28" fill="none" :stroke="tierColor" stroke-width="4"
              stroke-linecap="round" :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - facility.progressToUnlock / 100)"
              class="animate-pulse"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl filter blur-[1px] opacity-60">{{ facility.icon }}</span>
          </div>
        </div>
        <p class="text-gray-300 font-semibold text-sm">???</p>
        <p class="text-[10px] text-cyan-400">{{ Math.floor(facility.progressToUnlock) }}%</p>
      </div>
    </template>

    <!-- Revealed State -->
    <template v-else-if="facility.state === 'revealed'">
      <div class="p-3 flex flex-col items-center justify-center h-[180px] relative">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-amber-400/10 to-transparent animate-shimmer-slow" />
        <div class="relative w-14 h-14 mb-2">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(251,191,36,0.2)" stroke-width="4"/>
            <circle
              cx="32" cy="32" r="28" fill="none" stroke="#fbbf24" stroke-width="4"
              stroke-linecap="round" :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - facility.progressToUnlock / 100)"
              class="animate-pulse"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-3xl animate-pulse">{{ facility.icon }}</span>
          </div>
        </div>
        <p class="text-amber-300 font-bold text-sm truncate max-w-full px-1">{{ facility.name }}</p>
        <p class="text-[10px] text-amber-400">{{ Math.floor(facility.progressToUnlock) }}%</p>
      </div>
    </template>

    <!-- Unlocked State - Main Card -->
    <template v-else>
      <div class="p-3 flex flex-col h-[180px]">
        <!-- Top: Icon & Level -->
        <div class="flex items-start justify-between mb-2">
          <div class="relative">
            <div 
              class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
              :class="tierBgClass"
            >
              {{ facility.icon }}
            </div>
            <!-- Level Badge -->
            <div 
              v-if="facility.level > 0"
              class="absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow"
              :class="tierBadgeClass"
            >
              {{ facility.level > 99 ? '99+' : facility.level }}
            </div>
          </div>
          <!-- Milestone Bonus -->
          <div v-if="facility.milestoneBonus > 1" class="bg-yellow-400/20 rounded-lg px-1.5 py-0.5">
            <span class="text-[10px] text-yellow-400 font-bold">×{{ facility.milestoneBonus }}</span>
          </div>
        </div>

        <!-- Name -->
        <h3 class="font-bold text-white text-sm truncate mb-1">{{ facility.name }}</h3>

        <!-- Production -->
        <div class="flex-1">
          <div v-if="facility.level > 0" class="space-y-1">
            <div class="flex items-center gap-1 text-green-400 text-xs">
              <span>⚡</span>
              <span class="font-bold">+{{ formatNumber(facility.production) }}/分</span>
            </div>
            <!-- Production Bar (% of total) -->
            <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-green-400 to-emerald-400 transition-all"
                :style="{ width: productionPercent + '%' }"
              />
            </div>
            <p class="text-[9px] text-white/40">総生産の {{ productionPercent.toFixed(1) }}%</p>
          </div>
          <div v-else class="text-xs text-white/50">
            未購入
          </div>
        </div>

        <!-- Buy Section -->
        <div class="mt-auto pt-2 border-t border-white/10">
          <div class="flex items-center gap-1">
            <!-- Dropdown -->
            <select
              v-model="selectedAmount"
              @click.stop
              class="flex-1 px-1 py-1.5 rounded-lg text-[10px] font-bold bg-white/10 text-white border border-white/20 appearance-none cursor-pointer text-center"
            >
              <option value="1">×1</option>
              <option value="10">×10</option>
              <option value="100">×100</option>
              <option value="-1">MAX</option>
            </select>
            <!-- Buy Button -->
            <button
              @click.stop="handleBuyClick"
              :disabled="!canAffordMultiple"
              class="flex-1 py-1.5 rounded-lg font-bold text-[10px] transition-all flex items-center justify-center gap-0.5"
              :class="buyButtonClass"
            >
              <span>{{ facility.level === 0 ? '🔓' : '⬆️' }}</span>
              <span>{{ formatNumber(displayCost) }}</span>
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'

const props = defineProps({
  facility: { type: Object, required: true }
})

const emit = defineEmits(['buy'])
const evolutionStore = useEvolutionStore()

const selectedAmount = ref(1)
const circumference = 2 * Math.PI * 28

const formatNumber = (num) => evolutionStore.formatNumber(num)

const handleBuyClick = () => {
  const amount = parseInt(selectedAmount.value)
  emit('buy', { facilityId: props.facility.id, amount })
}

// 購入可能数と合計コストを計算
const purchaseInfo = computed(() => {
  if (props.facility.state !== 'unlocked') return { canBuy: 0, totalCost: 0 }
  
  const amount = parseInt(selectedAmount.value)
  const targetAmount = amount === -1 ? 1000 : amount
  let totalCost = 0, canBuy = 0
  let tempKP = evolutionStore.knowledgePoints
  let tempLevel = props.facility.level || 0
  
  for (let i = 0; i < targetAmount; i++) {
    const cost = evolutionStore.calculateCost(props.facility.baseCost, tempLevel)
    if (tempKP >= cost) {
      tempKP -= cost
      totalCost += cost
      tempLevel++
      canBuy++
    } else break
  }
  return { canBuy, totalCost }
})

const displayCost = computed(() => {
  const amount = parseInt(selectedAmount.value)
  return amount === 1 ? props.facility.currentCost : purchaseInfo.value.totalCost
})

const canAffordMultiple = computed(() => purchaseInfo.value.canBuy > 0)

// 総生産に対する割合
const productionPercent = computed(() => {
  if (!props.facility.production || !evolutionStore.currentProduction) return 0
  return (props.facility.production / evolutionStore.currentProduction) * 100
})

// Tier styles
const tierColors = {
  1: { color: '#64748b', bg: 'bg-slate-700', badge: 'bg-slate-500' },
  2: { color: '#3b82f6', bg: 'bg-blue-900', badge: 'bg-blue-500' },
  3: { color: '#8b5cf6', bg: 'bg-purple-900', badge: 'bg-purple-500' },
  4: { color: '#f97316', bg: 'bg-orange-900', badge: 'bg-orange-500' },
  5: { color: '#ec4899', bg: 'bg-pink-900', badge: 'bg-pink-500' },
  6: { color: '#f59e0b', bg: 'bg-amber-900', badge: 'bg-amber-500' }
}

const tierColor = computed(() => tierColors[props.facility.tier]?.color || '#64748b')
const tierBgClass = computed(() => tierColors[props.facility.tier]?.bg || 'bg-slate-700')
const tierBadgeClass = computed(() => tierColors[props.facility.tier]?.badge || 'bg-slate-500')

const cardClass = computed(() => {
  switch (props.facility.state) {
    case 'unlocked':
      return props.facility.level > 0 
        ? 'bg-slate-800/90 border border-white/20' 
        : 'bg-slate-800/70 border border-white/10'
    case 'revealed':
      return 'bg-gradient-to-b from-amber-900/80 to-yellow-900/80 border border-amber-400/50'
    case 'hint':
      return 'bg-gray-800/80 border border-white/10'
    default:
      return 'bg-gray-900/80 border border-white/5'
  }
})

const buyButtonClass = computed(() => {
  return canAffordMultiple.value
    ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white active:scale-95'
    : 'bg-white/10 text-white/30 cursor-not-allowed'
})
</script>

<style scoped>
.animate-shimmer-slow {
  animation: shimmer-slow 3s ease-in-out infinite;
}

@keyframes shimmer-slow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
</style>
