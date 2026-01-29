<template>
  <div class="particle-system" ref="containerRef">
    <div
      v-for="particle in particles"
      :key="particle.id"
      class="kp-particle"
      :style="particle.style"
    >
      <span class="particle-inner">{{ particle.icon }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  icon: { type: String, default: '💡' }
})

const containerRef = ref(null)
const particles = ref([])
let particleId = 0

/**
 * パーティクルを発生させる（高度なバージョン）
 * @param {Object} options
 * @param {number} options.count - パーティクル数
 * @param {number} options.startX - 発生X座標
 * @param {number} options.startY - 発生Y座標
 * @param {number} options.targetX - ターゲットX座標
 * @param {number} options.targetY - ターゲットY座標
 */
const emit = (options = {}) => {
  const {
    count = 5,
    startX = null,
    startY = null,
    targetX = null,
    targetY = null
  } = options

  const container = containerRef.value
  if (!container) return

  const rect = container.getBoundingClientRect()
  const sX = startX ?? rect.width / 2
  const sY = startY ?? rect.height / 2
  const tX = targetX ?? rect.width / 2
  const tY = targetY ?? 0

  for (let i = 0; i < count; i++) {
    const id = particleId++
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5
    const distance = 40 + Math.random() * 60
    const delay = i * 40

    // 初期位置（発生点から少し散らばる）
    const initX = sX + (Math.random() - 0.5) * 30
    const initY = sY + (Math.random() - 0.5) * 30

    // 中間位置（噴水のように広がる）
    const midX = initX + Math.cos(angle) * distance
    const midY = initY + Math.sin(angle) * distance * 0.5 - 30 // 上方向に弧を描く

    // 最終位置（KPカウンターへ）
    const endX = tX
    const endY = tY

    const particle = {
      id,
      icon: props.icon,
      style: {
        left: `${initX}px`,
        top: `${initY}px`,
        '--mid-x': `${midX - initX}px`,
        '--mid-y': `${midY - initY}px`,
        '--end-x': `${endX - initX}px`,
        '--end-y': `${endY - initY}px`,
        '--delay': `${delay}ms`,
        '--scale-start': 0.5 + Math.random() * 0.3,
        '--rotation': `${Math.random() * 360}deg`
      }
    }

    particles.value.push(particle)

    // パーティクル削除（アニメーション完了後）
    setTimeout(() => {
      particles.value = particles.value.filter(p => p.id !== id)
    }, 1200 + delay)
  }
}

// 外部から呼び出せるようにexpose
defineExpose({ emit })
</script>

<style scoped>
.particle-system {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: visible;
  z-index: 100;
}

.kp-particle {
  position: absolute;
  font-size: 1.5rem;
  animation: 
    particle-fly 1s cubic-bezier(0.36, 0, 0.66, 1) forwards;
  animation-delay: var(--delay);
  opacity: 0;
  transform: scale(var(--scale-start)) rotate(var(--rotation));
}

.particle-inner {
  display: block;
  filter: 
    drop-shadow(0 0 8px rgba(255, 215, 0, 0.9))
    drop-shadow(0 0 15px rgba(255, 180, 0, 0.5));
  animation: particle-glow 0.3s ease-in-out infinite;
}

@keyframes particle-glow {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.3); }
}

@keyframes particle-fly {
  0% {
    opacity: 0;
    transform: translate(0, 0) scale(var(--scale-start));
  }
  15% {
    opacity: 1;
    transform: translate(0, -10px) scale(1);
  }
  40% {
    opacity: 1;
    transform: translate(var(--mid-x), var(--mid-y)) scale(1.1);
  }
  100% {
    opacity: 0;
    transform: translate(var(--end-x), var(--end-y)) scale(0.3);
  }
}
</style>
