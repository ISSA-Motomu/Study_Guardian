<template>
  <div class="upgrade-panel min-h-screen pb-32">
    <!-- Space Background -->
    <div class="fixed inset-0 -z-10">
      <div class="absolute inset-0 bg-gradient-to-b from-indigo-950 via-purple-950 to-slate-900" />
      <div class="star-layer" />
    </div>

    <!-- Header - iOS Safe Area -->
    <div class="sticky top-0 z-30 bg-indigo-950/95 backdrop-blur-lg border-b border-purple-500/20 ios-safe-top">
      <div class="p-4 flex items-center gap-3">
        <button 
          @click="navigate('main')"
          class="w-12 h-12 rounded-2xl bg-white/15 flex items-center justify-center text-white active:bg-white/30 active:scale-95 transition-all text-lg"
        >
          ←
        </button>
        <div class="flex-1">
          <h1 class="text-xl font-bold text-white">🔬 アップグレード</h1>
          <p class="text-xs text-purple-300 mt-0.5">研究効率を永続的に強化</p>
        </div>
        <!-- Current KP -->
        <div class="bg-white/15 rounded-2xl px-4 py-2.5 flex items-center gap-2 border border-purple-500/30">
          <span class="text-xl">💡</span>
          <span class="text-xl font-bold text-yellow-300 tabular-nums">{{ formatNumber(evolutionStore.knowledgePoints) }}</span>
        </div>
      </div>
    </div>

    <!-- Stats Bar -->
    <div class="px-4 py-3 bg-black/30">
      <div class="flex gap-3">
        <div class="flex-1 bg-white/10 rounded-xl p-3 text-center">
          <p class="text-[10px] text-white/50 uppercase">現在の倍率</p>
          <p class="text-xl font-bold text-cyan-300">×{{ evolutionStore.totalMultiplier.toFixed(2) }}</p>
        </div>
        <div class="flex-1 bg-white/10 rounded-xl p-3 text-center">
          <p class="text-[10px] text-white/50 uppercase">購入済み</p>
          <p class="text-xl font-bold text-purple-300">{{ purchasedCount }}/{{ totalUpgrades }}</p>
        </div>
      </div>
    </div>

    <!-- Upgrade List -->
    <div class="p-4 space-y-3">
      <div v-if="availableUpgrades.length === 0 && unlockedUpgrades.length === 0" class="text-center py-12">
        <div class="text-6xl mb-4">🔒</div>
        <p class="text-white/60">施設レベルを上げてアップグレードを解放しよう</p>
      </div>

      <!-- Available Upgrades -->
      <div v-for="upgrade in availableUpgrades" :key="upgrade.id" class="upgrade-card available">
        <div class="flex items-start gap-4">
          <div class="text-4xl">{{ upgrade.icon }}</div>
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-white text-lg">{{ upgrade.name }}</h3>
            <p class="text-sm text-white/60 mt-1">{{ upgrade.description }}</p>
            <div class="mt-3 flex items-center gap-2">
              <span class="text-yellow-300 font-bold">💡 {{ formatNumber(upgrade.cost) }}</span>
            </div>
          </div>
          <button 
            @click="buyUpgrade(upgrade.id)"
            :disabled="!upgrade.canAfford"
            class="buy-button"
            :class="{ 'can-afford': upgrade.canAfford }"
          >
            {{ upgrade.canAfford ? '購入' : '💡不足' }}
          </button>
        </div>
      </div>

      <!-- Purchased Upgrades -->
      <div v-if="purchasedUpgradesList.length > 0" class="mt-6">
        <h2 class="text-sm text-white/50 uppercase tracking-wider mb-3">✅ 購入済み</h2>
        <div v-for="upgrade in purchasedUpgradesList" :key="upgrade.id" class="upgrade-card purchased">
          <div class="flex items-center gap-4">
            <div class="text-3xl opacity-60">{{ upgrade.icon }}</div>
            <div class="flex-1">
              <h3 class="font-bold text-white/60">{{ upgrade.name }}</h3>
              <p class="text-xs text-white/40">{{ upgrade.description }}</p>
            </div>
            <div class="text-green-400 text-2xl">✓</div>
          </div>
        </div>
      </div>

      <!-- Locked Upgrades (Hints) -->
      <div v-if="lockedUpgrades.length > 0" class="mt-6">
        <h2 class="text-sm text-white/50 uppercase tracking-wider mb-3">🔒 未解放</h2>
        <div v-for="upgrade in lockedUpgrades" :key="upgrade.id" class="upgrade-card locked">
          <div class="flex items-center gap-4">
            <div class="text-3xl grayscale opacity-30">{{ upgrade.icon }}</div>
            <div class="flex-1">
              <h3 class="font-bold text-white/40">???</h3>
              <p class="text-xs text-white/30">{{ getUnlockHint(upgrade) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Navigation -->
    <div class="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-indigo-950 via-indigo-950/95 to-transparent ios-safe-bottom">
      <div class="flex gap-3 max-w-md mx-auto">
        <button 
          @click="$emit('navigate', 'main')"
          class="flex-1 py-4 bg-white/15 backdrop-blur-xl rounded-2xl text-white font-bold flex items-center justify-center gap-2 border border-white/20 active:bg-white/30 active:scale-95 transition-all"
        >
          <span class="text-xl">🌍</span>
          <span>メイン</span>
        </button>
        <button 
          @click="$emit('navigate', 'prestige')"
          class="flex-1 py-4 bg-gradient-to-r from-amber-500 to-orange-500 rounded-2xl text-black font-bold flex items-center justify-center gap-2 active:scale-95 transition-all"
        >
          <span class="text-xl">🔄</span>
          <span>転生</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useEvolutionStore } from '@/stores/evolution'
import { soundManager } from '@/utils/sound'

const evolutionStore = useEvolutionStore()

const emit = defineEmits(['navigate'])
const navigate = (view) => {
  soundManager.play('click')
  emit('navigate', view)
}


const availableUpgrades = computed(() => 
  evolutionStore.upgradesWithState.filter(u => u.unlocked && !u.purchased)
)

const purchasedUpgradesList = computed(() => 
  evolutionStore.upgradesWithState.filter(u => u.purchased)
)

const lockedUpgrades = computed(() => 
  evolutionStore.upgradesWithState.filter(u => !u.unlocked && !u.purchased)
)

const unlockedUpgrades = computed(() => 
  evolutionStore.upgradesWithState.filter(u => u.unlocked)
)

const purchasedCount = computed(() => 
  evolutionStore.purchasedUpgrades?.length || 0
)

const totalUpgrades = computed(() => 
  evolutionStore.UPGRADES_MASTER?.length || 0
)

const formatNumber = (num) => {
  return evolutionStore.formatNumber(num)
}

const buyUpgrade = (upgradeId) => {
  evolutionStore.buyUpgrade(upgradeId)
}

const getUnlockHint = (upgrade) => {
  if (upgrade.unlockCondition?.facility) {
    const facility = evolutionStore.facilitiesWithState.find(f => f.id === upgrade.unlockCondition.facility)
    return `${facility?.name || '???'} をLv.${upgrade.unlockCondition.level}にすると解放`
  }
  if (upgrade.unlockCondition?.totalKP) {
    return `累計 ${formatNumber(upgrade.unlockCondition.totalKP)} KPで解放`
  }
  return '条件を満たすと解放'
}
</script>

<style scoped>
.ios-safe-top {
  padding-top: max(env(safe-area-inset-top, 0px), 8px);
}

.ios-safe-bottom {
  padding-bottom: max(env(safe-area-inset-bottom, 0px), 16px);
}

.star-layer {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(1px 1px at 10% 20%, rgba(255,255,255,0.4) 1px, transparent 0),
    radial-gradient(1px 1px at 40% 60%, rgba(255,255,255,0.3) 1px, transparent 0),
    radial-gradient(1.5px 1.5px at 70% 30%, rgba(255,255,255,0.5) 1px, transparent 0),
    radial-gradient(1px 1px at 90% 80%, rgba(255,255,255,0.2) 1px, transparent 0);
  animation: twinkle 4s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.upgrade-card {
  @apply p-4 rounded-2xl border transition-all;
}

.upgrade-card.available {
  @apply bg-purple-900/50 border-purple-500/30;
}

.upgrade-card.purchased {
  @apply bg-green-900/20 border-green-500/20;
}

.upgrade-card.locked {
  @apply bg-white/5 border-white/10;
}

.buy-button {
  @apply px-5 py-3 rounded-xl font-bold text-sm transition-all whitespace-nowrap;
  @apply bg-white/10 text-white/50;
}

.buy-button.can-afford {
  @apply bg-gradient-to-r from-yellow-400 to-amber-500 text-black;
  @apply active:scale-95 shadow-lg;
}

.buy-button:disabled {
  @apply opacity-50 cursor-not-allowed;
}
</style>
