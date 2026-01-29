import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useSound } from '@/composables/useSound'

export const useGameStore = defineStore('game', () => {
  const { playSound } = useSound()

  // State
  const gameState = ref({
    stage: 1,
    areaName: '始まりの大地',
    currentHp: 100,
    maxHp: 100,
    enemyName: 'スライム',
    enemyIcon: '💧',
    isBoss: false,
    dps: 0,
    clickDamage: 1,
    lastTick: Date.now()
  })

  const dmgEffects = ref([])
  const isHit = ref(false)
  const battleInterval = ref(null)
  const dmgIdCounter = ref(0)

  // Computed
  const hpPercentage = computed(() => {
    return (gameState.value.currentHp / gameState.value.maxHp) * 100
  })

  const stageDisplay = computed(() => {
    const world = Math.floor((gameState.value.stage - 1) / 10) + 1
    const level = (gameState.value.stage - 1) % 10 + 1
    return `${world}-${level}`
  })

  // Enemy database for future expansion
  const enemies = [
    { name: 'スライム', icon: '💧', baseHp: 100 },
    { name: 'コウモリ', icon: '🦇', baseHp: 120 },
    { name: 'ゴブリン', icon: '👺', baseHp: 150 },
    { name: 'オオカミ', icon: '🐺', baseHp: 180 },
    { name: 'スケルトン', icon: '💀', baseHp: 220 },
    { name: 'オーク', icon: '👹', baseHp: 280 },
    { name: 'ゴーレム', icon: '🗿', baseHp: 350 },
    { name: 'ドラゴン', icon: '🐲', baseHp: 500 }
  ]

  const bosses = [
    { name: 'キングスライム', icon: '👑', hpMultiplier: 5 },
    { name: 'ヴァンパイアロード', icon: '🧛', hpMultiplier: 6 },
    { name: 'デーモンキング', icon: '👿', hpMultiplier: 8 },
    { name: '???', icon: '❓', hpMultiplier: 10 }
  ]

  // Actions
  const startBattleLoop = () => {
    if (battleInterval.value) clearInterval(battleInterval.value)
    battleInterval.value = setInterval(() => {
      if (gameState.value.dps > 0) {
        dealDamage(gameState.value.dps / 10) // 10 ticks per second
      }
    }, 100)
  }

  const handleManualClick = (e) => {
    const rect = e.target.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    dealDamage(gameState.value.clickDamage, true, x, y)
    playSound('click')
  }

  const dealDamage = (amount, isCrit = false, x = 0, y = 0) => {
    gameState.value.currentHp -= amount
    isHit.value = true
    setTimeout(() => isHit.value = false, 100)

    // Visual effect
    if (isCrit || Math.random() < 0.3) {
      const id = dmgIdCounter.value++
      const finalX = x || (window.innerWidth / 2) + (Math.random() * 100 - 50)
      const finalY = y || (window.innerHeight / 2 - 100)

      dmgEffects.value.push({ id, val: amount, x: finalX, y: finalY, isCrit })
      setTimeout(() => {
        dmgEffects.value = dmgEffects.value.filter(d => d.id !== id)
      }, 800)
    }

    if (gameState.value.currentHp <= 0) {
      enemyDefeated()
    }
  }

  const enemyDefeated = () => {
    playSound('levelup')
    gameState.value.stage++

    // Calculate next enemy
    const growthRate = 1.1
    const baseHp = 100
    const nextHp = Math.floor(baseHp * Math.pow(growthRate, gameState.value.stage))

    gameState.value.maxHp = nextHp
    gameState.value.currentHp = nextHp

    // Boss logic (every 10 stages)
    gameState.value.isBoss = (gameState.value.stage % 10 === 0)

    // Update enemy
    const enemyType = enemies[(gameState.value.stage - 1) % enemies.length]
    gameState.value.enemyName = gameState.value.isBoss ? '??? (BOSS)' : enemyType.name
    gameState.value.enemyIcon = gameState.value.isBoss ? '👿' : enemyType.icon

    // Boss HP multiplier
    if (gameState.value.isBoss) {
      gameState.value.maxHp *= 5
      gameState.value.currentHp = gameState.value.maxHp
    }
  }

  const applyStudyDamage = (minutes) => {
    if (!minutes || minutes <= 0) return

    const stageScaling = Math.pow(1.1, gameState.value.stage)
    const damage = Math.floor(minutes * 100 * stageScaling)

    setTimeout(() => {
      dealDamage(damage, true)
      alert(`勉強の成果！\n敵に ${formatNumber(damage)} のダメージを与えました！`)
    }, 500)
  }

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
    if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
    return Math.floor(num)
  }

  return {
    // State
    gameState,
    dmgEffects,
    isHit,
    // Computed
    hpPercentage,
    stageDisplay,
    // Actions
    startBattleLoop,
    handleManualClick,
    dealDamage,
    applyStudyDamage,
    formatNumber
  }
})
