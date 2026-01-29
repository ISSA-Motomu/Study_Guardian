<template>
  <div 
    class="main-game-view relative min-h-[calc(100vh-180px)] overflow-hidden"
    @click="handleTap"
    @touchstart.passive="handleTouchStart"
    @touchmove.passive="handleTouchMove"
  >
    <!-- Parallax Space Background -->
    <SpaceBackground 
      :progress="evolutionStore.totalEarnedPoints" 
      :parallaxOffset="parallaxOffset"
    />

    <!-- Particle System -->
    <KPParticlesAdvanced ref="particleSystem" />

    <!-- Screen Shake Container -->
    <div :class="{ 'animate-shake': isShaking }">
      
      <!-- Top Stats Bar - iPhone Optimized with Safe Area -->
      <div 
        class="absolute top-0 left-0 right-0 z-30 ios-safe-top"
        ref="kpTargetRef"
      >
        <div class="flex justify-between items-start p-4 gap-2">
          <!-- KP Display - Larger touch target -->
          <div 
            class="kp-display bg-black/50 backdrop-blur-xl rounded-2xl px-4 py-3 border border-white/20 shadow-lg flex-1"
            :class="{ 'animate-glow-pulse': isKpGlowing }"
          >
            <div class="flex items-center gap-3">
              <span class="text-3xl">💡</span>
              <div>
                <p class="text-[10px] text-white/70 font-medium uppercase tracking-wider">Knowledge</p>
                <AnimatedCounter 
                  :value="evolutionStore.knowledgePoints" 
                  class="text-2xl font-bold text-yellow-300 tabular-nums"
                  :duration="300"
                />
              </div>
            </div>
          </div>

          <!-- Multiplier Display -->
          <div class="bg-black/50 backdrop-blur-xl rounded-2xl px-4 py-3 border border-white/20 shadow-lg">
            <div class="flex items-center gap-2">
              <span class="text-2xl">🔬</span>
              <div class="text-right">
                <p class="text-[10px] text-white/70 font-medium uppercase tracking-wider">効率</p>
                <p class="text-xl font-bold text-cyan-300 tabular-nums">×{{ evolutionStore.totalMultiplier.toFixed(1) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- XP (Shop Currency) - Pill style -->
        <div class="px-4">
          <div class="bg-black/40 backdrop-blur-lg rounded-full px-4 py-2 inline-flex items-center gap-2">
            <span class="text-lg">⭐</span>
            <span class="text-sm text-amber-300 font-bold tabular-nums">{{ userStore.user.xp || 0 }}</span>
            <span class="text-[10px] text-white/50">XP</span>
          </div>
        </div>
      </div>

      <!-- Central Evolution Visual - Better touch feedback -->
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
        <EvolutionStage 
          :totalKP="evolutionStore.totalEarnedPoints"
          :isActive="tapFeedbackActive"
          class="pointer-events-auto transform-gpu"
        />
      </div>

      <!-- Floating Tap Indicator -->
      <div 
        v-for="floater in floatingNumbers" 
        :key="floater.id"
        class="floating-number"
        :style="{ left: floater.x + 'px', top: floater.y + 'px' }"
      >
        +{{ floater.value }}
      </div>

      <!-- Tap Feedback Ripple -->
      <div 
        v-for="ripple in tapRipples" 
        :key="ripple.id"
        class="tap-ripple"
        :style="{ left: ripple.x + 'px', top: ripple.y + 'px' }"
      />

      <!-- Bottom Progress Bar - iPhone safe area aware -->
      <div class="absolute bottom-28 left-4 right-4 z-20">
        <div v-if="evolutionStore.nextUnlock" class="bg-black/50 backdrop-blur-xl rounded-2xl p-4 border border-white/20 shadow-lg">
          <div class="flex justify-between text-xs text-white/80 mb-2">
            <span class="flex items-center gap-1.5">
              <span class="text-base">🔮</span>
              <span class="font-medium">次の解放:</span>
              <span class="text-cyan-300 font-bold">
                {{ evolutionStore.nextUnlock.state === 'revealed' ? evolutionStore.nextUnlock.name : '???' }}
              </span>
            </span>
            <span class="text-yellow-300 font-bold tabular-nums">{{ Math.floor(evolutionStore.nextUnlock.progressToUnlock) }}%</span>
          </div>
          <div class="h-4 bg-white/10 rounded-full overflow-hidden relative">
            <div 
              class="h-full transition-all duration-500 rounded-full relative"
              :class="progressBarClass"
              :style="{ width: evolutionStore.nextUnlock.progressToUnlock + '%' }"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent animate-shimmer-fast" />
            </div>
          </div>
        </div>
      </div>

      <!-- Navigation Buttons - iOS style -->
      <div class="absolute bottom-4 left-4 right-4 z-20 ios-safe-bottom">
        <p class="text-[10px] text-white/50 text-center mb-3 uppercase tracking-widest">タップしてKPを獲得</p>
        <div class="flex gap-2 justify-center flex-wrap">
          <button 
            @click.stop="$emit('navigate', 'list')"
            class="ios-nav-button"
          >
            <span class="text-2xl">📋</span>
            <span class="text-[10px] font-medium">施設</span>
          </button>
          <button 
            @click.stop="$emit('navigate', 'tree')"
            class="ios-nav-button"
          >
            <span class="text-2xl">🌳</span>
            <span class="text-[10px] font-medium">ツリー</span>
          </button>
          <button 
            @click.stop="$emit('navigate', 'upgrade')"
            class="ios-nav-button"
          >
            <span class="text-2xl">🔬</span>
            <span class="text-[10px] font-medium">強化</span>
          </button>
          <button 
            @click.stop="$emit('navigate', 'prestige')"
            class="ios-nav-button prestige-button"
          >
            <span class="text-2xl">🔄</span>
            <span class="text-[10px] font-medium">転生</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Unlock Celebration Overlay -->
    <transition name="celebrate">
      <div 
        v-if="showUnlockCelebration"
        class="absolute inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md ios-safe-area"
        @click="showUnlockCelebration = false"
      >
        <div class="unlock-celebration text-center px-8">
          <div class="text-7xl mb-6 animate-bounce-in">{{ unlockingFacility?.icon }}</div>
          <h2 class="text-3xl font-bold text-white mb-2">🎉 解放！</h2>
          <p class="text-2xl text-yellow-300 font-bold">{{ unlockingFacility?.name }}</p>
          <p class="text-sm text-white/70 mt-3 leading-relaxed">{{ unlockingFacility?.description }}</p>
          <button 
            @click.stop="showUnlockCelebration = false"
            class="mt-8 px-8 py-4 bg-gradient-to-r from-yellow-400 to-amber-500 text-black font-bold rounded-2xl text-lg shadow-lg active:scale-95 transition-transform"
          >
            続ける
          </button>
        </div>
        <!-- Confetti -->
        <div class="confetti-container">
          <div v-for="i in 50" :key="i" class="confetti" :style="confettiStyle(i)" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { useUserStore } from '@/stores/user'
import AnimatedCounter from './AnimatedCounter.vue'
import KPParticlesAdvanced from './KPParticlesAdvanced.vue'
import SpaceBackground from './SpaceBackground.vue'
import EvolutionStage from './EvolutionStage.vue'

const evolutionStore = useEvolutionStore()
const userStore = useUserStore()

const emit = defineEmits(['navigate'])

// Refs
const particleSystem = ref(null)
const kpTargetRef = ref(null)

// State
const isKpGlowing = ref(false)
const isShaking = ref(false)
const tapFeedbackActive = ref(false)
const tapRipples = ref([])
const parallaxOffset = ref({ x: 0, y: 0 })
const showUnlockCelebration = ref(false)
const unlockingFacility = ref(null)
let rippleId = 0

// Progress bar styling based on progress
const progressBarClass = computed(() => {
  const progress = evolutionStore.nextUnlock?.progressToUnlock || 0
  if (progress >= 80) return 'bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-300 animate-pulse-urgent'
  if (progress >= 50) return 'bg-gradient-to-r from-cyan-400 to-blue-400'
  return 'bg-gradient-to-r from-indigo-500 to-purple-500'
})

// Tap handling
const handleTap = (e) => {
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // Add ripple effect
  const id = rippleId++
  tapRipples.value.push({ id, x, y })
  setTimeout(() => {
    tapRipples.value = tapRipples.value.filter(r => r.id !== id)
  }, 600)

  // Add floating number
  const tapKP = Math.max(1, Math.floor(evolutionStore.totalMultiplier * 0.1))
  const fid = floatId++
  floatingNumbers.value.push({ id: fid, x, y, value: tapKP })
  setTimeout(() => {
    floatingNumbers.value = floatingNumbers.value.filter(f => f.id !== fid)
  }, 1000)

  // Tap feedback
  tapFeedbackActive.value = true
  setTimeout(() => tapFeedbackActive.value = false, 100)

  // Add KP (tap bonus)
  evolutionStore.addPoints(tapKP)

  // Emit particles toward KP counter
  if (particleSystem.value && kpTargetRef.value) {
    const targetRect = kpTargetRef.value.getBoundingClientRect()
    particleSystem.value.emit({
      count: Math.min(8, tapKP),
      startX: x,
      startY: y,
      targetX: targetRect.left + 60,
      targetY: targetRect.top + 40
    })
  }

  // Update parallax based on tap position
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  parallaxOffset.value = {
    x: (x - centerX) * 0.02,
    y: (y - centerY) * 0.02
  }
}

// Floating numbers for tap feedback
const floatingNumbers = ref([])
let floatId = 0

const handleTouchStart = (e) => {
  // Prevent default only for single-finger taps to avoid zoom
  // passive listener won't block, but we still track
}

const handleTouchMove = (e) => {
  // Update parallax on touch move for interactive feel
  if (e.touches.length === 1) {
    const touch = e.touches[0]
    const rect = e.currentTarget.getBoundingClientRect()
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    parallaxOffset.value = {
      x: (touch.clientX - rect.left - centerX) * 0.015,
      y: (touch.clientY - rect.top - centerY) * 0.015
    }
  }
}

// Watch for KP changes
watch(() => evolutionStore.knowledgePoints, (newVal, oldVal) => {
  if (newVal > (oldVal || 0)) {
    isKpGlowing.value = true
    setTimeout(() => isKpGlowing.value = false, 500)
  }
})

// Watch for new unlocks
let previousUnlocked = []
watch(() => evolutionStore.facilitiesWithState, (facilities) => {
  const currentUnlocked = facilities.filter(f => f.state === 'unlocked').map(f => f.id)
  const newlyUnlocked = currentUnlocked.filter(id => !previousUnlocked.includes(id))
  
  if (newlyUnlocked.length > 0 && previousUnlocked.length > 0) {
    const facility = facilities.find(f => f.id === newlyUnlocked[0])
    if (facility) {
      triggerUnlockCelebration(facility)
    }
  }
  
  previousUnlocked = currentUnlocked
}, { deep: true })

const triggerUnlockCelebration = (facility) => {
  // Screen shake
  isShaking.value = true
  setTimeout(() => isShaking.value = false, 500)
  
  // Show celebration
  unlockingFacility.value = facility
  showUnlockCelebration.value = true
}

// Confetti style generator
const confettiStyle = (i) => {
  const colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
  return {
    '--delay': `${Math.random() * 3}s`,
    '--x-end': `${(Math.random() - 0.5) * 400}px`,
    '--rotation': `${Math.random() * 720}deg`,
    left: `${Math.random() * 100}%`,
    backgroundColor: colors[i % colors.length],
    animationDelay: `${Math.random() * 0.5}s`
  }
}

onMounted(() => {
  previousUnlocked = evolutionStore.facilitiesWithState.filter(f => f.state === 'unlocked').map(f => f.id)
})
</script>

<style scoped>
.main-game-view {
  touch-action: manipulation;
  user-select: none;
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: transparent;
  overscroll-behavior: none;
}

/* iOS Safe Areas */
.ios-safe-top {
  padding-top: max(env(safe-area-inset-top, 0px), 12px);
}

.ios-safe-bottom {
  padding-bottom: max(env(safe-area-inset-bottom, 0px), 12px);
}

.ios-safe-area {
  padding: env(safe-area-inset-top, 0px) env(safe-area-inset-right, 0px) env(safe-area-inset-bottom, 0px) env(safe-area-inset-left, 0px);
}

/* iOS-style Navigation Buttons - 44px min touch target */
.ios-nav-button {
  @apply flex flex-col items-center justify-center gap-1.5 bg-white/15 backdrop-blur-xl rounded-2xl border border-white/30 text-white transition-all;
  min-width: 64px;
  min-height: 56px;
  padding: 10px 14px;
}

.ios-nav-button:active {
  @apply bg-white/30 scale-95;
  transition: transform 0.1s ease-out, background-color 0.1s ease-out;
}

/* Prestige button special styling */
.ios-nav-button.prestige-button {
  @apply bg-gradient-to-br from-amber-500/30 to-orange-500/30 border-amber-400/50;
}

.ios-nav-button.prestige-button:active {
  @apply from-amber-500/50 to-orange-500/50;
}

/* Floating tap numbers */
.floating-number {
  position: absolute;
  transform: translate(-50%, -50%);
  font-size: 24px;
  font-weight: bold;
  color: #facc15;
  text-shadow: 0 0 10px rgba(250, 204, 21, 0.8), 0 2px 4px rgba(0,0,0,0.5);
  pointer-events: none;
  animation: float-up 1s ease-out forwards;
  z-index: 40;
}

@keyframes float-up {
  0% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(0.5);
  }
  20% {
    transform: translate(-50%, -70%) scale(1.2);
  }
  100% {
    opacity: 0;
    transform: translate(-50%, -150%) scale(1);
  }
}

/* Tap Ripple Effect - Larger for mobile */
.tap-ripple {
  position: absolute;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.4) 40%, transparent 70%);
  transform: translate(-50%, -50%);
  animation: ripple-expand 0.6s ease-out forwards;
  pointer-events: none;
}

