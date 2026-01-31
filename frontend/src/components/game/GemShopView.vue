<template>
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-gradient-to-br from-purple-900 to-indigo-900 rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden border border-purple-400/30">
      <!-- Header -->
      <div class="bg-gradient-to-r from-purple-600 to-pink-600 p-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
          <span class="text-3xl">💎</span>
          <div>
            <h2 class="text-white font-bold text-lg">勉強石ショップ</h2>
            <p class="text-white/70 text-xs">勉強でしか手に入らない貴重な石</p>
          </div>
        </div>
        <button @click="emit('close')" class="text-white/80 hover:text-white text-xl p-2">✕</button>
      </div>
      
      <!-- Gem Balance -->
      <div class="bg-black/30 p-3 flex items-center justify-center gap-4 border-b border-purple-500/30">
        <div class="flex items-center gap-2">
          <span class="text-2xl animate-pulse">💎</span>
          <span class="text-2xl font-bold text-purple-200">{{ evolutionStore.studyGems }}</span>
          <span class="text-purple-300 text-sm">勉強石</span>
        </div>
        <div class="text-purple-400/60 text-xs">
          累計: {{ evolutionStore.totalStudyGems }}
        </div>
      </div>
      
      <!-- How to get gems -->
      <div class="bg-purple-800/30 p-2 text-center border-b border-purple-500/20">
        <p class="text-purple-200 text-xs">
          📖 勉強15分ごとに1個獲得 | 45分+で+1 | 60分+で+2
        </p>
      </div>
      
      <!-- Category Tabs -->
      <div class="flex border-b border-purple-500/30 bg-black/20">
        <button 
          v-for="cat in categories"
          :key="cat.id"
          @click="activeCategory = cat.id"
          :class="[
            'flex-1 py-2.5 text-xs font-medium transition-all',
            activeCategory === cat.id 
              ? 'text-white bg-purple-600/50 border-b-2 border-purple-300' 
              : 'text-purple-300 hover:text-white'
          ]"
        >
          {{ cat.icon }} {{ cat.name }}
        </button>
      </div>
      
      <!-- Items List -->
      <div class="p-3 overflow-y-auto" style="max-height: calc(90vh - 260px);">
        <div class="space-y-3">
          <div 
            v-for="item in filteredItems"
            :key="item.id"
            :class="[
              'p-3 rounded-xl border transition-all',
              item.isPurchased 
                ? 'bg-gray-800/50 border-gray-600/50 opacity-60' 
                : item.canBuy 
                  ? 'bg-purple-800/40 border-purple-400/50 hover:border-purple-300' 
                  : 'bg-gray-800/30 border-gray-600/30'
            ]"
          >
            <div class="flex items-start gap-3">
              <!-- Icon -->
              <div class="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500/30 to-pink-500/30 flex items-center justify-center text-2xl flex-shrink-0">
                {{ item.icon }}
              </div>
              
              <!-- Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <h4 class="font-bold text-white text-sm">{{ item.name }}</h4>
                  <span v-if="item.isPurchased" class="text-[10px] px-1.5 py-0.5 rounded bg-green-500/30 text-green-300">購入済</span>
                </div>
                <p class="text-purple-200/70 text-xs mt-0.5">{{ item.description }}</p>
                
                <!-- Requirements -->
                <p v-if="item.requires && !item.requiresMet" class="text-yellow-400 text-[10px] mt-1">
                  ⚠️ 前提: {{ getItemName(item.requires) }}
                </p>
              </div>
              
              <!-- Price & Buy -->
              <div class="text-right flex-shrink-0">
                <div class="flex items-center gap-1 justify-end mb-1">
                  <span class="text-lg">💎</span>
                  <span :class="['font-bold', item.canAfford ? 'text-purple-200' : 'text-red-400']">
                    {{ item.cost }}
                  </span>
                </div>
                <button 
                  v-if="!item.isPurchased"
                  @click="buyItem(item)"
                  :disabled="!item.canBuy"
                  :class="[
                    'px-3 py-1.5 rounded-lg text-xs font-bold transition-all',
                    item.canBuy 
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-400 hover:to-pink-400 active:scale-95' 
                      : 'bg-gray-600/50 text-gray-400 cursor-not-allowed'
                  ]"
                >
                  {{ item.canBuy ? '購入' : (item.canAfford ? '条件未達成' : '石不足') }}
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="filteredItems.length === 0" class="text-center py-8 text-purple-300/50">
            このカテゴリにアイテムはありません
          </div>
        </div>
      </div>
      
      <!-- Active Buffs Summary -->
      <div class="bg-black/40 p-3 border-t border-purple-500/30">
        <h4 class="text-purple-300 text-xs font-bold mb-2">有効なバフ</h4>
        <div class="flex flex-wrap gap-2">
          <span v-if="evolutionStore.permanentBuffs.productionBoost > 0" class="text-[10px] px-2 py-1 rounded-full bg-purple-600/40 text-purple-200">
            ⚡ 生産+{{ evolutionStore.permanentBuffs.productionBoost }}%
          </span>
          <span v-if="evolutionStore.permanentBuffs.offlineBoost > 0" class="text-[10px] px-2 py-1 rounded-full bg-blue-600/40 text-blue-200">
            🌙 オフライン+{{ evolutionStore.permanentBuffs.offlineBoost }}%
          </span>
          <span v-if="evolutionStore.permanentBuffs.studyMultiplier > 0" class="text-[10px] px-2 py-1 rounded-full bg-green-600/40 text-green-200">
            📖 勉強KP+{{ evolutionStore.permanentBuffs.studyMultiplier }}%
          </span>
          <span v-if="evolutionStore.permanentBuffs.criticalChance > 0" class="text-[10px] px-2 py-1 rounded-full bg-yellow-600/40 text-yellow-200">
            💡 クリ{{ evolutionStore.permanentBuffs.criticalChance }}%
          </span>
          <span v-if="evolutionStore.doubleGemActive" class="text-[10px] px-2 py-1 rounded-full bg-pink-600/40 text-pink-200 animate-pulse">
            💠 次回石2倍!
          </span>
          <span v-if="!hasAnyBuff" class="text-[10px] text-purple-400/50">
            バフはまだありません
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { useToastStore } from '@/stores/toast'

const emit = defineEmits(['close'])
const evolutionStore = useEvolutionStore()
const toast = useToastStore()

const activeCategory = ref('production')

const categories = [
  { id: 'production', name: '生産', icon: '⚡' },
  { id: 'offline', name: 'オフライン', icon: '🌙' },
  { id: 'study', name: '勉強', icon: '📖' },
  { id: 'special', name: '特殊', icon: '✨' },
  { id: 'consumable', name: '消耗品', icon: '🧪' }
]

const filteredItems = computed(() => {
  return evolutionStore.gemShopItems.filter(item => item.category === activeCategory.value)
})

const hasAnyBuff = computed(() => {
  const buffs = evolutionStore.permanentBuffs
  return buffs.productionBoost > 0 || buffs.offlineBoost > 0 || 
         buffs.studyMultiplier > 0 || buffs.criticalChance > 0 ||
         evolutionStore.doubleGemActive
})

const getItemName = (itemId) => {
  const item = evolutionStore.GEM_SHOP_ITEMS.find(i => i.id === itemId)
  return item ? item.name : itemId
}

const buyItem = (item) => {
  const result = evolutionStore.buyGemItem(item.id)
  if (result.success) {
    toast.success(`${item.name}を購入！\n${result.message}`)
  } else {
    toast.error(result.message)
  }
}
</script>
