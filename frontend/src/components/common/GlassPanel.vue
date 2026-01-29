<template>
  <div 
    class="rounded-2xl p-4 shadow-lg backdrop-blur-lg"
    :class="[
      variant === 'glass' ? 'bg-white/70' : 'bg-white',
      customClass
    ]"
  >
    <slot />
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'glass' // 'glass' | 'solid'
  },
  customClass: {
    type: String,
    default: ''
  }
})
</script>
