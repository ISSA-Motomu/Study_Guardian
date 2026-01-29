<template>
  <div class="tech-tree-advanced min-h-screen">
    <!-- Space Background -->
    <div class="fixed inset-0 -z-10">
      <SpaceBackground :progress="evolutionStore.totalEarnedPoints" :parallaxOffset="parallaxOffset" />
    </div>

    <!-- Header -->
    <div class="sticky top-0 z-30 bg-black/80 backdrop-blur-lg border-b border-white/10">
      <div class="p-4 flex items-center gap-4">
        <button 
          @click="$emit('navigate', 'main')"
          class="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center text-white hover:bg-white/20 transition-all"
        >
          ←
        </button>
        <div class="flex-1">
          <h1 class="text-lg font-bold text-white">テックツリー</h1>
          <p class="text-xs text-white/60">ドラッグ＆ズームで探索</p>
        </div>
        <!-- Current KP -->
        <div class="bg-white/10 rounded-xl px-3 py-2 flex items-center gap-2">
          <span class="text-lg">💡</span>
          <AnimatedCounter 
            :value="evolutionStore.knowledgePoints"
            class="text-lg font-bold text-yellow-300"
          />
        </div>
      </div>
    </div>

    <!-- Tree Container -->
    <div 
      class="tree-viewport"
      ref="viewportRef"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
      @touchstart="startDrag"
      @touchmove="onDrag"
      @touchend="endDrag"
      @wheel.prevent="onWheel"
    >
      <!-- Tree Content -->
      <div 
        class="tree-world"
        :style="transformStyle"
      >
        <!-- SVG Connections -->
        <svg class="absolute inset-0 w-full h-full pointer-events-none" style="overflow: visible;">
          <defs>
            <!-- Gradient for unlocked connections -->
            <linearGradient id="gradient-unlocked" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#06b6d4" stop-opacity="0.8"/>
              <stop offset="50%" stop-color="#8b5cf6" stop-opacity="1"/>
              <stop offset="100%" stop-color="#ec4899" stop-opacity="0.8"/>
            </linearGradient>
            <!-- Gradient for locked connections -->
            <linearGradient id="gradient-locked" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#374151" stop-opacity="0.3"/>
              <stop offset="100%" stop-color="#1f2937" stop-opacity="0.5"/>
            </linearGradient>
            <!-- Glow filter -->
            <filter id="glow-filter" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <!-- Connection Lines -->
          <g v-for="conn in connections" :key="conn.id">
            <line
              :x1="conn.x1 + worldOffset.x"
              :y1="conn.y1 + worldOffset.y"
              :x2="conn.x2 + worldOffset.x"
              :y2="conn.y2 + worldOffset.y"
              :stroke="conn.unlocked ? 'url(#gradient-unlocked)' : 'url(#gradient-locked)'"
              stroke-width="3"
              :filter="conn.unlocked ? 'url(#glow-filter)' : ''"
              :class="{ 'animate-flow': conn.unlocked }"
            />
          </g>
        </svg>

        <!-- Nodes -->
        <TechNodeAdvanced
          v-for="node in nodesWithPositions"
          :key="node.id"
          :node="node"
          :style="getNodeStyle(node)"
          @select="selectNode"
          @buy="$emit('buy', node.id)"
        />
      </div>
    </div>

    <!-- Zoom Controls -->
    <div class="fixed bottom-24 right-4 flex flex-col gap-2 z-40">
      <button @click="zoomIn" class="zoom-btn">+</button>
      <button @click="zoomOut" class="zoom-btn">−</button>
      <button @click="resetView" class="zoom-btn text-sm">🎯</button>
    </div>

    <!-- Selected Node Panel -->
    <transition name="slide-up">
      <div 
        v-if="selectedNode"
        class="fixed bottom-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-xl rounded-t-3xl p-4 pb-8 shadow-2xl border-t border-white/10"
      >
        <div class="flex items-start gap-4">
          <!-- Icon -->
          <div 
            class="w-16 h-16 rounded-2xl flex items-center justify-center text-4xl"
            :class="getTierBgClass(selectedNode.tier)"
          >
            {{ selectedNode.icon }}
          </div>
          <!-- Info -->
          <div class="flex-1">
            <h3 class="text-xl font-bold text-white">
              {{ selectedNode.state === 'unlocked' || selectedNode.state === 'revealed' ? selectedNode.name : '???' }}
            </h3>
            <p class="text-sm text-white/60 mt-1">
              {{ selectedNode.state === 'unlocked' ? selectedNode.description : '施設の詳細は解放後に公開' }}
            </p>
            <div class="flex items-center gap-4 mt-3 text-sm">
              <span class="text-yellow-300">💡 {{ formatNumber(selectedNode.currentCost) }} KP</span>
              <span class="text-green-400">⚡ +{{ selectedNode.production.toFixed(1) }}/分</span>
              <span class="text-purple-300">Lv.{{ selectedNode.level }}</span>
            </div>
          </div>
          <!-- Close -->
          <button @click="selectedNode = null" class="p-2 text-white/40 hover:text-white">✕</button>
        </div>

        <!-- Action Button -->
        <button
          v-if="selectedNode.state === 'unlocked'"
          @click="handleBuyFromPanel"
          :disabled="!selectedNode.canAfford"
          class="w-full mt-4 py-4 rounded-xl font-bold text-lg transition-all"
          :class="selectedNode.canAfford 
            ? 'bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 text-white shadow-lg' 
            : 'bg-white/10 text-white/40'"
        >
          {{ selectedNode.level === 0 ? '🔓 解放する' : '⬆️ アップグレード' }}
        </button>
        <div 
          v-else 
          class="w-full mt-4 py-4 rounded-xl bg-white/5 text-center text-white/50"
        >
          🔒 {{ formatNumber(selectedNode.unlockCondition) }} KP で解放可能
          <div class="mt-2 h-2 bg-white/10 rounded-full overflow-hidden mx-8">
            <div 
              class="h-full bg-gradient-to-r from-amber-400 to-yellow-300"
              :style="{ width: selectedNode.progressToUnlock + '%' }"
            />
          </div>
        </div>
      </div>
    </transition>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black to-transparent z-30">
      <div class="flex gap-3 max-w-md mx-auto">
        <button 
          @click="$emit('navigate', 'main')"
          class="flex-1 py-3 bg-white/10 backdrop-blur rounded-xl text-white font-semibold flex items-center justify-center gap-2"
        >
          <span>🌍</span>
          <span>メイン</span>
        </button>
        <button 
          @click="$emit('navigate', 'list')"
          class="flex-1 py-3 bg-white/10 backdrop-blur rounded-xl text-white font-semibold flex items-center justify-center gap-2"
        >
          <span>📋</span>
          <span>施設</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import AnimatedCounter from './AnimatedCounter.vue'
