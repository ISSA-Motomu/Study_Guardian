<template>
  <div class="game-container">
    <!-- Screen Transitions -->
    <transition name="fade-slide" mode="out-in">
      
      <!-- Main Game View (Tap & Collect) -->
      <MainGameView 
        v-if="currentView === 'main'"
        key="main"
        @navigate="handleNavigate"
      />

      <!-- Facility List View -->
      <FacilityListView 
        v-else-if="currentView === 'list'"
        key="list"
        @navigate="handleNavigate"
      />

      <!-- Tech Tree View -->
      <TechTreeViewAdvanced 
        v-else-if="currentView === 'tree'"
        key="tree"
        @navigate="handleNavigate"
        @buy="handleBuy"
      />

      <!-- Upgrade Panel -->
      <UpgradePanel 
        v-else-if="currentView === 'upgrade'"
        key="upgrade"
        @navigate="handleNavigate"
      />

      <!-- Prestige View -->
      <PrestigeView 
        v-else-if="currentView === 'prestige'"
        key="prestige"
        @navigate="handleNavigate"
      />

    </transition>

    <!-- Offline Reward Popup - Enhanced Visual -->
    <transition name="fade">
      <div 
        v-if="showOfflineReward"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4"
      >
        <!-- Floating particles -->
        <div class="absolute inset-0 pointer-events-none overflow-hidden">
          <div v-for="i in 15" :key="'p'+i" class="offline-particle" :style="particleStyle(i)" />
        </div>
        
        <div class="bg-gradient-to-br from-indigo-900 via-purple-900 to-indigo-950 rounded-3xl p-6 max-w-sm w-full border border-purple-400/50 shadow-2xl text-center relative overflow-hidden">
          <!-- Background glow -->
          <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div class="w-64 h-64 rounded-full bg-gradient-radial from-yellow-400/20 via-amber-500/10 to-transparent animate-pulse" />
          </div>
          
          <!-- Content -->
          <div class="relative z-10">
            <div class="text-7xl mb-3 animate-bounce">🌙</div>
            <h2 class="text-2xl font-bold text-white mb-1">おかえりなさい！</h2>
            <p class="text-purple-200 text-sm mb-4">
              あなたがいない間に施設が稼働していました
            </p>
            
            <!-- Offline Details -->
            <div class="bg-black/40 rounded-2xl p-4 mb-4 space-y-3">
              <div class="flex justify-between items-center text-sm">
                <span class="text-white/60">⏱️ 経過時間</span>
                <span class="text-cyan-300 font-bold">{{ offlineTimeDisplay }}</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-white/60">⚡ 生産効率</span>
                <span class="text-green-300 font-bold">{{ evolutionStore.formatNumber(evolutionStore.currentProduction) }}/分</span>
              </div>
              <div class="flex justify-between items-center text-sm">
                <span class="text-white/60">📊 オフライン効率</span>
                <span class="text-amber-300 font-bold">50%</span>
              </div>
            </div>
            
            <!-- Main Reward -->
            <div class="bg-gradient-to-br from-yellow-500/20 to-amber-500/20 rounded-2xl p-5 mb-5 border border-yellow-400/30">
              <p class="text-xs text-white/50 mb-1 uppercase tracking-wider">獲得Knowledge Points</p>
              <div class="flex items-center justify-center gap-2">
                <span class="text-4xl">💡</span>
                <p class="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-amber-400 to-yellow-300 animate-pulse">
                  +{{ formatOfflineReward }}
                </p>
              </div>
              <p class="text-xs text-yellow-200/60 mt-2">現在の所持: {{ evolutionStore.formatNumber(evolutionStore.knowledgePoints) }} KP</p>
            </div>
            
            <button 
              @click="claimOfflineReward"
              class="w-full py-4 bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-400 text-black font-bold rounded-2xl text-lg active:scale-95 transition-all shadow-lg hover:shadow-yellow-400/50 relative overflow-hidden group"
            >
              <span class="relative z-10">🎁 報酬を受け取る！</span>
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-500" />
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import MainGameView from './MainGameView.vue'
import FacilityListView from './FacilityListView.vue'
import TechTreeViewAdvanced from './TechTreeViewAdvanced.vue'
import UpgradePanel from './UpgradePanel.vue'
import PrestigeView from './PrestigeView.vue'

const evolutionStore = useEvolutionStore()
const currentView = ref('main')
const showOfflineReward = ref(false)
const offlineSeconds = ref(0)

const handleNavigate = (view) => {
  currentView.value = view
}

const handleBuy = (facilityId) => {
  evolutionStore.buyFacility(facilityId)
}

const formatOfflineReward = computed(() => {
  return evolutionStore.formatNumber(evolutionStore.pendingOfflineReward)
})

// オフライン経過時間の表示
const offlineTimeDisplay = computed(() => {
  const seconds = offlineSeconds.value
  if (seconds < 60) return `${seconds}秒`
  if (seconds < 3600) return `${Math.floor(seconds / 60)}分`
  const hours = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  if (hours < 24) return `${hours}時間${mins}分`
  const days = Math.floor(hours / 24)
  return `${days}日${hours % 24}時間`
})

// パーティクルスタイル
const particleStyle = (i) => {
  return {
    '--delay': `${Math.random() * 3}s`,
    '--x': `${Math.random() * 100}%`,
    '--size': `${4 + Math.random() * 8}px`,
    left: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 2}s`
  }
}

const claimOfflineReward = () => {
  evolutionStore.claimOfflineReward()
  showOfflineReward.value = false
}

onMounted(async () => {
  await evolutionStore.initialize()
  
  // Check for offline reward
  if (evolutionStore.pendingOfflineReward > 0) {
    // 経過時間を計算（lastActiveTimeから）
    const now = Date.now()
    const lastActive = evolutionStore.lastActiveTime || now
    offlineSeconds.value = Math.floor((now - lastActive) / 1000)
    showOfflineReward.value = true
  }
})
</script>

<style scoped>
.game-container {
  min-height: calc(100vh - 100px);
}

/* Offline Reward Particles */
.offline-particle {
  position: absolute;
  width: var(--size, 6px);
  height: var(--size, 6px);
  background: linear-gradient(135deg, #fcd34d, #f59e0b);
  border-radius: 50%;
  animation: float-up 4s ease-in-out infinite;
  opacity: 0;
}

@keyframes float-up {
  0% {
    opacity: 0;
    transform: translateY(100vh) scale(0);
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateY(-100px) scale(1.5);
  }
}

/* Screen Transitions */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
