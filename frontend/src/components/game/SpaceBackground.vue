<template>
  <div class="space-background" :style="backgroundStyle">
    <!-- Star Layer 1 (Distant - Slow) -->
    <div 
      class="star-layer star-layer-1"
      :style="{ transform: `translate(${parallaxOffset.x * 0.1}px, ${parallaxOffset.y * 0.1}px)` }"
    />
    
    <!-- Star Layer 2 (Medium) -->
    <div 
      class="star-layer star-layer-2"
      :style="{ transform: `translate(${parallaxOffset.x * 0.3}px, ${parallaxOffset.y * 0.3}px)` }"
    />
    
    <!-- Star Layer 3 (Close - Fast) -->
    <div 
      class="star-layer star-layer-3"
      :style="{ transform: `translate(${parallaxOffset.x * 0.5}px, ${parallaxOffset.y * 0.5}px)` }"
    />

    <!-- Nebula Overlay -->
    <div 
      class="nebula-overlay"
      :class="nebulaClass"
      :style="{ transform: `translate(${parallaxOffset.x * 0.2}px, ${parallaxOffset.y * 0.2}px)` }"
    />

    <!-- Shooting Stars (Occasional) -->
    <div 
      v-for="star in shootingStars" 
      :key="star.id"
      class="shooting-star"
      :style="star.style"
    />

    <!-- Ambient Particles (Dust) -->
    <div class="ambient-particles">
      <div 
        v-for="i in 30" 
        :key="i"
        class="dust-particle"
        :style="dustStyle(i)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  progress: { type: Number, default: 0 },
  parallaxOffset: { 
    type: Object, 
    default: () => ({ x: 0, y: 0 }) 
  }
})

// Background changes based on progress
const backgroundStyle = computed(() => {
  const p = props.progress
  
  // Tier 1-2: Deep space (0 - 5,000)
  if (p < 5000) {
    return {
      background: 'radial-gradient(ellipse at bottom, #1B2838 0%, #0a0e17 50%, #000005 100%)'
    }
  }
  // Tier 3: Purple nebula (5,000 - 50,000)
  if (p < 50000) {
    return {
      background: 'radial-gradient(ellipse at bottom, #1a1a3e 0%, #0d0d24 50%, #050510 100%)'
    }
  }
  // Tier 4: Mars orange tint (50,000 - 500,000)
  if (p < 500000) {
    return {
      background: 'radial-gradient(ellipse at bottom, #2a1810 0%, #150a08 50%, #0a0505 100%)'
    }
  }
  // Tier 5-6: Cosmic (500,000+)
  return {
    background: 'radial-gradient(ellipse at bottom, #1a0a2e 0%, #0a0518 50%, #020108 100%)'
  }
})

const nebulaClass = computed(() => {
  const p = props.progress
  if (p < 5000) return 'nebula-blue'
  if (p < 50000) return 'nebula-purple'
  if (p < 500000) return 'nebula-orange'
  return 'nebula-cosmic'
})

// Shooting stars
const shootingStars = ref([])
let shootingStarId = 0
let shootingStarInterval = null

