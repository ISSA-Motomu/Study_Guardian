<template>
  <div class="particle-container" ref="containerRef">
    <div
      v-for="particle in particles"
      :key="particle.id"
      class="particle"
      :style="particle.style"
    >
      {{ particle.icon }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  icon: { type: String, default: '💡' },
  targetSelector: { type: String, default: '.kp-target' }
})

const containerRef = ref(null)
const particles = ref([])
let particleId = 0

// パーティクルを発生させる
const emit = (count = 5, startX = null, startY = null) => {
  const container = containerRef.value
  if (!container) return

  const rect = container.getBoundingClientRect()
  const centerX = startX ?? rect.width / 2
  const centerY = startY ?? rect.height / 2

  for (let i = 0; i < count; i++) {
    const id = particleId++
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5
    const distance = 30 + Math.random() * 50
    const delay = i * 50

    // 初期位置（中央から放射状に広がる）
    const startPosX = centerX + Math.cos(angle) * 20
    const startPosY = centerY + Math.sin(angle) * 20

    // 中間位置（広がる）
    const midX = centerX + Math.cos(angle) * distance
    const midY = centerY + Math.sin(angle) * distance

    // 最終位置（上部のKPバーに向かう）
    const endX = rect.width / 2
    const endY = -50

    const particle = {
      id,
      icon: props.icon,
      style: {
        left: `${startPosX}px`,
        top: `${startPosY}px`,
        '--mid-x': `${midX - startPosX}px`,
        '--mid-y': `${midY - startPosY}px`,
        '--end-x': `${endX - startPosX}px`,
        '--end-y': `${endY - startPosY}px`,
        animationDelay: `${delay}ms`
      }
    }

    particles.value.push(particle)

    // パーティクル削除
    setTimeout(() => {
      particles.value = particles.value.filter(p => p.id !== id)
    }, 1500 + delay)
  }
}

// 外部から呼び出せるようにexpose
defineExpose({ emit })
</script>

<style scoped>
.particle-container {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: visible;
  z-index: 100;
}

.particle {
  position: absolute;
  font-size: 1.5rem;
  animation: float-to-target 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards;
  opacity: 0;
  filter: drop-shadow(0 0 8px rgba(255, 215, 0, 0.8));
}

@keyframes float-to-target {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(0.5);
  }
  20% {
    opacity: 1;
    transform: translate(var(--mid-x), var(--mid-y)) scale(1.2);
  }
  100% {
    opacity: 0;
    transform: translate(var(--end-x), var(--end-y)) scale(0.3);
  }
}
</style>
