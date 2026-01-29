<template>
  <div class="prestige-view min-h-screen pb-32 relative overflow-hidden">
    <!-- Animated Background -->
    <div class="fixed inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-b from-amber-950 via-orange-950 to-slate-900" />
      <div class="star-layer" />
      <!-- Glowing orb effect -->
      <div class="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-amber-500/20 rounded-full blur-3xl animate-pulse" />
    </div>

    <!-- Header -->
    <div class="sticky top-0 z-30 bg-amber-950/95 backdrop-blur-lg border-b border-amber-500/20 ios-safe-top">
      <div class="p-4 flex items-center gap-3">
        <button 
          @click="navigate('main')"
          class="w-12 h-12 rounded-2xl bg-white/15 flex items-center justify-center text-white active:bg-white/30 active:scale-95 transition-all text-lg"
        >
          ←
        </button>
        <div class="flex-1">
          <h1 class="text-xl font-bold text-white">🔄 転生</h1>
          <p class="text-xs text-amber-300 mt-0.5">新たな始まりへ</p>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="p-4">
      <!-- Current Progress -->
      <div class="bg-black/30 rounded-3xl p-6 mb-6 border border-amber-500/20">
        <div class="text-center mb-6">
          <div class="text-6xl mb-4">🌟</div>
          <h2 class="text-2xl font-bold text-white">転生レベル {{ evolutionStore.prestigeLevel }}</h2>
          <p class="text-amber-300 mt-2">現在の転生ボーナス: ×{{ evolutionStore.prestigeMultiplier.toFixed(2) }}</p>
        </div>

        <div class="grid grid-cols-2 gap-4 text-center">
          <div class="bg-white/10 rounded-2xl p-4">
            <p class="text-xs text-white/50 mb-1">累計獲得KP</p>
            <p class="text-xl font-bold text-yellow-300">{{ formatNumber(evolutionStore.totalEarnedPoints) }}</p>
          </div>
          <div class="bg-white/10 rounded-2xl p-4">
            <p class="text-xs text-white/50 mb-1">転生ポイント</p>
            <p class="text-xl font-bold text-amber-300">{{ evolutionStore.prestigePoints }}</p>
          </div>
        </div>
      </div>

      <!-- Prestige Preview -->
      <div class="bg-gradient-to-br from-amber-900/50 to-orange-900/50 rounded-3xl p-6 mb-6 border border-amber-400/30">
        <div class="text-center">
          <h3 class="text-lg font-bold text-white mb-4">転生すると...</h3>
          
          <div v-if="canPrestige" class="space-y-4">
            <div class="bg-black/30 rounded-2xl p-4">
              <p class="text-amber-200 text-sm mb-2">獲得できる転生ポイント</p>
              <p class="text-4xl font-bold text-amber-400 animate-pulse">
                +{{ evolutionStore.potentialPrestigePoints }}
              </p>
            </div>
            
            <div class="bg-black/30 rounded-2xl p-4">
              <p class="text-amber-200 text-sm mb-2">新しい転生ボーナス</p>
              <p class="text-2xl font-bold text-cyan-300">
                ×{{ calculateNewMultiplier.toFixed(2) }}
              </p>
              <p class="text-xs text-green-400 mt-1">
                (+{{ (calculateNewMultiplier - evolutionStore.prestigeMultiplier).toFixed(2) }})
              </p>
            </div>

            <div class="bg-red-900/30 rounded-2xl p-4 border border-red-500/30">
              <p class="text-red-300 text-sm">⚠️ リセットされるもの</p>
              <ul class="text-xs text-white/60 mt-2 space-y-1 text-left pl-4">
                <li>• 現在のKP（{{ formatNumber(evolutionStore.knowledgePoints) }}）</li>
                <li>• 全施設レベル</li>
                <li>• 購入済みアップグレード</li>
              </ul>
            </div>

            <div class="bg-green-900/30 rounded-2xl p-4 border border-green-500/30">
              <p class="text-green-300 text-sm">✅ 保持されるもの</p>
              <ul class="text-xs text-white/60 mt-2 space-y-1 text-left pl-4">
                <li>• 転生ポイント・ボーナス倍率</li>
                <li>• 獲得した実績</li>
                <li>• 生涯累計KP</li>
              </ul>
            </div>
          </div>

          <div v-else class="space-y-4">
            <div class="bg-black/30 rounded-2xl p-6">
              <p class="text-white/60 text-sm mb-4">転生には10億KP以上が必要です</p>
              <div class="relative h-4 bg-white/10 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-amber-500 to-orange-500 transition-all duration-500"
                  :style="{ width: prestigeProgress + '%' }"
                />
              </div>
              <p class="text-xs text-white/40 mt-2">
                {{ formatNumber(evolutionStore.totalEarnedPoints) }} / 1B
                ({{ prestigeProgress.toFixed(1) }}%)
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Achievements Preview -->
      <div class="bg-black/30 rounded-3xl p-6 border border-white/10">
        <h3 class="text-lg font-bold text-white mb-4">🏆 実績</h3>
        <div class="grid grid-cols-4 gap-3">
          <div 
            v-for="achievement in recentAchievements" 
            :key="achievement.id"
            class="achievement-badge"
            :class="{ 'unlocked': achievement.unlocked }"
            :title="achievement.name"
          >
            <span class="text-2xl">{{ achievement.icon }}</span>
          </div>
        </div>
        <p class="text-xs text-white/40 text-center mt-4">
          {{ unlockedAchievementCount }}/{{ totalAchievements }} 達成
        </p>
      </div>
    </div>

    <!-- Prestige Button -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-amber-950 via-amber-950/95 to-transparent ios-safe-bottom">
      <div class="max-w-md mx-auto space-y-3">
        <button 
          v-if="canPrestige"
          @click="showConfirmDialog = true; soundManager.play('click')"
          class="w-full py-5 bg-gradient-to-r from-amber-400 via-yellow-400 to-amber-400 text-black font-bold rounded-2xl text-xl shadow-2xl active:scale-95 transition-all animate-shimmer"
        >
          🔄 転生する (+{{ evolutionStore.potentialPrestigePoints }} pts)
        </button>
        <button 
          v-else
          disabled
          class="w-full py-5 bg-white/10 text-white/40 font-bold rounded-2xl text-lg"
        >
          🔒 転生条件未達成
        </button>
        
        <button 
          @click="navigate('main')"
          class="w-full py-4 bg-white/15 backdrop-blur-xl rounded-2xl text-white font-bold flex items-center justify-center gap-2 border border-white/20 active:bg-white/30 active:scale-95 transition-all"
        >
          <span class="text-xl">🌍</span>
          <span>メインに戻る</span>
        </button>
      </div>
    </div>

    <!-- Confirm Dialog -->
    <transition name="fade">
      <div 
        v-if="showConfirmDialog"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-6"
        @click.self="showConfirmDialog = false"
      >
        <div class="bg-gradient-to-br from-amber-900 to-orange-900 rounded-3xl p-6 max-w-sm w-full border border-amber-400/50 shadow-2xl">
          <div class="text-center">
            <div class="text-6xl mb-4">🔄</div>
            <h2 class="text-2xl font-bold text-white mb-2">転生しますか？</h2>
            <p class="text-amber-200 text-sm mb-6">
              全ての進行がリセットされ、<br/>
              <span class="text-amber-400 font-bold">+{{ evolutionStore.potentialPrestigePoints }} 転生ポイント</span>を獲得します
            </p>
            
            <div class="flex gap-3">
              <button 
                @click="showConfirmDialog = false"
                class="flex-1 py-4 bg-white/20 rounded-2xl text-white font-bold active:bg-white/30 transition-all"
              >
                キャンセル
              </button>
              <button 
                @click="doPrestige"
                class="flex-1 py-4 bg-gradient-to-r from-amber-400 to-orange-400 rounded-2xl text-black font-bold active:scale-95 transition-all"
              >
                転生する
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Success Animation -->
    <transition name="celebrate">
      <div 
        v-if="showSuccessAnimation"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
      >
        <div class="text-center">
          <div class="text-8xl mb-6 animate-bounce">✨</div>
          <h2 class="text-4xl font-bold text-amber-400 mb-4">転生完了！</h2>
          <p class="text-xl text-white">新たな旅が始まる...</p>
        </div>
        <!-- Particles -->
        <div class="absolute inset-0 pointer-events-none overflow-hidden">
          <div v-for="i in 30" :key="i" class="prestige-particle" :style="getParticleStyle(i)" />
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { soundManager } from '@/utils/sound'

