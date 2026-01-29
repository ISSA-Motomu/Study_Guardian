<template>
  <div 
    class="tech-node"
    :class="nodeClass"
    @click="$emit('select', node)"
  >
    <!-- Outer Glow Ring -->
    <div 
      v-if="node.state === 'unlocked' && node.level > 0"
      class="glow-ring"
      :class="glowClass"
    />

    <!-- Progress Ring (for locked/hint states) -->
    <svg 
      v-if="node.state !== 'unlocked'"
      class="progress-ring"
      viewBox="0 0 80 80"
    >
      <circle
        cx="40" cy="40" r="36"
        fill="none"
        stroke="rgba(255,255,255,0.1)"
        stroke-width="3"
      />
      <circle
        cx="40" cy="40" r="36"
        fill="none"
        :stroke="progressColor"
        stroke-width="3"
        stroke-linecap="round"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="circumference * (1 - node.progressToUnlock / 100)"
        class="progress-stroke"
      />
    </svg>

    <!-- Main Node Circle -->
    <div class="node-body" :class="bodyClass">
      <!-- Icon -->
      <span class="node-icon" :class="iconClass">
        {{ displayIcon }}
      </span>
    </div>

    <!-- Level Badge -->
    <div 
      v-if="node.state === 'unlocked' && node.level > 0"
      class="level-badge"
      :class="badgeClass"
    >
      {{ node.level }}
    </div>

    <!-- Name Label -->
    <div class="node-label">
      <span :class="labelClass">
        {{ displayName }}
      </span>
    </div>

    <!-- Unlock Indicator (for revealed) -->
    <div 
      v-if="node.state === 'revealed'"
      class="unlock-indicator"
    >
      🔓
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  node: { type: Object, required: true }
})

defineEmits(['select', 'buy'])

const circumference = 2 * Math.PI * 36

const nodeClass = computed(() => {
  const base = 'relative cursor-pointer transition-all duration-300'
  switch (props.node.state) {
    case 'unlocked':
      return `${base} hover:scale-110`
    case 'revealed':
      return `${base} hover:scale-105 animate-pulse-slow`
    case 'hint':
      return `${base} opacity-70`
    default:
      return `${base} opacity-40`
  }
})

const bodyClass = computed(() => {
  const base = 'relative w-16 h-16 rounded-full flex items-center justify-center transition-all'
  switch (props.node.state) {
    case 'unlocked':
      return props.node.level > 0 
        ? `${base} ${tierBgClass.value} shadow-lg` 
        : `${base} bg-slate-600 shadow-md`
    case 'revealed':
      return `${base} bg-amber-900/80 ring-2 ring-amber-400/50 shadow-lg`
    case 'hint':
      return `${base} bg-slate-800/80 backdrop-blur`
    default:
      return `${base} bg-slate-900/80`
  }
})

const tierBgClass = computed(() => {
  const tier = props.node.tier
  const classes = {
    1: 'bg-gradient-to-br from-slate-400 to-slate-600',
    2: 'bg-gradient-to-br from-blue-400 to-blue-600',
    3: 'bg-gradient-to-br from-purple-400 to-purple-600',
    4: 'bg-gradient-to-br from-orange-400 to-red-500',
    5: 'bg-gradient-to-br from-pink-400 to-purple-600',
    6: 'bg-gradient-to-br from-yellow-400 to-amber-500'
  }
  return classes[tier] || 'bg-gradient-to-br from-gray-400 to-gray-600'
})

const glowClass = computed(() => {
  const tier = props.node.tier
  const classes = {
    1: 'glow-slate',
    2: 'glow-blue',
    3: 'glow-purple',
    4: 'glow-orange',
    5: 'glow-pink',
    6: 'glow-gold'
  }
  return classes[tier] || 'glow-slate'
})

const badgeClass = computed(() => {
  const tier = props.node.tier
  const classes = {
    1: 'bg-slate-500',
    2: 'bg-blue-500',
    3: 'bg-purple-500',
    4: 'bg-orange-500',
    5: 'bg-pink-500',
    6: 'bg-amber-500'
  }
  return classes[tier] || 'bg-gray-500'
})

const iconClass = computed(() => {
  const base = 'text-2xl'
  switch (props.node.state) {
    case 'unlocked':
      return base
    case 'revealed':
      return `${base} animate-pulse`
    case 'hint':
      return `${base} filter blur-[2px] opacity-60`
    default:
      return `${base} filter blur-[3px] grayscale opacity-30`
  }
})

const labelClass = computed(() => {
  switch (props.node.state) {
    case 'unlocked':
      return 'text-white font-semibold'
    case 'revealed':
      return 'text-amber-300 font-semibold'
    default:
      return 'text-white/40'
  }
})

const progressColor = computed(() => {
  if (props.node.state === 'revealed') return '#fbbf24'
  if (props.node.state === 'hint') return '#64748b'
  return '#374151'
})

const displayIcon = computed(() => {
  if (props.node.state === 'locked') return '❓'
  return props.node.icon
})

const displayName = computed(() => {
  if (props.node.state === 'locked') return '???'
  if (props.node.state === 'hint') return '???'
  return props.node.name
})
</script>

<style scoped>
.tech-node {
  width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.glow-ring {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

.glow-slate { background: radial-gradient(circle, rgba(100,116,139,0.4) 0%, transparent 70%); }
.glow-blue { background: radial-gradient(circle, rgba(59,130,246,0.4) 0%, transparent 70%); }
.glow-purple { background: radial-gradient(circle, rgba(139,92,246,0.5) 0%, transparent 70%); }
.glow-orange { background: radial-gradient(circle, rgba(249,115,22,0.4) 0%, transparent 70%); }
.glow-pink { background: radial-gradient(circle, rgba(236,72,153,0.4) 0%, transparent 70%); }
.glow-gold { background: radial-gradient(circle, rgba(250,204,21,0.5) 0%, transparent 70%); }

@keyframes pulse-glow {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

.progress-ring {
  position: absolute;
  inset: 0;
  width: 80px;
  height: 80px;
  transform: rotate(-90deg);
}

.progress-stroke {
  transition: stroke-dashoffset 0.5s ease;
  filter: drop-shadow(0 0 4px currentColor);
}

.node-body {
  z-index: 1;
}

.node-icon {
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.level-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  color: white;
  z-index: 2;
  box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.node-label {
  margin-top: 8px;
  text-align: center;
  font-size: 11px;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-shadow: 0 1px 3px rgba(0,0,0,0.8);
}

.unlock-indicator {
  position: absolute;
  bottom: -24px;
  font-size: 14px;
  animation: bounce-unlock 1s ease-in-out infinite;
}

@keyframes bounce-unlock {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.animate-pulse-slow {
  animation: pulse-slow 2s ease-in-out infinite;
}

@keyframes pulse-slow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
