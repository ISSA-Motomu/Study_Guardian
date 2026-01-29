import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { useUserStore } from './user'

// 施設マスターデータ（宇宙開発テーマ）
const FACILITIES_MASTER = [
  // Tier 1: 基礎研究（0-500pt）
  {
    id: 'study_desk',
    name: '学習デスク',
    description: '全ての始まり。知識を蓄積する場所。',
    baseCost: 10,
    baseMultiplier: 0.1,
    unlockCondition: 0,
    tier: 1,
    icon: '📚'
  },
  {
    id: 'bookshelf',
    name: '本棚',
    description: '知識のストック。効率的な学習を支援。',
    baseCost: 50,
    baseMultiplier: 0.3,
    unlockCondition: 30,
    tier: 1,
    icon: '📖'
  },
  {
    id: 'pc_setup',
    name: 'PCセットアップ',
    description: 'デジタル時代の学習環境。',
    baseCost: 150,
    baseMultiplier: 0.8,
    unlockCondition: 100,
    tier: 1,
    icon: '💻'
  },
  // Tier 2: 研究施設（500-5000pt）
  {
    id: 'lab',
    name: '研究室',
    description: '本格的な実験と研究が可能に。',
    baseCost: 500,
    baseMultiplier: 2,
    unlockCondition: 300,
    tier: 2,
    icon: '🔬'
  },
  {
    id: 'library',
    name: '私設図書館',
    description: '膨大な知識のアーカイブ。',
    baseCost: 1500,
    baseMultiplier: 5,
    unlockCondition: 800,
    tier: 2,
    icon: '🏛️'
  },
  {
    id: 'ai_assistant',
    name: 'AI学習アシスタント',
    description: '人工知能が学習を最適化。',
    baseCost: 4000,
    baseMultiplier: 12,
    unlockCondition: 2000,
    tier: 2,
    icon: '🤖'
  },
  // Tier 3: 宇宙開発（5000-50000pt）
  {
    id: 'satellite',
    name: '観測衛星',
    description: '宇宙からの知見を地上に。',
    baseCost: 10000,
    baseMultiplier: 30,
    unlockCondition: 5000,
    tier: 3,
    icon: '🛰️'
  },
  {
    id: 'space_center',
    name: '宇宙センター',
    description: '九州から宇宙へ。JAXAとの共同研究。',
    baseCost: 30000,
    baseMultiplier: 80,
    unlockCondition: 15000,
    tier: 3,
    icon: '🚀'
  },
  {
    id: 'orbital_lab',
    name: '軌道研究ステーション',
    description: '無重力環境での最先端研究。',
    baseCost: 80000,
    baseMultiplier: 200,
    unlockCondition: 40000,
    tier: 3,
    icon: '🛸'
  },
  // Tier 4: 惑星開発（50000-500000pt）
  {
    id: 'moon_base',
    name: '月面基地',
    description: '人類初の恒久的な月面居住施設。',
    baseCost: 200000,
    baseMultiplier: 500,
    unlockCondition: 100000,
    tier: 4,
    icon: '🌙'
  },
  {
    id: 'mars_colony',
    name: '火星コロニー',
    description: '赤い惑星でのテラフォーミング開始。',
    baseCost: 600000,
    baseMultiplier: 1500,
    unlockCondition: 350000,
    tier: 4,
    icon: '🔴'
  },
  {
    id: 'asteroid_mining',
    name: '小惑星採掘基地',
    description: '宇宙資源の無限の可能性。',
    baseCost: 1500000,
    baseMultiplier: 4000,
    unlockCondition: 800000,
    tier: 4,
    icon: '☄️'
  },
  // Tier 5: 銀河進出（500000-5000000pt）
  {
    id: 'dyson_sphere',
    name: 'ダイソン球殻',
    description: '恒星エネルギーの完全利用。',
    baseCost: 5000000,
    baseMultiplier: 12000,
    unlockCondition: 2500000,
    tier: 5,
    icon: '☀️'
  },
  {
    id: 'warp_drive',
    name: 'ワープドライブ研究所',
    description: '光速を超える旅への第一歩。',
    baseCost: 15000000,
    baseMultiplier: 35000,
    unlockCondition: 8000000,
    tier: 5,
    icon: '🌀'
  },
  {
    id: 'galactic_council',
    name: '銀河評議会',
    description: '知的生命体との接触。新たな時代の幕開け。',
    baseCost: 50000000,
    baseMultiplier: 100000,
    unlockCondition: 25000000,
    tier: 5,
    icon: '👽'
  },
  // Tier 6: 特異点（最終段階）
  {
    id: 'singularity',
    name: '技術的特異点',
    description: '全てが一つに収束する。無限の知性の誕生。',
    baseCost: 200000000,
    baseMultiplier: 500000,
    unlockCondition: 100000000,
    tier: 6,
    icon: '✨'
  }
]

