<template>
  <teleport to="body">
    <div class="fixed top-4 left-1/2 transform -translate-x-1/2 z-[100] flex flex-col gap-2 max-w-[90vw]">
      <transition-group name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'px-4 py-3 rounded-xl shadow-lg backdrop-blur-lg text-center transform transition-all duration-300',
            typeClasses[toast.type]
          ]"
          @click="dismiss(toast.id)"
        >
          <div class="flex items-center justify-center gap-2">
            <span class="text-lg">{{ typeIcons[toast.type] }}</span>
            <span class="text-sm font-medium whitespace-pre-line">{{ toast.message }}</span>
          </div>
        </div>
      </transition-group>
    </div>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.toasts)
const dismiss = toastStore.dismiss

const typeClasses = {
  success: 'bg-green-500/90 text-white',
  error: 'bg-red-500/90 text-white',
  warning: 'bg-amber-500/90 text-white',
  info: 'bg-blue-500/90 text-white'
}

const typeIcons = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️'
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
</style>