const evolutionStore = useEvolutionStore()

const emit = defineEmits(['navigate'])
const navigate = (view) => {
  soundManager.play('click')
  emit('navigate', view)
}


const showConfirmDialog = ref(false)
const showSuccessAnimation = ref(false)

const canPrestige = computed(() => evolutionStore.potentialPrestigePoints > 0)

const prestigeProgress = computed(() => {
  const target = 1e9
  return Math.min(100, (evolutionStore.totalEarnedPoints / target) * 100)
})

const calculateNewMultiplier = computed(() => {
  const newPoints = evolutionStore.prestigePoints + evolutionStore.potentialPrestigePoints
  return 1 + Math.log10(newPoints + 1) * 0.5
})

const formatNumber = (num) => {
  return evolutionStore.formatNumber(num)
}

const recentAchievements = computed(() => {
  const achievements = evolutionStore.ACHIEVEMENTS_MASTER || []
  return achievements.slice(0, 8).map(a => ({
    ...a,
    unlocked: evolutionStore.unlockedAchievements?.includes(a.id)
  }))
})

const unlockedAchievementCount = computed(() => 
  evolutionStore.unlockedAchievements?.length || 0
)

const totalAchievements = computed(() => 
  evolutionStore.ACHIEVEMENTS_MASTER?.length || 0
)

