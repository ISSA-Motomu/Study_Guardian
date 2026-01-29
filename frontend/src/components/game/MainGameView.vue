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
      <div class="absolute bottom-24 left-3 right-3 z-20 sm:bottom-28 sm:left-4 sm:right-4">
        <div v-if="evolutionStore.nextUnlock" class="bg-black/50 backdrop-blur-xl rounded-2xl p-3 sm:p-4 border border-white/20 shadow-lg">
          <div class="flex justify-between text-xs text-white/80 mb-2">
            <span class="flex items-center gap-1.5">
              <span class="text-base">🔮</span>
              <span class="font-medium hidden sm:inline">次の解放:</span>
              <span class="text-cyan-300 font-bold text-xs sm:text-sm truncate max-w-[100px] sm:max-w-none">
                {{ evolutionStore.nextUnlock.state === 'revealed' ? evolutionStore.nextUnlock.name : '???' }}
              </span>
            </span>
            <span class="text-yellow-300 font-bold tabular-nums">{{ Math.floor(evolutionStore.nextUnlock.progressToUnlock) }}%</span>
          </div>
          <div class="h-3 sm:h-4 bg-white/10 rounded-full overflow-hidden relative">
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
      <div class="absolute bottom-2 left-1 right-1 z-20 ios-safe-bottom sm:bottom-4 sm:left-2 sm:right-2">
        <p class="text-[9px] sm:text-[10px] text-white/50 text-center mb-1 sm:mb-2 uppercase tracking-widest">タップでKP獲得</p>
        <div class="flex gap-1 sm:gap-1.5 justify-center px-1">
          <button 
            @click.stop="navigate('list')"
            class="ios-nav-button"
          >
            <span class="text-2xl sm:text-3xl">📋</span>
            <span class="text-[10px] sm:text-xs font-bold">施設</span>
          </button>
          <button 
            @click.stop="navigate('tree')"
            class="ios-nav-button"
          >
            <span class="text-2xl sm:text-3xl">🌳</span>
            <span class="text-[10px] sm:text-xs font-bold">ツリー</span>
          </button>
          <button 
            @click.stop="navigate('upgrade')"
            class="ios-nav-button"
          >
            <span class="text-2xl sm:text-3xl">🔬</span>
            <span class="text-[10px] sm:text-xs font-bold">強化</span>
          </button>
          <button 
            @click.stop="navigate('prestige')"
            class="ios-nav-button prestige-button"
          >
            <span class="text-2xl sm:text-3xl">🔄</span>
            <span class="text-[10px] sm:text-xs font-bold">転生</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Unlock Celebration Overlay - Premium Design -->
    <transition name="celebrate">
      <div 
        v-if="showUnlockCelebration"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-lg"
        @click.self="showUnlockCelebration = false"
      >
        <!-- Radial Glow Background -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div class="w-96 h-96 rounded-full bg-gradient-radial from-yellow-400/30 via-amber-500/10 to-transparent animate-pulse-slow" />
        </div>
        
        <!-- Floating Particles -->
        <div class="absolute inset-0 pointer-events-none overflow-hidden">
          <div v-for="i in 20" :key="'sparkle-'+i" class="sparkle" :style="sparkleStyle(i)" />
        </div>

        <!-- Main Content Card -->
        <div class="unlock-celebration relative z-10 max-w-sm mx-4 bg-gradient-to-br from-slate-900/95 via-indigo-900/95 to-purple-900/95 rounded-3xl p-8 border border-yellow-400/30 shadow-2xl">
          <!-- Top Badge -->
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-amber-500 px-6 py-2 rounded-full shadow-lg">
            <span class="text-black font-bold text-sm tracking-wider">🔓 NEW UNLOCK</span>
          </div>

          <!-- Icon with Glow -->
          <div class="relative mt-4 mb-6">
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="w-32 h-32 rounded-full bg-yellow-400/20 animate-ping-slow" />
            </div>
            <div class="relative text-8xl text-center animate-bounce-in filter drop-shadow-[0_0_20px_rgba(250,204,21,0.5)]">
              {{ unlockingFacility?.icon }}
            </div>
          </div>

          <!-- Title -->
          <h2 class="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-amber-400 to-yellow-300 text-center mb-2 animate-shimmer-text">
            {{ unlockingFacility?.name }}
          </h2>

          <!-- Tier Badge -->
          <div class="flex justify-center mb-4">
            <span class="px-3 py-1 text-xs font-bold rounded-full" :class="getTierBadgeClass(unlockingFacility?.tier)">
              Tier {{ unlockingFacility?.tier }} 施設
            </span>
          </div>

          <!-- Description -->
          <p class="text-white/80 text-center text-sm leading-relaxed mb-4">
            {{ unlockingFacility?.description }}
          </p>

          <!-- Academic Note - 学術的説明 -->
          <div v-if="unlockingFacility?.academicNote" class="bg-black/40 rounded-xl p-4 mb-6 border border-cyan-400/30">
            <div class="flex items-start gap-2">
              <span class="text-cyan-400 text-lg">📖</span>
              <div>
                <p class="text-[10px] text-cyan-400 font-bold uppercase tracking-wider mb-1">Academic Note</p>
                <p class="text-xs text-cyan-100/80 leading-relaxed italic">
                  {{ unlockingFacility?.academicNote }}
                </p>
              </div>
            </div>
          </div>

          <!-- Stats Preview -->
          <div class="grid grid-cols-2 gap-3 mb-6">
            <div class="bg-white/10 rounded-xl p-3 text-center">
              <p class="text-[10px] text-white/50 uppercase">生産量</p>
              <p class="text-lg font-bold text-green-400">+{{ unlockingFacility?.baseProduction }}/分</p>
            </div>
            <div class="bg-white/10 rounded-xl p-3 text-center">
              <p class="text-[10px] text-white/50 uppercase">初期コスト</p>
              <p class="text-lg font-bold text-yellow-400">{{ unlockingFacility?.baseCost }} KP</p>
            </div>
          </div>

          <!-- Flavor Text -->
          <p v-if="unlockingFacility?.flavorText" class="text-center text-white/50 text-xs italic mb-6">
            {{ unlockingFacility?.flavorText }}
          </p>

          <!-- Continue Button -->
          <button 
            @click.stop="showUnlockCelebration = false"
            class="w-full py-4 bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-400 text-black font-bold rounded-2xl text-lg shadow-lg active:scale-95 transition-all hover:shadow-yellow-400/50 hover:shadow-xl"
          >
            🚀 研究を開始する
          </button>
        </div>

        <!-- Confetti -->
        <div class="confetti-container">
          <div v-for="i in 60" :key="i" class="confetti" :style="confettiStyle(i)" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { useUserStore } from '@/stores/user'
