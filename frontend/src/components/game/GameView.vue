<template>
  <div class="space-y-4 mt-8">
    <!-- Mode Tabs -->
    <div class="flex gap-2 p-1 bg-white/50 rounded-xl backdrop-blur-sm">
      <button
        @click="mode = 'evolution'"
        class="flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all"
        :class="mode === 'evolution' 
          ? 'bg-gradient-to-r from-indigo-500 to-purple-500 text-white shadow-lg' 
          : 'text-gray-500 hover:text-gray-700'"
      >
        🧬 進化
      </button>
      <button
        @click="mode = 'battle'"
        class="flex-1 py-2 px-4 rounded-lg font-semibold text-sm transition-all"
        :class="mode === 'battle' 
          ? 'bg-gradient-to-r from-red-500 to-orange-500 text-white shadow-lg' 
          : 'text-gray-500 hover:text-gray-700'"
      >
        ⚔️ バトル
      </button>
    </div>

    <!-- Evolution Mode -->
    <EvolutionView v-if="mode === 'evolution'" />

    <!-- Battle Mode (Original) -->
    <template v-else>
      <!-- Stage Info -->
      <GlassPanel class="text-center">
        <p class="text-sm text-gray-500">{{ gameStore.gameState.areaName }}</p>
        <p class="text-2xl font-bold text-indigo-700">
          Stage {{ gameStore.stageDisplay }}
        </p>
      </GlassPanel>

      <!-- Battle Area -->
      <div 
        class="relative bg-gradient-to-b from-slate-800 to-slate-900 rounded-2xl overflow-hidden min-h-[300px] flex items-center justify-center cursor-pointer"
        @click="gameStore.handleManualClick"
      >
        <!-- Enemy -->
        <EnemyDisplay 
          :name="gameStore.gameState.enemyName"
          :icon="gameStore.gameState.enemyIcon"
          :is-boss="gameStore.gameState.isBoss"
          :is-hit="gameStore.isHit"
        />

        <!-- Damage Effects -->
        <DamageEffect
          v-for="dmg in gameStore.dmgEffects"
          :key="dmg.id"
          :value="dmg.val"
          :x="dmg.x"
          :y="dmg.y"
          :is-crit="dmg.isCrit"
        />

        <!-- HP Bar -->
        <div class="absolute bottom-4 left-4 right-4">
          <div class="flex justify-between text-white text-sm mb-1">
            <span>{{ gameStore.gameState.enemyName }}</span>
            <span>{{ formatHp(gameStore.gameState.currentHp) }} / {{ formatHp(gameStore.gameState.maxHp) }}</span>
          </div>
          <div class="h-4 bg-gray-700 rounded-full overflow-hidden">
            <div 
              class="h-full transition-all duration-200"
              :class="gameStore.gameState.isBoss ? 'bg-gradient-to-r from-red-600 to-orange-500' : 'bg-gradient-to-r from-green-500 to-emerald-400'"
              :style="{ width: gameStore.hpPercentage + '%' }"
            />
          </div>
        </div>

        <!-- Tap hint -->
        <div class="absolute bottom-20 left-0 right-0 text-center">
          <p class="text-white/50 text-sm animate-pulse">タップで攻撃！</p>
        </div>
      </div>

      <!-- Player Stats -->
      <div class="grid grid-cols-2 gap-4">
        <GlassPanel class="text-center">
          <p class="text-xs text-gray-500">DPS</p>
          <p class="text-xl font-bold text-indigo-600">{{ gameStore.formatNumber(gameStore.gameState.dps) }}</p>
        </GlassPanel>
        <GlassPanel class="text-center">
          <p class="text-xs text-gray-500">タップダメージ</p>
          <p class="text-xl font-bold text-amber-500">{{ gameStore.formatNumber(gameStore.gameState.clickDamage) }}</p>
        </GlassPanel>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGameStore } from '@/stores/game'
import GlassPanel from '@/components/common/GlassPanel.vue'
import EnemyDisplay from './EnemyDisplay.vue'
import DamageEffect from './DamageEffect.vue'
import EvolutionView from './EvolutionView.vue'

const gameStore = useGameStore()
const mode = ref('evolution') // デフォルトは進化モード

const formatHp = (hp) => {
  return gameStore.formatNumber(hp)
}
</script>