@keyframes ripple-expand {
  0% {
    width: 30px;
    height: 30px;
    opacity: 1;
  }
  100% {
    width: 200px;
    height: 200px;
    opacity: 0;
  }
}

/* KP Glow */
.animate-glow-pulse {
  animation: glow-pulse 0.5s ease-out;
}

@keyframes glow-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(250, 204, 21, 0); }
  50% { box-shadow: 0 0 30px 10px rgba(250, 204, 21, 0.4); }
}

/* Screen Shake */
.animate-shake {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
}

/* Progress Bar */
.animate-pulse-urgent {
  animation: pulse-urgent 1s ease-in-out infinite;
}

@keyframes pulse-urgent {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.3); }
}

.animate-shimmer-fast {
  animation: shimmer-fast 1.5s ease-in-out infinite;
}

@keyframes shimmer-fast {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}

/* Celebration Animation */
.celebrate-enter-active {
  animation: celebrate-in 0.5s ease-out;
}

.celebrate-leave-active {
  animation: celebrate-out 0.3s ease-in;
}

@keyframes celebrate-in {
  0% { opacity: 0; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes celebrate-out {
  0% { opacity: 1; transform: scale(1); }
  100% { opacity: 0; transform: scale(0.8); }
}

.animate-bounce-in {
  animation: bounce-in 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

@keyframes bounce-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* Confetti */
.confetti-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.confetti {
  position: absolute;
  top: -10px;
  width: 10px;
  height: 10px;
  animation: confetti-fall 3s ease-in-out infinite;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(-10px) translateX(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh) translateX(var(--x-end)) rotate(var(--rotation));
    opacity: 0;
  }
}
</style>