import { soundManager } from '@/utils/sound'
import AnimatedCounter from './AnimatedCounter.vue'
import KPParticlesAdvanced from './KPParticlesAdvanced.vue'
import SpaceBackground from './SpaceBackground.vue'
import EvolutionStage from './EvolutionStage.vue'

const evolutionStore = useEvolutionStore()
const userStore = useUserStore()

const emit = defineEmits(['navigate'])

// Initialize sounds
onMounted(() => {
  document.addEventListener('click', () => soundManager.init(), { once: true })
})

// Navigation with sound
const navigate = (view) => {
  soundManager.play('click')
  emit('navigate', view)
}

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
  soundManager.play('click')
  const rect = e.currentTarget.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top

  // Add ripple effect
  const id = rippleId++
  tapRipples.value.push({ id, x, y })
  setTimeout(() => {
    tapRipples.value = tapRipples.value.filter(r => r.id !== id)
  }, 600)

  // Add floating number (タップは基本1KP、倍率によって最大でも数KP程度)
  const tapKP = Math.max(1, Math.floor(evolutionStore.totalMultiplier * 0.01))
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

// Sparkle style generator for unlock screen
const sparkleStyle = (i) => {
  return {
    '--sparkle-delay': `${Math.random() * 2}s`,
    '--sparkle-x': `${Math.random() * 100}%`,
    '--sparkle-y': `${Math.random() * 100}%`,
    '--sparkle-size': `${4 + Math.random() * 8}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`
  }
}

// Tier badge class
const getTierBadgeClass = (tier) => {
  const classes = {
    1: 'bg-slate-600 text-slate-200',
    2: 'bg-blue-600 text-blue-100',
    3: 'bg-purple-600 text-purple-100',
    4: 'bg-orange-600 text-orange-100',
    5: 'bg-pink-600 text-pink-100',
    6: 'bg-amber-600 text-amber-100'
  }
  return classes[tier] || 'bg-gray-600 text-gray-200'
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

/* iOS-style Navigation Buttons - Compact for small screens */
.ios-nav-button {
  @apply flex flex-col items-center justify-center bg-white/15 backdrop-blur-xl rounded-xl sm:rounded-2xl border border-white/30 text-white transition-all;
  min-width: 60px;
  min-height: 52px;
  padding: 6px 4px;
  flex: 1;
  max-width: 80px;
  gap: 2px;
}

@media (min-width: 640px) {
  .ios-nav-button {
    min-width: 72px;
    min-height: 64px;
    padding: 10px 8px;
    max-width: 90px;
  }
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
  font-size: 32px;
  font-weight: 800;
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

/* Sparkle particles for unlock */
.sparkle {
  position: absolute;
  width: var(--sparkle-size, 6px);
  height: var(--sparkle-size, 6px);
  background: radial-gradient(circle, rgba(255, 215, 0, 1) 0%, transparent 70%);
  border-radius: 50%;
  animation: sparkle-float 3s ease-in-out infinite;
  animation-delay: var(--sparkle-delay, 0s);
}

@keyframes sparkle-float {
  0%, 100% {
    opacity: 0;
    transform: scale(0) translateY(0);
  }
  50% {
    opacity: 1;
    transform: scale(1) translateY(-30px);
  }
}

/* Radial gradient background */
.bg-gradient-radial {
  background: radial-gradient(circle, var(--tw-gradient-from) 0%, var(--tw-gradient-via) 50%, var(--tw-gradient-to) 100%);
}

/* Slow pulse for glow effect */
.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.1); }
}

/* Ping slow for icon backdrop */
.animate-ping-slow {
  animation: ping-slow 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

@keyframes ping-slow {
  75%, 100% {
    transform: scale(1.5);
    opacity: 0;
  }
}

/* Shimmer text effect */
.animate-shimmer-text {
  background-size: 200% 100%;
  animation: shimmer-text 2s linear infinite;
}

@keyframes shimmer-text {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}
</style>
