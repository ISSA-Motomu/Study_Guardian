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

    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import MainGameView from './MainGameView.vue'
import FacilityListView from './FacilityListView.vue'
import TechTreeViewAdvanced from './TechTreeViewAdvanced.vue'

const evolutionStore = useEvolutionStore()
const currentView = ref('main')

const handleNavigate = (view) => {
  currentView.value = view
}

const handleBuy = (facilityId) => {
  evolutionStore.buyFacility(facilityId)
}

onMounted(async () => {
  await evolutionStore.initialize()
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
</style>
