<template>
  <div 
    class="facility-card-advanced relative rounded-2xl overflow-hidden transition-all duration-300"
    :class="cardClass"
    @click="handleClick"
  >
    <!-- Background Glow for unlocked -->
    <div 
      v-if="facility.state === 'unlocked' && facility.level > 0"
      class="absolute inset-0 bg-gradient-to-br opacity-20"
      :class="tierGradient"
    />

    <!-- Locked State - Heavy Silhouette -->
    <template v-if="facility.state === 'locked'">
      <div class="p-4 flex items-center gap-4">
        <!-- Circular Progress Ring -->
        <div class="relative w-16 h-16 shrink-0">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
            <!-- Background ring -->
            <circle
              cx="32" cy="32" r="28"
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              stroke-width="4"
            />
            <!-- Progress ring -->
            <circle
              cx="32" cy="32" r="28"
              fill="none"
              stroke="rgba(100,116,139,0.5)"
              stroke-width="4"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - facility.progressToUnlock / 100)"
              class="transition-all duration-500"
            />
          </svg>
          <!-- Center Icon (Silhouette) -->
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl filter grayscale blur-[2px] opacity-30">{{ facility.icon }}</span>
          </div>
        </div>
        <!-- Info -->
        <div class="flex-1">
          <p class="text-gray-400 font-semibold">???</p>
          <p class="text-xs text-gray-500 mt-1">未発見の施設</p>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs text-gray-500">🔒</span>
            <span class="text-xs text-gray-400">{{ formatNumber(facility.unlockCondition) }} KP で解放</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Hint State - Partial Reveal with Progress -->
    <template v-else-if="facility.state === 'hint'">
      <div class="p-4 flex items-center gap-4">
        <!-- Circular Progress Ring -->
        <div class="relative w-16 h-16 shrink-0">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="4"/>
            <circle
              cx="32" cy="32" r="28"
              fill="none"
              :stroke="tierColor"
              stroke-width="4"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - facility.progressToUnlock / 100)"
              class="transition-all duration-500"
              :class="{ 'animate-pulse-ring': facility.progressToUnlock > 40 }"
            />
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-2xl filter blur-[1px] opacity-60">{{ facility.icon }}</span>
          </div>
          <!-- Progress Percentage -->
          <div class="absolute -bottom-1 -right-1 bg-gray-700 rounded-full px-1.5 py-0.5">
            <span class="text-[10px] text-gray-300 font-bold">{{ Math.floor(facility.progressToUnlock) }}%</span>
          </div>
        </div>
        <!-- Info -->
        <div class="flex-1">
          <p class="text-gray-300 font-semibold">???</p>
          <p class="text-xs text-gray-500 mt-1">施設の気配を感じる...</p>
          <div class="mt-2 flex items-center gap-2 text-xs">
            <span class="text-gray-400">あと {{ formatNumber(facility.unlockCondition - currentTotalPoints) }} KP</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Revealed State - Almost Unlocked -->
    <template v-else-if="facility.state === 'revealed'">
      <div class="p-4 flex items-center gap-4 relative overflow-hidden">
        <!-- Shimmer effect -->
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-amber-400/10 to-transparent animate-shimmer-slow" />
        
        <!-- Circular Progress Ring (Glowing) -->
        <div class="relative w-16 h-16 shrink-0">
          <svg class="w-full h-full transform -rotate-90" viewBox="0 0 64 64">
            <circle cx="32" cy="32" r="28" fill="none" stroke="rgba(251,191,36,0.2)" stroke-width="4"/>
            <circle
              cx="32" cy="32" r="28"
              fill="none"
              stroke="url(#gold-gradient)"
              stroke-width="4"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="circumference * (1 - facility.progressToUnlock / 100)"
              class="transition-all duration-500 animate-pulse-ring-gold"
            />
            <defs>
              <linearGradient id="gold-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#fbbf24"/>
                <stop offset="50%" stop-color="#f59e0b"/>
                <stop offset="100%" stop-color="#fbbf24"/>
              </linearGradient>
            </defs>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <span class="text-3xl animate-pulse">{{ facility.icon }}</span>
          </div>
          <div class="absolute -bottom-1 -right-1 bg-amber-500 rounded-full px-1.5 py-0.5">
            <span class="text-[10px] text-black font-bold">{{ Math.floor(facility.progressToUnlock) }}%</span>
          </div>
        </div>
        <!-- Info -->
        <div class="flex-1">
          <p class="text-amber-300 font-bold">{{ facility.name }}</p>
          <p class="text-xs text-amber-200/70 mt-1">{{ facility.description }}</p>
          <div class="mt-2 flex items-center gap-2 text-xs">
            <span class="text-amber-400 font-semibold">
              🔓 あと {{ formatNumber(facility.unlockCondition - currentTotalPoints) }} KP!
            </span>
          </div>
        </div>
      </div>
    </template>

    <!-- Unlocked State - Full Display -->
    <template v-else>
      <div class="p-4 flex items-center gap-4">
        <!-- Icon with Level Badge -->
        <div class="relative w-16 h-16 shrink-0">
          <div 
            class="w-full h-full rounded-xl flex items-center justify-center text-3xl"
            :class="tierBgClass"
          >
            {{ facility.icon }}
          </div>
          <!-- Level Badge -->
          <div 
            v-if="facility.level > 0"
            class="absolute -top-1 -right-1 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
            :class="tierBadgeClass"
          >
            {{ facility.level }}
          </div>
        </div>

        <!-- Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <h3 class="font-bold text-gray-800 truncate">{{ facility.name }}</h3>
          </div>
          <p class="text-xs text-gray-500 mt-0.5 line-clamp-1">{{ facility.description }}</p>
          
          <!-- Stats -->
          <div class="flex items-center gap-3 mt-2 text-xs">
            <div class="flex items-center gap-1 text-green-600">
              <span>⚡</span>
              <span>+{{ facility.production.toFixed(1) }}/分</span>
            </div>
            <div class="flex items-center gap-1 text-gray-500">
              <span>💡</span>
              <span>{{ formatNumber(facility.currentCost) }} KP</span>
            </div>
          </div>
        </div>

        <!-- Buy Button -->
        <button
          @click.stop="$emit('buy', facility.id)"
          :disabled="!facility.canAfford"
          class="px-4 py-3 rounded-xl font-bold text-sm transition-all shrink-0"
          :class="buyButtonClass"
        >
          <span v-if="facility.level === 0">🔓</span>
          <span v-else>⬆️</span>
        </button>
      </div>

      <!-- Level Progress Bar -->
      <div v-if="facility.level > 0" class="px-4 pb-3">
        <div class="h-1 bg-gray-200 rounded-full overflow-hidden">
          <div 
            class="h-full transition-all duration-300"
            :class="tierGradient"
            :style="{ width: (facility.level % 10) * 10 + '%' }"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'

