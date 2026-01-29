<template>
  <div 
    class="tech-tree-container"
    ref="treeContainer"
    @mousedown="startDrag"
    @mousemove="onDrag"
    @mouseup="endDrag"
    @mouseleave="endDrag"
    @touchstart="startDrag"
    @touchmove="onDrag"
    @touchend="endDrag"
    @wheel="onWheel"
  >
    <!-- Background Grid -->
    <div class="absolute inset-0 bg-grid opacity-20" />
    
    <!-- SVG Lines connecting nodes -->
    <svg 
      class="absolute inset-0 w-full h-full pointer-events-none"
      :style="transformStyle"
    >
      <defs>
        <linearGradient id="line-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#6366f1;stop-opacity:0.3" />
          <stop offset="100%" style="stop-color:#a855f7;stop-opacity:0.8" />
        </linearGradient>
        <linearGradient id="line-locked" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#374151;stop-opacity:0.2" />
          <stop offset="100%" style="stop-color:#374151;stop-opacity:0.4" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
      
      <!-- Connection Lines -->
      <g v-for="connection in connections" :key="connection.id">
        <line
          :x1="connection.x1"
          :y1="connection.y1"
          :x2="connection.x2"
          :y2="connection.y2"
          :stroke="connection.unlocked ? 'url(#line-gradient)' : 'url(#line-locked)'"
          stroke-width="3"
          :filter="connection.unlocked ? 'url(#glow)' : ''"
          :class="{ 'animate-pulse-line': connection.justUnlocked }"
        />
      </g>
    </svg>

    <!-- Tree Nodes -->
    <div 
      class="tree-content"
      :style="transformStyle"
    >
      <TechNode
        v-for="node in nodesWithPositions"
        :key="node.id"
        :node="node"
        :style="{ 
          left: node.x + 'px', 
          top: node.y + 'px',
          transform: 'translate(-50%, -50%)'
        }"
        @buy="$emit('buy', node.id)"
        @click="selectNode(node)"
      />
    </div>

    <!-- Zoom Controls -->
    <div class="absolute bottom-4 right-4 flex flex-col gap-2 z-50">
      <button 
        @click="zoomIn"
        class="w-10 h-10 bg-white/80 backdrop-blur rounded-full shadow-lg flex items-center justify-center text-xl hover:bg-white transition-all"
      >
        +
      </button>
      <button 
        @click="zoomOut"
        class="w-10 h-10 bg-white/80 backdrop-blur rounded-full shadow-lg flex items-center justify-center text-xl hover:bg-white transition-all"
      >
        −
      </button>
      <button 
        @click="resetView"
        class="w-10 h-10 bg-white/80 backdrop-blur rounded-full shadow-lg flex items-center justify-center text-sm hover:bg-white transition-all"
      >
        🎯
      </button>
    </div>

    <!-- Selected Node Detail Panel -->
    <transition name="slide-up">
      <div 
        v-if="selectedNode"
        class="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-lg rounded-t-3xl p-4 shadow-2xl z-50"
      >
        <div class="flex items-start gap-4">
          <div 
            class="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
            :class="getTierBgClass(selectedNode.tier)"
          >
            {{ selectedNode.icon }}
          </div>
          <div class="flex-1">
            <h3 class="font-bold text-lg text-gray-800">{{ selectedNode.name }}</h3>
            <p class="text-sm text-gray-500 mt-1">{{ selectedNode.description }}</p>
            <div class="flex items-center gap-4 mt-2 text-sm">
              <span class="text-indigo-600">💡 {{ formatNumber(selectedNode.currentCost) }} KP</span>
              <span class="text-green-600">+{{ selectedNode.production.toFixed(1) }}/分</span>
              <span class="text-purple-600">Lv.{{ selectedNode.level }}</span>
            </div>
          </div>
          <button 
            @click="selectedNode = null"
            class="p-2 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        <button
          v-if="selectedNode.state === 'unlocked'"
          @click="$emit('buy', selectedNode.id); selectedNode = null"
          :disabled="!selectedNode.canAfford"
          class="w-full mt-4 py-3 rounded-xl font-bold transition-all"
          :class="selectedNode.canAfford 
            ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg' 
            : 'bg-gray-200 text-gray-400'"
        >
          {{ selectedNode.level === 0 ? '🔓 解放する' : '⬆️ アップグレード' }}
        </button>
        <div v-else class="w-full mt-4 py-3 rounded-xl bg-gray-100 text-center text-gray-500">
          🔒 {{ formatNumber(selectedNode.unlockCondition) }} KP で解放
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TechNode from './TechNode.vue'

