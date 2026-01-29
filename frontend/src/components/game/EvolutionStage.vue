<template>
  <div 
    class="evolution-stage relative"
    :class="{ 'active': isActive }"
  >
    <!-- Glow Ring -->
    <div 
      class="glow-ring"
      :class="stageGlowClass"
    />
    
    <!-- Main Visual Container -->
    <div class="stage-visual" :class="stageClass">
      <!-- Stage Icon/Emoji (fallback if no image) -->
      <div class="stage-icon">
        {{ currentStage.emoji }}
      </div>
      
      <!-- Stage Name -->
      <div class="stage-name">
        {{ currentStage.name }}
      </div>
      
      <!-- Orbiting Elements (for higher tiers) -->
      <div v-if="currentStage.tier >= 3" class="orbiting-elements">
        <div 
          v-for="i in orbitCount" 
          :key="i"
          class="orbit-item"
          :style="orbitStyle(i)"
        >
          {{ orbitEmoji }}
        </div>
      </div>
    </div>

    <!-- Tap Indicator -->
    <div class="tap-indicator">
      <span class="tap-text">タップ</span>
      <div class="tap-arrow">↓</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  totalKP: { type: Number, default: 0 },
  isActive: { type: Boolean, default: false }
})

// Evolution stages
const STAGES = [
  { 
    tier: 1, 
    minKP: 0, 
    name: '学習の始まり', 
    emoji: '🌍',
    description: '知識の種を蒔く'
  },
  { 
    tier: 2, 
    minKP: 5000, 
    name: '軌道上へ', 
    emoji: '🛰️',
    description: '視野が広がる'
  },
  { 
    tier: 3, 
    minKP: 50000, 
    name: '月への到達', 
    emoji: '🌙',
    description: '新たなフロンティア'
  },
  { 
    tier: 4, 
    minKP: 200000, 
    name: '火星開拓', 
    emoji: '🔴',
    description: '惑星間文明'
  },
  { 
    tier: 5, 
    minKP: 1000000, 
    name: '銀河進出', 
    emoji: '🌌',
    description: '星々の海へ'
  },
  { 
    tier: 6, 
    minKP: 10000000, 
    name: '技術的特異点', 
    emoji: '✨',
    description: '無限の知性'
  }
]

const currentStage = computed(() => {
  const kp = props.totalKP
  let stage = STAGES[0]
  for (const s of STAGES) {
    if (kp >= s.minKP) stage = s
  }
  return stage
})

const stageClass = computed(() => `stage-tier-${currentStage.value.tier}`)

const stageGlowClass = computed(() => {
  const tier = currentStage.value.tier
  const classes = {
    1: 'glow-blue',
    2: 'glow-cyan',
    3: 'glow-silver',
    4: 'glow-orange',
    5: 'glow-purple',
    6: 'glow-gold'
  }
  return classes[tier] || 'glow-blue'
})

const orbitCount = computed(() => {
  const tier = currentStage.value.tier
  if (tier < 3) return 0
  if (tier === 3) return 1
  if (tier === 4) return 2
  if (tier === 5) return 3
  return 5
})

const orbitEmoji = computed(() => {
  const tier = currentStage.value.tier
  const emojis = { 3: '🛰️', 4: '🚀', 5: '⭐', 6: '💫' }
  return emojis[tier] || '⭐'
})

const orbitStyle = (index) => {
  const angle = (360 / orbitCount.value) * index
  const duration = 10 + (index * 2)
  return {
    '--orbit-angle': `${angle}deg`,
    '--orbit-duration': `${duration}s`,
    animationDelay: `${index * -2}s`
  }
}
</script>

<style scoped>
.evolution-stage {
  width: 240px;
  height: 240px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.1s ease;
  -webkit-tap-highlight-color: transparent;
}

.evolution-stage.active {
  transform: scale(0.92);
}

.evolution-stage:active {
  transform: scale(0.92);
}

/* Glow Ring - Larger */
.glow-ring {
  position: absolute;
  inset: -30px;
  border-radius: 50%;
  opacity: 0.5;
  animation: pulse-glow 3s ease-in-out infinite;
}

.glow-blue { background: radial-gradient(circle, rgba(59,130,246,0.5) 0%, transparent 70%); }
.glow-cyan { background: radial-gradient(circle, rgba(34,211,238,0.5) 0%, transparent 70%); }
.glow-silver { background: radial-gradient(circle, rgba(203,213,225,0.6) 0%, transparent 70%); }
.glow-orange { background: radial-gradient(circle, rgba(249,115,22,0.5) 0%, transparent 70%); }
.glow-purple { background: radial-gradient(circle, rgba(168,85,247,0.5) 0%, transparent 70%); }
.glow-gold { background: radial-gradient(circle, rgba(250,204,21,0.6) 0%, transparent 70%); }

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.15); opacity: 0.9; }
}