const props = defineProps({
  facility: { type: Object, required: true }
})

defineEmits(['buy'])

const evolutionStore = useEvolutionStore()
const currentTotalPoints = computed(() => evolutionStore.totalEarnedPoints)

// SVG circle circumference
const circumference = 2 * Math.PI * 28

// Tier colors
const tierColors = {
  1: { color: '#64748b', gradient: 'from-slate-400 to-slate-600', bg: 'bg-slate-100', badge: 'bg-slate-500' },
  2: { color: '#3b82f6', gradient: 'from-blue-400 to-blue-600', bg: 'bg-blue-100', badge: 'bg-blue-500' },
  3: { color: '#8b5cf6', gradient: 'from-purple-400 to-purple-600', bg: 'bg-purple-100', badge: 'bg-purple-500' },
  4: { color: '#f97316', gradient: 'from-orange-400 to-red-500', bg: 'bg-orange-100', badge: 'bg-orange-500' },
  5: { color: '#ec4899', gradient: 'from-pink-400 to-purple-600', bg: 'bg-pink-100', badge: 'bg-pink-500' },
  6: { color: '#f59e0b', gradient: 'from-yellow-400 to-amber-500', bg: 'bg-amber-100', badge: 'bg-amber-500' }
}

const tierColor = computed(() => tierColors[props.facility.tier]?.color || '#64748b')
const tierGradient = computed(() => `bg-gradient-to-r ${tierColors[props.facility.tier]?.gradient || 'from-gray-400 to-gray-600'}`)
const tierBgClass = computed(() => tierColors[props.facility.tier]?.bg || 'bg-gray-100')
const tierBadgeClass = computed(() => tierColors[props.facility.tier]?.badge || 'bg-gray-500')

const cardClass = computed(() => {
  switch (props.facility.state) {
    case 'unlocked':
      return props.facility.level > 0 
        ? 'bg-white shadow-md ring-2 ring-indigo-200' 
        : 'bg-white shadow-md'
    case 'revealed':
      return 'bg-gradient-to-r from-amber-900/90 to-yellow-900/90 shadow-lg ring-2 ring-amber-400/50'
    case 'hint':
      return 'bg-gray-800/90 shadow-md'
    default:
      return 'bg-gray-900/90 shadow-sm'
  }
})

const buyButtonClass = computed(() => {
  if (props.facility.canAfford) {
    return 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg hover:shadow-xl active:scale-95'
  }
  return 'bg-gray-200 text-gray-400 cursor-not-allowed'
})

const handleClick = () => {
  // カード全体タップでも購入可能（モバイル用）
  if (props.facility.state === 'unlocked' && props.facility.canAfford) {
    // 購入ボタンがあるのでここでは何もしない
  }
}

const formatNumber = (num) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return Math.floor(num).toLocaleString()
}
</script>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.animate-pulse-ring {
  animation: pulse-ring 2s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.animate-pulse-ring-gold {
  animation: pulse-ring-gold 1.5s ease-in-out infinite;
  filter: drop-shadow(0 0 4px rgba(251, 191, 36, 0.5));
}

@keyframes pulse-ring-gold {
  0%, 100% { 
    opacity: 0.8;
    filter: drop-shadow(0 0 4px rgba(251, 191, 36, 0.5));
  }
  50% { 
    opacity: 1;
    filter: drop-shadow(0 0 8px rgba(251, 191, 36, 0.8));
  }
}

.animate-shimmer-slow {
  animation: shimmer-slow 3s ease-in-out infinite;
}

@keyframes shimmer-slow {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
</style>
