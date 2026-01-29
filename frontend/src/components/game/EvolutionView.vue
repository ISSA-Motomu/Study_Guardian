<template>
  <div class="relative pb-8" ref="mainContainer">
    <!-- Particle System -->
    <KPParticles ref="particleSystem" icon="💡" />

    <!-- Currency Display Header -->
    <div 
      class="sticky top-0 z-20 -mx-6 px-6 py-3 rounded-b-2xl shadow-lg kp-target"
      :class="headerClass"
    >
      <!-- Dual Currency Display -->
      <div class="grid grid-cols-2 gap-3 mb-3">
        <!-- KP (Game Currency) with Animation -->
        <div 
          class="bg-white/20 rounded-xl p-2 text-center relative overflow-hidden"
          :class="{ 'animate-pulse-glow': isKpGlowing }"
        >
          <div class="absolute inset-0 bg-gradient-to-r from-yellow-400/0 via-yellow-400/30 to-yellow-400/0 animate-shimmer" v-if="isKpGlowing" />
          <div class="relative z-10">
            <div class="flex items-center justify-center gap-1">
              <span class="text-lg">💡</span>
              <span class="text-xs text-white/80">KP</span>
            </div>
            <AnimatedCounter 
              :value="evolutionStore.knowledgePoints" 
              class="text-xl font-bold text-white"
            />
            <p class="text-[10px] text-white/60">ゲーム内専用</p>
          </div>
        </div>
        <!-- XP (Shop Currency) -->
        <div class="bg-black/20 rounded-xl p-2 text-center">
          <div class="flex items-center justify-center gap-1">
            <span class="text-lg">⭐</span>
            <span class="text-xs text-white/80">XP</span>
          </div>
          <AnimatedCounter 
            :value="userStore.user.xp || 0" 
            class="text-xl font-bold text-amber-300"
          />
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
          <AnimatedCounter 
            :value="evolutionStore.totalEarnedPoints" 
            class="text-lg font-semibold"
          />
        </div>
      </div>
      
      <!-- Progress to next unlock with pulsing -->
      <div v-if="evolutionStore.nextUnlock" class="mt-3">
        <div class="flex justify-between text-xs text-white/70 mb-1">
          <span>次の解放: {{ evolutionStore.nextUnlock.state === 'revealed' ? evolutionStore.nextUnlock.name : '???' }}</span>
          <span>{{ Math.floor(evolutionStore.nextUnlock.progressToUnlock) }}%</span>
        </div>
        <div class="h-2 bg-white/20 rounded-full overflow-hidden relative">
          <div 
            class="h-full bg-gradient-to-r from-amber-400 to-yellow-300 transition-all duration-500 relative"
            :style="{ width: evolutionStore.nextUnlock.progressToUnlock + '%' }"
          >
            <div class="absolute inset-0 bg-white/50 animate-pulse-bar" />
          </div>
        </div>
      </div>
    </div>

    <!-- View Mode Toggle -->
    <div class="flex gap-2 p-1 bg-white/50 rounded-xl backdrop-blur-sm mt-4 mb-4">
      <button
        @click="viewMode = 'list'"
        class="flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all"
        :class="viewMode === 'list' 
          ? 'bg-white text-indigo-600 shadow-md' 
          : 'text-gray-500 hover:text-gray-700'"
      >
        📋 リスト
      </button>
      <button
        @click="viewMode = 'tree'"
        class="flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all"
        :class="viewMode === 'tree' 
          ? 'bg-white text-purple-600 shadow-md' 
          : 'text-gray-500 hover:text-gray-700'"
      >
        🌳 テックツリー
      </button>
    </div>

    <!-- List View -->
    <template v-if="viewMode === 'list'">
      <!-- Summary Card -->
      <GlassPanel class="text-center mb-4">
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

      <!-- Facility List by Tier -->
      <div class="space-y-6">
        <div
          v-for="tierGroup in evolutionStore.facilitiesByTier"
          :key="tierGroup.tier"
          class="relative"
        >
          <div 
            class="sticky top-[140px] z-10 -mx-2 px-3 py-2 rounded-lg mb-3"
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
    </template>

    <!-- Tech Tree View -->
    <template v-else>
      <TechTreeView 
        :facilities="evolutionStore.facilitiesWithState"
        @buy="handleBuy"
      />
    </template>

    <!-- Debug Button -->
    <div v-if="isDev" class="fixed bottom-24 right-4 flex flex-col gap-2">
      <button
        @click="debugAddAndAnimate(1000)"
        class="p-3 bg-red-500 text-white rounded-full shadow-lg"
      >
        +1000
      </button>
      <button
        @click="triggerParticles"
        class="p-3 bg-purple-500 text-white rounded-full shadow-lg text-xs"
      >
        ✨
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
import { onMounted, ref, watch } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { useUserStore } from '@/stores/user'
import GlassPanel from '@/components/common/GlassPanel.vue'
import FacilityCard from './FacilityCard.vue'
import AnimatedCounter from './AnimatedCounter.vue'
import KPParticles from './KPParticles.vue'
import TechTreeView from './TechTreeView.vue'

const evolutionStore = useEvolutionStore()
const userStore = useUserStore()
const isDev = ref(import.meta.env.DEV)
const viewMode = ref('list')
const isKpGlowing = ref(false)
const particleSystem = ref(null)
const mainContainer = ref(null)

// Header pulsing class based on activity
const headerClass = ref('bg-gradient-to-r from-indigo-600/90 to-purple-600/90 backdrop-blur-lg')

onMounted(async () => {
  await evolutionStore.initialize()
})

// Watch for KP changes to trigger effects
let previousKp = 0
watch(() => evolutionStore.knowledgePoints, (newVal, oldVal) => {
  if (newVal > (oldVal || previousKp)) {
    isKpGlowing.value = true
    setTimeout(() => isKpGlowing.value = false, 1000)
    
    // Trigger particles on KP gain
    if (particleSystem.value && newVal - (oldVal || 0) > 0) {
      particleSystem.value.emit(Math.min(10, Math.ceil((newVal - (oldVal || 0)) / 100)))
    }
  }
  previousKp = newVal
})

const handleBuy = (facilityId) => {
  const success = evolutionStore.buyFacility(facilityId)
  if (success) {
    // 購入成功のフィードバック
    isKpGlowing.value = true
    setTimeout(() => isKpGlowing.value = false, 500)
  }
}

// Debug functions
const debugAddAndAnimate = (amount) => {
  evolutionStore.debugAddPoints(amount)
  triggerParticles()
}

const triggerParticles = () => {
  if (particleSystem.value) {
    particleSystem.value.emit(8)
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

.animate-pulse-glow {
  animation: pulse-glow 0.5s ease-out;
}

@keyframes pulse-glow {
  0% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0.4); }
  50% { box-shadow: 0 0 20px 10px rgba(250, 204, 21, 0.2); }
  100% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0); }
}

.animate-shimmer {
  animation: shimmer 1s ease-out;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.animate-pulse-bar {
  animation: pulse-bar 2s ease-in-out infinite;
}

@keyframes pulse-bar {
  0%, 100% { opacity: 0; }
  50% { opacity: 0.5; }
}
</style>

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
