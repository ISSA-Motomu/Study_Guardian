<template>
  <div 
    class="transition-transform"
    :class="{ 'animate-shake': isHit }"
  >
    <!-- Boss Badge -->
    <div 
      v-if="isBoss"
      class="absolute top-4 left-1/2 transform -translate-x-1/2 bg-red-600 text-white px-3 py-1 rounded-full text-xs font-bold animate-pulse"
    >
      👑 BOSS
    </div>

    <!-- Enemy Icon -->
    <div class="text-8xl filter drop-shadow-lg">
      {{ icon }}
    </div>

    <!-- Enemy Name -->
    <p class="mt-4 text-white font-bold text-lg">
      {{ name }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    required: true
  },
  isBoss: {
    type: Boolean,
    default: false
  },
  isHit: {
    type: Boolean,
    default: false
  }
})
</script>