const createShootingStar = () => {
  const id = shootingStarId++
  const star = {
    id,
    style: {
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 50}%`,
      '--angle': `${-30 + Math.random() * 20}deg`,
      '--duration': `${0.5 + Math.random() * 0.5}s`,
      animationDelay: '0s'
    }
  }
  shootingStars.value.push(star)
  setTimeout(() => {
    shootingStars.value = shootingStars.value.filter(s => s.id !== id)
  }, 1500)
}

// Dust particles style
const dustStyle = (i) => ({
  '--delay': `${Math.random() * 20}s`,
  '--duration': `${15 + Math.random() * 15}s`,
  '--x-start': `${Math.random() * 100}%`,
  '--y-start': `${Math.random() * 100}%`,
  '--drift': `${(Math.random() - 0.5) * 100}px`,
  opacity: 0.2 + Math.random() * 0.3,
  width: `${1 + Math.random() * 2}px`,
  height: `${1 + Math.random() * 2}px`
})

onMounted(() => {
  // Occasional shooting stars
  shootingStarInterval = setInterval(() => {
    if (Math.random() > 0.7) {
      createShootingStar()
    }
  }, 3000)
})

onUnmounted(() => {
  clearInterval(shootingStarInterval)
})
</script>

<style scoped>
.space-background {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

/* Star Layers */
.star-layer {
  position: absolute;
  inset: -50%;
  background-repeat: repeat;
  transition: transform 0.3s ease-out;
}

.star-layer-1 {
  background-image: 
    radial-gradient(1px 1px at 20% 30%, white 100%, transparent),
    radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.8) 100%, transparent),
    radial-gradient(1px 1px at 60% 20%, rgba(255,255,255,0.6) 100%, transparent),
    radial-gradient(1px 1px at 80% 60%, white 100%, transparent);
  background-size: 200px 200px;
  opacity: 0.6;
  animation: twinkle-slow 8s ease-in-out infinite;
}

.star-layer-2 {
  background-image: 
    radial-gradient(1.5px 1.5px at 25% 25%, white 100%, transparent),
    radial-gradient(1.5px 1.5px at 75% 75%, rgba(200,220,255,0.9) 100%, transparent),
    radial-gradient(1px 1px at 50% 50%, rgba(255,220,200,0.8) 100%, transparent);
  background-size: 150px 150px;
  opacity: 0.7;
  animation: twinkle-medium 6s ease-in-out infinite 2s;
}

.star-layer-3 {
  background-image: 
    radial-gradient(2px 2px at 30% 40%, white 100%, transparent),
    radial-gradient(2px 2px at 70% 80%, rgba(150,200,255,1) 100%, transparent),
    radial-gradient(2.5px 2.5px at 90% 10%, rgba(255,200,150,1) 100%, transparent);
  background-size: 250px 250px;
  opacity: 0.8;
  animation: twinkle-fast 4s ease-in-out infinite 1s;
}

@keyframes twinkle-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.7; }
}

@keyframes twinkle-medium {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0.9; }
}

@keyframes twinkle-fast {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

/* Nebula Overlays */
.nebula-overlay {
  position: absolute;
  inset: 0;
  opacity: 0.4;
  mix-blend-mode: screen;
  transition: all 2s ease-out;
}

.nebula-blue {
  background: 
    radial-gradient(ellipse at 20% 80%, rgba(59, 130, 246, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(99, 102, 241, 0.2) 0%, transparent 40%);
}

.nebula-purple {
  background: 
    radial-gradient(ellipse at 30% 70%, rgba(139, 92, 246, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 30%, rgba(167, 139, 250, 0.3) 0%, transparent 40%),
    radial-gradient(ellipse at 50% 50%, rgba(192, 132, 252, 0.2) 0%, transparent 60%);
}

.nebula-orange {
  background: 
    radial-gradient(ellipse at 40% 60%, rgba(249, 115, 22, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 60% 40%, rgba(239, 68, 68, 0.2) 0%, transparent 40%);
}

.nebula-cosmic {
  background: 
    radial-gradient(ellipse at 25% 75%, rgba(236, 72, 153, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 75% 25%, rgba(139, 92, 246, 0.3) 0%, transparent 40%),
    radial-gradient(ellipse at 50% 50%, rgba(245, 158, 11, 0.2) 0%, transparent 60%);
  animation: nebula-shift 20s ease-in-out infinite;
}

@keyframes nebula-shift {
  0%, 100% { 
    opacity: 0.4;
    filter: hue-rotate(0deg);
  }
  50% { 
    opacity: 0.5;
    filter: hue-rotate(20deg);
  }
}

/* Shooting Stars */
.shooting-star {
  position: absolute;
  width: 100px;
  height: 2px;
  background: linear-gradient(90deg, white 0%, transparent 100%);
  border-radius: 50%;
  transform: rotate(var(--angle));
  animation: shoot var(--duration) linear forwards;
  filter: drop-shadow(0 0 6px white);
}

@keyframes shoot {
  0% {
    transform: rotate(var(--angle)) translateX(0);
    opacity: 1;
  }
  100% {
    transform: rotate(var(--angle)) translateX(300px);
    opacity: 0;
  }
}

/* Ambient Dust Particles */
.ambient-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.dust-particle {
  position: absolute;
  left: var(--x-start);
  top: var(--y-start);
  background: white;
  border-radius: 50%;
  animation: float-dust var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes float-dust {
  0%, 100% {
    transform: translate(0, 0);
    opacity: 0.3;
  }
  50% {
    transform: translate(var(--drift), calc(var(--drift) * -0.5));
    opacity: 0.6;
  }
}
</style>
