<template>
  <nav class="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white/80 backdrop-blur-lg rounded-full shadow-lg px-6 py-3 z-40 w-[90%] max-w-sm">
    <div class="flex justify-between items-center px-4">
      <button 
        v-for="item in navItems" 
        :key="item.id"
        @click="emit('update:modelValue', item.id)"
        :class="[
          'flex flex-col items-center transition-transform',
          modelValue === item.id ? 'text-indigo-600 scale-110' : 'text-gray-400'
        ]"
        :disabled="item.id !== 'study' && inSession"
      >
        <span class="text-xl">{{ item.icon }}</span>
        <span class="text-xs mt-1">{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  },
  inSession: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const navItems = [
  { id: 'data', icon: '📊', label: 'データ' },
  { id: 'study', icon: '📖', label: '勉強' },
  { id: 'game', icon: '⚔️', label: 'ゲーム' }
]
</script>