// Tier情報
const TIER_INFO = {
  1: { name: '基礎研究', color: 'from-slate-400 to-slate-600', bgColor: 'bg-slate-100' },
  2: { name: '研究施設', color: 'from-blue-400 to-blue-600', bgColor: 'bg-blue-50' },
  3: { name: '宇宙開発', color: 'from-purple-400 to-purple-600', bgColor: 'bg-purple-50' },
  4: { name: '惑星開発', color: 'from-orange-400 to-red-500', bgColor: 'bg-orange-50' },
  5: { name: '銀河進出', color: 'from-pink-400 to-purple-600', bgColor: 'bg-pink-50' },
  6: { name: '特異点', color: 'from-yellow-400 to-amber-500', bgColor: 'bg-amber-50' }
}

export const useEvolutionStore = defineStore('evolution', () => {
  const userStore = useUserStore()

  // ===== State =====
  /**
   * KP (Knowledge Points) - ゲーム内専用通貨
   * 
   * 【重要】XP（ショップ用通貨）とは完全に分離されています
   * - KP: 進化ゲーム内の施設購入・アップグレード専用
   * - XP: ショップでのアイテム購入専用（user.jsで管理）
   * 
   * ゲーム内の生産・消費はKPのみで完結します
   */
  const knowledgePoints = ref(0)        // 現在のKP残高
  const totalEarnedPoints = ref(0)       // 累計獲得KP（アンロック判定用）

  // 施設レベル
  const facilityLevels = ref({})

  // 最後の同期時刻
  const lastSyncTime = ref(null)
  const isDirty = ref(false) // 未保存の変更があるか

  // ===== Computed =====
  // 現在の倍率（全施設の合計）
  const totalMultiplier = computed(() => {
    let mult = 1.0
    for (const facility of FACILITIES_MASTER) {
      const level = facilityLevels.value[facility.id] || 0
      if (level > 0) {
        mult += facility.baseMultiplier * level
      }
    }
    return mult
  })

  // 施設リスト（状態付き）
  const facilitiesWithState = computed(() => {
    return FACILITIES_MASTER.map(facility => {
      const level = facilityLevels.value[facility.id] || 0
      const currentCost = calculateCost(facility.baseCost, level)
      const production = facility.baseMultiplier * (level || 1)

      // 状態判定
      let state = 'locked'
      if (totalEarnedPoints.value >= facility.unlockCondition) {
        state = 'unlocked'
      } else if (totalEarnedPoints.value >= facility.unlockCondition * 0.5) {
        state = 'revealed' // 50%到達で予兆表示
      } else if (totalEarnedPoints.value >= facility.unlockCondition * 0.2) {
        state = 'hint' // 20%到達でぼやけた表示
      }

      return {
        ...facility,
        level,
        currentCost,
        production,
        state,
        canAfford: knowledgePoints.value >= currentCost && state === 'unlocked',
        progressToUnlock: Math.min(100, (totalEarnedPoints.value / facility.unlockCondition) * 100)
      }
    })
  })

  // Tier別グループ化
  const facilitiesByTier = computed(() => {
    const grouped = {}
    for (const facility of facilitiesWithState.value) {
      if (!grouped[facility.tier]) {
        grouped[facility.tier] = {
          ...TIER_INFO[facility.tier],
          tier: facility.tier,
          facilities: []
        }
      }
      grouped[facility.tier].facilities.push(facility)
    }
    return Object.values(grouped).sort((a, b) => a.tier - b.tier)
  })

  // 次にアンロックされる施設
  const nextUnlock = computed(() => {
    return facilitiesWithState.value.find(f => f.state !== 'unlocked')
  })

  // 統計情報
  const stats = computed(() => {
    const totalOwned = Object.values(facilityLevels.value).reduce((a, b) => a + b, 0)
    const unlockedCount = facilitiesWithState.value.filter(f => f.state === 'unlocked').length
    return {
      totalOwned,
      unlockedCount,
      totalFacilities: FACILITIES_MASTER.length,
      multiplier: totalMultiplier.value
    }
  })

  // ===== Actions =====
  // コスト計算（指数関数的）
  function calculateCost(baseCost, level) {
    return Math.floor(baseCost * Math.pow(1.15, level))
  }

  // 施設購入
  function buyFacility(facilityId) {
    const facility = FACILITIES_MASTER.find(f => f.id === facilityId)
    if (!facility) return false

    const level = facilityLevels.value[facilityId] || 0
    const cost = calculateCost(facility.baseCost, level)

    if (knowledgePoints.value >= cost && totalEarnedPoints.value >= facility.unlockCondition) {
      knowledgePoints.value -= cost
      facilityLevels.value[facilityId] = level + 1
      isDirty.value = true
      saveToLocalStorage()
      return true
    }
    return false
  }

  // 勉強時間からポイント獲得
  function earnFromStudy(minutes) {
    if (minutes <= 0) return 0

    // 1分 = 基本1pt × 倍率
    const earned = Math.floor(minutes * totalMultiplier.value)
    knowledgePoints.value += earned
    totalEarnedPoints.value += earned
    isDirty.value = true
    saveToLocalStorage()
    return earned
  }

  // ローカルストレージ保存
  function saveToLocalStorage() {
    const userId = userStore.currentUserId || 'guest'
    const data = {
      knowledgePoints: knowledgePoints.value,
      totalEarnedPoints: totalEarnedPoints.value,
      facilityLevels: facilityLevels.value,
      lastSave: Date.now()
    }
    localStorage.setItem(`evolution_${userId}`, JSON.stringify(data))
  }

  // ローカルストレージ読み込み
  function loadFromLocalStorage() {
    const userId = userStore.currentUserId || 'guest'
    const saved = localStorage.getItem(`evolution_${userId}`)
    if (saved) {
      try {
        const data = JSON.parse(saved)
        knowledgePoints.value = data.knowledgePoints || 0
        totalEarnedPoints.value = data.totalEarnedPoints || 0
        facilityLevels.value = data.facilityLevels || {}
        return true
      } catch (e) {
        console.error('Failed to load evolution data:', e)
      }
    }
    return false
  }

  // サーバー同期（勉強終了時のみ呼び出し）
  async function syncToServer() {
    if (!isDirty.value) return

    const userId = userStore.currentUserId
    if (!userId) return

    try {
      const response = await fetch('/api/game/evolution/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          knowledge_points: knowledgePoints.value,
          total_earned: totalEarnedPoints.value,
          facility_levels: facilityLevels.value
        })
      })

      if (response.ok) {
        isDirty.value = false
        lastSyncTime.value = Date.now()
      }
    } catch (e) {
      console.error('Sync failed:', e)
    }
  }

  // サーバーから読み込み
  async function loadFromServer() {
    const userId = userStore.currentUserId
    if (!userId) return false

    try {
      const response = await fetch(`/api/game/evolution/${userId}`)
      if (!response.ok) return false

      const data = await response.json()
      if (data.status === 'ok' && data.data) {
        knowledgePoints.value = data.data.knowledge_points || 0
        totalEarnedPoints.value = data.data.total_earned || 0
        facilityLevels.value = data.data.facility_levels || {}
        saveToLocalStorage()
        return true
      }
    } catch (e) {
      console.error('Load from server failed:', e)
    }
    return false
  }

  // 初期化
  async function initialize() {
    // まずローカルから読み込み
    const localLoaded = loadFromLocalStorage()

    // サーバーと同期を試みる
    const serverLoaded = await loadFromServer()

    // サーバーデータがある場合はそちらを優先
    if (serverLoaded) {
      saveToLocalStorage()
    } else if (!localLoaded) {
      // 初回起動：初期ポイント付与
      knowledgePoints.value = 0
      totalEarnedPoints.value = 0
      facilityLevels.value = {}
    }
  }

  // デバッグ用：ポイント追加
  function debugAddPoints(amount) {
    knowledgePoints.value += amount
    totalEarnedPoints.value += amount
    isDirty.value = true
    saveToLocalStorage()
  }

  return {
    // State
    knowledgePoints,
    totalEarnedPoints,
    facilityLevels,
    lastSyncTime,
    isDirty,
    // Computed
    totalMultiplier,
    facilitiesWithState,
    facilitiesByTier,
    nextUnlock,
    stats,
    // Actions
    buyFacility,
    earnFromStudy,
    syncToServer,
    loadFromServer,
    initialize,
    saveToLocalStorage,
    debugAddPoints,
    // Constants
    TIER_INFO
  }
})
