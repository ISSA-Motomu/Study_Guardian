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

    <!-- Offline Reward Popup -->
    <transition name="fade">
      <div 
        v-if="showOfflineReward"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-6"
        @click="claimOfflineReward"
      >
        <div class="bg-gradient-to-br from-indigo-900 to-purple-900 rounded-3xl p-8 max-w-sm w-full border border-purple-400/50 shadow-2xl text-center">
          <div class="text-6xl mb-4">🌙</div>
          <h2 class="text-2xl font-bold text-white mb-2">おかえりなさい！</h2>
          <p class="text-purple-200 text-sm mb-4">
            あなたがいない間に施設が稼働していました
          </p>
          <div class="bg-black/30 rounded-2xl p-4 mb-6">
            <p class="text-xs text-white/50 mb-2">獲得KP</p>
            <p class="text-4xl font-bold text-yellow-400">
              +{{ formatOfflineReward }}
            </p>
          </div>
          <button 
            @click="claimOfflineReward"
            class="w-full py-4 bg-gradient-to-r from-yellow-400 to-amber-500 text-black font-bold rounded-2xl text-lg active:scale-95 transition-all"
          >
            受け取る！
          </button>
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

const handleNavigate = (view) => {
  currentView.value = view
}

const handleBuy = (facilityId) => {
  evolutionStore.buyFacility(facilityId)
}

const formatOfflineReward = computed(() => {
  return evolutionStore.formatNumber(evolutionStore.pendingOfflineReward)
})

const claimOfflineReward = () => {
  evolutionStore.claimOfflineReward()
  showOfflineReward.value = false
}

onMounted(async () => {
  await evolutionStore.initialize()
  
  // Check for offline reward
  if (evolutionStore.pendingOfflineReward > 0) {
    showOfflineReward.value = true
  }
})
</script>

<style scoped>
.game-container {
  min-height: calc(100vh - 100px);
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