/* Main Visual - Larger for iPhone */
.stage-visual {
  position: relative;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.5s ease;
}

.stage-tier-1 {
  background: radial-gradient(circle at 30% 30%, #4a90d9 0%, #1a4a7a 50%, #0d2840 100%);
  box-shadow: 
    inset -10px -10px 20px rgba(0,0,0,0.5),
    0 0 40px rgba(59,130,246,0.3);
}

.stage-tier-2 {
  background: radial-gradient(circle at 30% 30%, #60d4e8 0%, #2090a8 50%, #104858 100%);
  box-shadow: 
    inset -10px -10px 20px rgba(0,0,0,0.5),
    0 0 50px rgba(34,211,238,0.4);
}

.stage-tier-3 {
  background: radial-gradient(circle at 30% 30%, #e8e8e8 0%, #a0a0a0 50%, #505050 100%);
  box-shadow: 
    inset -10px -10px 20px rgba(0,0,0,0.3),
    0 0 50px rgba(203,213,225,0.5);
}

.stage-tier-4 {
  background: radial-gradient(circle at 30% 30%, #f87171 0%, #c53030 50%, #7a1a1a 100%);
  box-shadow: 
    inset -10px -10px 20px rgba(0,0,0,0.5),
    0 0 50px rgba(249,115,22,0.4);
}

.stage-tier-5 {
  background: radial-gradient(circle at 30% 30%, #c084fc 0%, #7c3aed 50%, #4c1d95 100%);
  box-shadow: 
    inset -10px -10px 20px rgba(0,0,0,0.5),
    0 0 60px rgba(168,85,247,0.5);
  animation: cosmic-pulse 4s ease-in-out infinite;
}

.stage-tier-6 {
  background: radial-gradient(circle, #fef08a 0%, #fbbf24 30%, #d97706 60%, #92400e 100%);
  box-shadow: 
    inset -10px -10px 20px rgba(0,0,0,0.3),
    0 0 80px rgba(250,204,21,0.6),
    0 0 120px rgba(245,158,11,0.3);
  animation: singularity-glow 2s ease-in-out infinite;
}

@keyframes cosmic-pulse {
  0%, 100% { filter: brightness(1) saturate(1); }
  50% { filter: brightness(1.2) saturate(1.1); }
}

@keyframes singularity-glow {
  0%, 100% { 
    transform: scale(1);
    filter: brightness(1); 
  }
  50% { 
    transform: scale(1.05);
    filter: brightness(1.3); 
  }
}

.stage-icon {
  font-size: 4.5rem;
  filter: drop-shadow(0 0 15px rgba(255,255,255,0.6));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.stage-name {
  position: absolute;
  bottom: -35px;
  white-space: nowrap;
  color: white;
  font-size: 1rem;
  font-weight: 700;
  text-shadow: 0 2px 12px rgba(0,0,0,0.9);
  letter-spacing: 0.025em;
}

/* Orbiting Elements - Larger radius */
.orbiting-elements {
  position: absolute;
  inset: -40px;
  animation: rotate-slow 30s linear infinite;
}

.orbit-item {
  position: absolute;
  top: 50%;
  left: 50%;
  font-size: 1.75rem;
  animation: orbit var(--orbit-duration) linear infinite;
  transform-origin: center;
}

@keyframes orbit {
  0% {
    transform: rotate(var(--orbit-angle)) translateX(110px) rotate(calc(var(--orbit-angle) * -1));
  }
  100% {
    transform: rotate(calc(var(--orbit-angle) + 360deg)) translateX(110px) rotate(calc((var(--orbit-angle) + 360deg) * -1));
  }
}

/* Tap Indicator - More visible */
.tap-indicator {
  position: absolute;
  bottom: -70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white/60;
  animation: tap-hint 2s ease-in-out infinite;
}

.tap-text {
  font-size: 0.875rem;
  color: rgba(255,255,255,0.6);
  font-weight: 500;
}

.tap-arrow {
  font-size: 1.25rem;
  color: rgba(255,255,255,0.5);
  animation: bounce-arrow 1s ease-in-out infinite;
}

@keyframes tap-hint {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes bounce-arrow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(8px); }
}
</style>