import SpaceBackground from './SpaceBackground.vue'
import TechNodeAdvanced from './TechNodeAdvanced.vue'

const evolutionStore = useEvolutionStore()

const emit = defineEmits(['navigate', 'buy'])

// Viewport & Transform
const viewportRef = ref(null)
const scale = ref(0.7)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const selectedNode = ref(null)
const parallaxOffset = ref({ x: 0, y: 0 })

// World offset for centering
const worldOffset = computed(() => ({
  x: 200,
  y: 100
}))

const transformStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${scale.value})`,
  transformOrigin: 'top left'
}))

// Node positions
const nodesWithPositions = computed(() => {
  const centerX = 150
  const tierSpacing = 180
  const nodeSpacing = 140

  return evolutionStore.facilitiesWithState.map(facility => {
    const tierIndex = facility.tier - 1
    const sameTierItems = evolutionStore.facilitiesWithState.filter(f => f.tier === facility.tier)
    const indexInTier = sameTierItems.findIndex(f => f.id === facility.id)
    const tierCount = sameTierItems.length
    const xOffset = (indexInTier - (tierCount - 1) / 2) * nodeSpacing

    return {
      ...facility,
      x: centerX + xOffset,
      y: 80 + tierIndex * tierSpacing
    }
  })
})

const getNodeStyle = (node) => ({
  position: 'absolute',
  left: `${node.x + worldOffset.value.x}px`,
  top: `${node.y + worldOffset.value.y}px`,
  transform: 'translate(-50%, -50%)'
})

// Connections between nodes
const connections = computed(() => {
  const lines = []
  const tierGroups = {}

  nodesWithPositions.value.forEach(node => {
    if (!tierGroups[node.tier]) tierGroups[node.tier] = []
    tierGroups[node.tier].push(node)
  })

  const tiers = Object.keys(tierGroups).map(Number).sort((a, b) => a - b)

  for (let i = 0; i < tiers.length - 1; i++) {
    const currentTier = tierGroups[tiers[i]]
    const nextTier = tierGroups[tiers[i + 1]]

    currentTier.forEach(fromNode => {
      nextTier.forEach(toNode => {
        // Connect if within reasonable distance
        const xDiff = Math.abs(fromNode.x - toNode.x)
        if (xDiff < 200) {
          lines.push({
            id: `${fromNode.id}-${toNode.id}`,
            x1: fromNode.x,
            y1: fromNode.y,
            x2: toNode.x,
            y2: toNode.y,
            unlocked: fromNode.state === 'unlocked' && fromNode.level > 0
          })
        }
      })
    })
  }

  return lines
})

// Drag handlers
const startDrag = (e) => {
  if (e.target.closest('.tech-node')) return
  isDragging.value = true
  const point = e.touches ? e.touches[0] : e
  dragStart.value = {
    x: point.clientX - panX.value,
    y: point.clientY - panY.value
  }
}

const onDrag = (e) => {
  if (!isDragging.value) return
  const point = e.touches ? e.touches[0] : e
  panX.value = point.clientX - dragStart.value.x
  panY.value = point.clientY - dragStart.value.y
  
  // Update parallax
  parallaxOffset.value = {
    x: panX.value * 0.1,
    y: panY.value * 0.1
  }
}

const endDrag = () => {
  isDragging.value = false
}

const onWheel = (e) => {
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.max(0.3, Math.min(1.5, scale.value + delta))
}

const zoomIn = () => scale.value = Math.min(1.5, scale.value + 0.15)
const zoomOut = () => scale.value = Math.max(0.3, scale.value - 0.15)
const resetView = () => {
  scale.value = 0.7
  panX.value = 0
  panY.value = 50
}

const selectNode = (node) => {
  selectedNode.value = node
}

const handleBuyFromPanel = () => {
  if (selectedNode.value) {
    emit('buy', selectedNode.value.id)
    selectedNode.value = null
  }
}

const getTierBgClass = (tier) => {
  const classes = {
    1: 'bg-slate-700',
    2: 'bg-blue-700',
    3: 'bg-purple-700',
    4: 'bg-orange-700',
    5: 'bg-pink-700',
    6: 'bg-amber-600'
  }
  return classes[tier] || 'bg-slate-700'
}

const formatNumber = (num) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return Math.floor(num).toLocaleString()
}

onMounted(() => {
  panY.value = 50
})
</script>

<style scoped>
.tree-viewport {
  position: relative;
  width: 100%;
  height: calc(100vh - 180px);
  overflow: hidden;
  cursor: grab;
  touch-action: none;
}

.tree-viewport:active {
  cursor: grabbing;
}

.tree-world {
  position: absolute;
  width: 800px;
  height: 1200px;
  transition: transform 0.05s linear;
}

.zoom-btn {
  @apply w-12 h-12 bg-black/60 backdrop-blur-lg rounded-full flex items-center justify-center text-white text-xl font-bold border border-white/20 hover:bg-white/20 transition-all;
}

.animate-flow {
  stroke-dasharray: 8 4;
  animation: flow 1s linear infinite;
}

@keyframes flow {
  0% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -24; }
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
  opacity: 0;
}
</style>
