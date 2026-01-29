<template>
  <div class="fixed inset-0 bg-black/30 backdrop-blur-sm z-50 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-white/30 border-t-white mx-auto" />
      <p class="mt-4 text-white font-medium">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: '読み込み中...'
  }
})
</script>