const doPrestige = () => {
  showConfirmDialog.value = false
  showSuccessAnimation.value = true
  
  setTimeout(() => {
    evolutionStore.prestige()
    setTimeout(() => {
      showSuccessAnimation.value = false
      emit('navigate', 'main')
    }, 2000)
  }, 500)
}

const getParticleStyle = (i) => {
  const angle = (i / 30) * 360
  const distance = 100 + Math.random() * 200
  const size = 4 + Math.random() * 8
  const delay = Math.random() * 0.5
  const duration = 1 + Math.random() * 1
  
  return {
    '--angle': angle + 'deg',
    '--distance': distance + 'px',
    width: size + 'px',
    height: size + 'px',
    animationDelay: delay + 's',
    animationDuration: duration + 's'
  }
}
</script>

<style scoped>
.ios-safe-top {
  padding-top: max(env(safe-area-inset-top, 0px), 8px);
}

.ios-safe-bottom {
  padding-bottom: max(env(safe-area-inset-bottom, 0px), 16px);
}

.star-layer {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.4) 1px, transparent 0),
    radial-gradient(1.5px 1.5px at 40% 60%, rgba(255,255,255,0.3) 1px, transparent 0),
    radial-gradient(2px 2px at 70% 30%, rgba(255,255,255,0.5) 1px, transparent 0);
  animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

.achievement-badge {
  @apply w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center;
  @apply opacity-30 grayscale transition-all;
}

.achievement-badge.unlocked {
  @apply opacity-100 grayscale-0 bg-amber-900/50 border border-amber-500/30;
}

.animate-shimmer {
  background-size: 200% 100%;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.celebrate-enter-active {
  animation: celebrate-in 0.5s ease-out;
}
.celebrate-leave-active {
  animation: celebrate-out 0.5s ease-in;
}

@keyframes celebrate-in {
  from { opacity: 0; transform: scale(1.5); }
  to { opacity: 1; transform: scale(1); }
}

@keyframes celebrate-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

.prestige-particle {
  @apply absolute rounded-full bg-amber-400;
  left: 50%;
  top: 50%;
  animation: particle-burst 1.5s ease-out forwards;
}

@keyframes particle-burst {
  0% {
    transform: translate(-50%, -50%) rotate(var(--angle)) translateX(0);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) rotate(var(--angle)) translateX(var(--distance));
    opacity: 0;
  }
}
</style>
