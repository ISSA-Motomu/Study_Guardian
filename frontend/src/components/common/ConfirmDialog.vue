<template>
  <Teleport to="body">
    <Transition name="fade">
      <div 
        v-if="modelValue" 
        class="fixed inset-0 z-[100] flex items-center justify-center p-4"
        @click.self="cancel"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
        
        <!-- Dialog -->
        <Transition name="scale">
          <div 
            v-if="modelValue"
            class="relative w-full max-w-sm bg-gradient-to-b from-white to-gray-50 rounded-3xl shadow-2xl overflow-hidden"
          >
            <!-- Top decoration -->
            <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r" :class="typeGradient"></div>
            
            <!-- Icon -->
            <div class="pt-8 pb-4 flex justify-center">
              <div 
                class="w-20 h-20 rounded-full flex items-center justify-center text-4xl animate-bounce-slow"
                :class="iconBgClass"
              >
                {{ icon }}
              </div>
            </div>
            
            <!-- Title -->
            <h3 class="text-xl font-bold text-center text-gray-800 px-6">
              {{ title }}
            </h3>
            
            <!-- Message -->
            <p class="text-center text-gray-500 text-sm px-6 py-4 leading-relaxed">
              {{ message }}
            </p>
            
            <!-- Buttons -->
            <div class="px-6 pb-6 space-y-3">
              <!-- Confirm Button -->
              <button 
                @click="confirm"
                class="w-full py-4 rounded-2xl font-bold text-lg text-white shadow-lg transform active:scale-95 transition-all duration-200"
                :class="confirmButtonClass"
              >
                <span class="flex items-center justify-center gap-2">
                  <span>{{ confirmText }}</span>
                  <span v-if="confirmIcon">{{ confirmIcon }}</span>
                </span>
              </button>
              
              <!-- Cancel Button -->
              <button 
                @click="cancel"
                class="w-full py-4 rounded-2xl font-bold text-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transform active:scale-95 transition-all duration-200"
              >
                {{ cancelText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'info', // info, warning, danger, success
    validator: (v) => ['info', 'warning', 'danger', 'success'].includes(v)
  },
  title: {
    type: String,
    default: '確認'
  },
  message: {
    type: String,
    default: 'この操作を実行しますか？'
  },
  confirmText: {
    type: String,
    default: 'はい'
  },
  cancelText: {
    type: String,
    default: 'キャンセル'
  },
  icon: {
    type: String,
    default: ''
  },
  confirmIcon: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const typeConfig = computed(() => {
  const configs = {
    info: {
      gradient: 'from-blue-400 to-indigo-500',
      iconBg: 'bg-gradient-to-br from-blue-100 to-indigo-100',
      button: 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 shadow-blue-500/30',
      icon: '❓'
    },
    warning: {
      gradient: 'from-amber-400 to-orange-500',
      iconBg: 'bg-gradient-to-br from-amber-100 to-orange-100',
      button: 'bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 shadow-amber-500/30',
      icon: '⚠️'
    },
    danger: {
      gradient: 'from-red-400 to-pink-500',
      iconBg: 'bg-gradient-to-br from-red-100 to-pink-100',
      button: 'bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 shadow-red-500/30',
      icon: '🗑️'
    },
    success: {
      gradient: 'from-green-400 to-emerald-500',
      iconBg: 'bg-gradient-to-br from-green-100 to-emerald-100',
      button: 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 shadow-green-500/30',
      icon: '✅'
    }
  }
  return configs[props.type]
})

const typeGradient = computed(() => typeConfig.value.gradient)
const iconBgClass = computed(() => typeConfig.value.iconBg)
const confirmButtonClass = computed(() => typeConfig.value.button)
const icon = computed(() => props.icon || typeConfig.value.icon)

const confirm = () => {
  emit('confirm')
  emit('update:modelValue', false)
}

const cancel = () => {
  emit('cancel')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.scale-leave-active {
  transition: all 0.2s ease-in;
}

.scale-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(20px);
}

.scale-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.animate-bounce-slow {
  animation: bounce-slow 2s ease-in-out infinite;
}
</style>
