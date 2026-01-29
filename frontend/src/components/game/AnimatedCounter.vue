<template>
  <span class="odometer" :class="{ 'text-glow': isGlowing }">
    {{ displayValue }}
  </span>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  duration: { type: Number, default: 500 }
})

const displayValue = ref('0')
const isGlowing = ref(false)
let animationFrame = null

const formatNumber = (num) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return Math.floor(num).toLocaleString()
}

const animateValue = (start, end, duration) => {
  if (animationFrame) cancelAnimationFrame(animationFrame)
  
  const startTime = performance.now()
  const diff = end - start
  
  // 増加時にグロー効果
  if (diff > 0) {
    isGlowing.value = true
    setTimeout(() => isGlowing.value = false, duration + 200)
  }
  
  const step = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // easeOutExpo for smooth ending
    const easeProgress = 1 - Math.pow(2, -10 * progress)
    const currentValue = start + diff * easeProgress
    
    displayValue.value = formatNumber(currentValue)
    
    if (progress < 1) {
      animationFrame = requestAnimationFrame(step)
    }
  }
  
  animationFrame = requestAnimationFrame(step)
}

let previousValue = 0

watch(() => props.value, (newVal, oldVal) => {
  const start = oldVal || previousValue || 0
  previousValue = newVal
  animateValue(start, newVal, props.duration)
}, { immediate: true })

onMounted(() => {
  displayValue.value = formatNumber(props.value)
})
</script>

<style scoped>
.odometer {
  font-variant-numeric: tabular-nums;
  transition: text-shadow 0.3s ease;
}

.text-glow {
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.8),
               0 0 20px rgba(255, 215, 0, 0.6),
               0 0 30px rgba(255, 215, 0, 0.4);
  animation: pulse-glow 0.5s ease-out;
}

@keyframes pulse-glow {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}
</style>
