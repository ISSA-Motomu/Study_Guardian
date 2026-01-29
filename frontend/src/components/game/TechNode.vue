<template>
  <div 
    class="tech-node absolute"
    :class="nodeClass"
    @click="$emit('click', node)"
  >
    <!-- Glow effect for unlocked -->
    <div 
      v-if="node.state === 'unlocked' && node.level > 0"
      class="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-400/30 to-purple-400/30 animate-pulse-slow"
    />
    
    <!-- Node content -->
    <div class="relative z-10 flex flex-col items-center">
      <!-- Icon -->
      <div 
        class="w-14 h-14 rounded-xl flex items-center justify-center text-2xl transition-transform"
        :class="iconBgClass"
      >
        <span :class="{ 'blur-sm': node.state === 'locked', 'blur-[2px]': node.state === 'hint' }">
          {{ node.state === 'locked' ? '🔒' : node.icon }}
        </span>
      </div>
      
      <!-- Name -->
      <p 
        class="mt-1 text-xs font-semibold text-center max-w-[80px] truncate"
        :class="textClass"
      >
        {{ node.state === 'locked' || node.state === 'hint' ? '???' : node.name }}
      </p>
      
      <!-- Level badge -->
      <div 
        v-if="node.level > 0"
        class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-indigo-500 text-white text-[10px] font-bold flex items-center justify-center shadow-lg"
      >
        {{ node.level }}
      </div>

      <!-- Progress ring for revealed nodes -->
      <svg 
        v-if="node.state === 'revealed' || node.state === 'hint'"
        class="absolute -inset-1 w-[calc(100%+8px)] h-[calc(100%+8px)]"
        viewBox="0 0 100 100"
      >
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="rgba(255,255,255,0.2)"
          stroke-width="3"
        />
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="url(#progress-gradient)"
          stroke-width="3"
          stroke-linecap="round"
          :stroke-dasharray="`${node.progressToUnlock * 2.83} 283`"
          transform="rotate(-90 50 50)"
          class="transition-all duration-500"
        />
        <defs>
          <linearGradient id="progress-gradient">
            <stop offset="0%" stop-color="#fbbf24" />
            <stop offset="100%" stop-color="#f59e0b" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  node: { type: Object, required: true }
})

defineEmits(['click'])

const nodeClass = computed(() => {
  const base = 'p-2 rounded-2xl transition-all duration-300 cursor-pointer'
  
  switch (props.node.state) {
    case 'unlocked':
      return props.node.level > 0
        ? `${base} bg-white/90 shadow-lg shadow-indigo-500/20 hover:scale-105`
        : `${base} bg-white/70 shadow-md hover:scale-105 hover:bg-white/90`
    case 'revealed':
      return `${base} bg-amber-100/50 shadow-md animate-pulse-subtle`
    case 'hint':
      return `${base} bg-gray-700/50 backdrop-blur-sm`
    default:
      return `${base} bg-gray-800/50 opacity-50`
  }
})

const iconBgClass = computed(() => {
  if (props.node.state === 'locked' || props.node.state === 'hint') {
    return 'bg-gray-700/50'
  }
  
  const tierColors = {
    1: 'bg-slate-100',
    2: 'bg-blue-100',
    3: 'bg-purple-100',
    4: 'bg-orange-100',
    5: 'bg-pink-100',
    6: 'bg-amber-100'
  }
  return tierColors[props.node.tier] || 'bg-gray-100'
})

const textClass = computed(() => {
  switch (props.node.state) {
    case 'unlocked':
      return 'text-gray-800'
    case 'revealed':
      return 'text-amber-700'
    default:
      return 'text-gray-400'
  }
})
</script>

<style scoped>
.tech-node {
  min-width: 80px;
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.animate-pulse-subtle {
  animation: pulse-subtle 2s ease-in-out infinite;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

@keyframes pulse-subtle {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}
</style>
