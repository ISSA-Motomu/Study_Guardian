<template>
  <div 
    class="absolute pointer-events-none animate-fly-up font-bold text-xl"
    :class="isCrit ? 'text-yellow-400 scale-150' : 'text-white'"
    :style="{ left: x + 'px', top: y + 'px' }"
  >
    {{ isCrit ? '💥' : '' }}{{ Math.floor(value) }}
  </div>
</template>

<script setup>
defineProps({
  value: {
    type: Number,
    required: true
  },
  x: {
    type: Number,
    default: 0
  },
  y: {
    type: Number,
    default: 0
  },
  isCrit: {
    type: Boolean,
    default: false
  }
})
</script>
