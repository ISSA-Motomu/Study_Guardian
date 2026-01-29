<template>
  <div class="circular-progress" :style="containerStyle">
    <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
      <!-- Background Circle -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        stroke="rgba(255,255,255,0.1)"
        :stroke-width="strokeWidth"
      />
      <!-- Progress Circle -->
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        fill="none"
        :stroke="color"
        :stroke-width="strokeWidth"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="offset"
        class="progress-ring transition-all duration-500"
        :style="{ transform: 'rotate(-90deg)', transformOrigin: 'center' }"
      />
    </svg>
    <!-- Center Text -->
    <div class="absolute inset-0 flex items-center justify-center">
      <span class="text-xs font-bold text-white">{{ Math.round(progress) }}%</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  progress: { type: Number, default: 0 },
  size: { type: Number, default: 40 },
  strokeWidth: { type: Number, default: 3 },
  color: { type: String, default: '#3b82f6' }
})

const radius = computed(() => (props.size - props.strokeWidth) / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)
const offset = computed(() => circumference.value * (1 - props.progress / 100))

const containerStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  position: 'relative'
}))
</script>

<style scoped>
.progress-ring {
  filter: drop-shadow(0 0 3px currentColor);
}
</style>
