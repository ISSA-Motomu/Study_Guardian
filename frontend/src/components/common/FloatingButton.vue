<template>
  <button
    @click="emit('click')"
    class="fixed bottom-24 right-6 w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-full shadow-xl flex items-center justify-center text-3xl z-30 transition-transform hover:scale-110 active:scale-95"
  >
    <span :class="inSession ? 'animate-pulse' : ''">
      {{ inSession ? '⏱️' : '▶️' }}
    </span>
  </button>
</template>

<script setup>
defineProps({
  inSession: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])
</script>