const props = defineProps({
  facilities: { type: Array, required: true }
})

const emit = defineEmits(['buy'])

// Pan & Zoom state
const scale = ref(0.8)
const panX = ref(0)
const panY = ref(0)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const selectedNode = ref(null)
const treeContainer = ref(null)

// Transform style
const transformStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${scale.value})`,
  transformOrigin: 'center center'
}))

// Node positions (テックツリーレイアウト)
const nodesWithPositions = computed(() => {
  const centerX = 180
  const tierSpacing = 150
  const nodeSpacing = 120

  return props.facilities.map((facility, index) => {
    // Tierごとに縦に配置、同一Tier内は横に配置
    const tierIndex = facility.tier - 1
    const sameTimerItems = props.facilities.filter(f => f.tier === facility.tier)
    const indexInTier = sameTimerItems.findIndex(f => f.id === facility.id)
    const tierCount = sameTimerItems.length

    // 中央揃えのオフセット
    const xOffset = (indexInTier - (tierCount - 1) / 2) * nodeSpacing

    return {
      ...facility,
      x: centerX + xOffset,
      y: 80 + tierIndex * tierSpacing
    }
  })
})

// Connection lines between nodes
const connections = computed(() => {
  const lines = []
  const tierGroups = {}

  // Tierごとにグループ化
  nodesWithPositions.value.forEach(node => {
    if (!tierGroups[node.tier]) tierGroups[node.tier] = []
    tierGroups[node.tier].push(node)
  })

  // 隣接するTier間を接続
  const tiers = Object.keys(tierGroups).map(Number).sort((a, b) => a - b)
  
  for (let i = 0; i < tiers.length - 1; i++) {
    const currentTier = tierGroups[tiers[i]]
    const nextTier = tierGroups[tiers[i + 1]]

    // 各ノードから次のTierの中央ノードへ接続
    currentTier.forEach(fromNode => {
      const toNode = nextTier[Math.floor(nextTier.length / 2)]
      if (toNode) {
        lines.push({
          id: `${fromNode.id}-${toNode.id}`,
          x1: fromNode.x,
          y1: fromNode.y,
          x2: toNode.x,
          y2: toNode.y,
          unlocked: fromNode.state === 'unlocked' && fromNode.level > 0,
          justUnlocked: false
        })
      }
    })
  }

  return lines
})

// Drag handlers
const startDrag = (e) => {
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
}

const endDrag = () => {
  isDragging.value = false
}

// Zoom handlers
const onWheel = (e) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.max(0.3, Math.min(2, scale.value + delta))
}

const zoomIn = () => {
  scale.value = Math.min(2, scale.value + 0.2)
}

const zoomOut = () => {
  scale.value = Math.max(0.3, scale.value - 0.2)
}

const resetView = () => {
  scale.value = 0.8
  panX.value = 0
  panY.value = 0
}

const selectNode = (node) => {
  selectedNode.value = node
}

const getTierBgClass = (tier) => {
  const classes = {
    1: 'bg-slate-100',
    2: 'bg-blue-100',
    3: 'bg-purple-100',
    4: 'bg-orange-100',
    5: 'bg-pink-100',
    6: 'bg-amber-100'
  }
  return classes[tier] || 'bg-gray-100'
}

const formatNumber = (num) => {
  if (num >= 1000000000) return (num / 1000000000).toFixed(2) + 'B'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return Math.floor(num).toLocaleString()
}

// 初期位置調整
onMounted(() => {
  panY.value = 50
})
</script>

<style scoped>
.tech-tree-container {
  position: relative;
  width: 100%;
  height: 70vh;
  overflow: hidden;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
  border-radius: 1.5rem;
  touch-action: none;
  cursor: grab;
}

.tech-tree-container:active {
  cursor: grabbing;
}

.tree-content {
  position: absolute;
  width: 100%;
  height: 100%;
  transition: transform 0.1s ease-out;
}

.bg-grid {
  background-image: 
    linear-gradient(rgba(99, 102, 241, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
}

.animate-pulse-line {
  animation: pulse-line 1s ease-in-out infinite;
}

@keyframes pulse-line {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
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
