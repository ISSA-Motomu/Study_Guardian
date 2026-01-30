<template>
  <div class="space-y-4 mt-8 pb-8">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-white">⚙️ その他</h2>
    </div>

    <!-- User Info Card -->
    <GlassPanel>
      <div class="flex items-center gap-4 mb-4">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center overflow-hidden">
          <img 
            v-if="userStore.user.avatar_url" 
            :src="userStore.user.avatar_url" 
            class="w-full h-full object-cover"
            alt="avatar"
          />
          <span v-else class="text-3xl">👤</span>
        </div>
        <div class="flex-1">
          <h3 class="font-bold text-lg text-gray-800">{{ userStore.user.name }}</h3>
          <p class="text-sm text-gray-500">
            Lv.{{ userStore.user.level }} · {{ userStore.user.rank_name }}
          </p>
          <p v-if="userStore.isGuestMode" class="text-xs text-orange-500 font-medium">
            ⚠️ ゲストモード
          </p>
        </div>
      </div>
    </GlassPanel>

    <!-- Menu List -->
    <GlassPanel>
      <div class="divide-y divide-gray-100">
        <!-- Settings Section -->
        <div class="py-3">
          <h4 class="text-xs text-gray-400 uppercase tracking-wide mb-2">設定</h4>
          <MenuItem 
            icon="🎨" 
            label="テーマの選択" 
            :description="currentThemeName"
            @click="showThemeModal = true"
          />
          <MenuItem 
            icon="🔔" 
            label="通知設定" 
            @click="openNotificationSettings"
          />
          <MenuItem 
            icon="🎵" 
            label="サウンド設定" 
            @click="openSoundSettings"
          />
        </div>

        <!-- Data Section -->
        <div class="py-3">
          <h4 class="text-xs text-gray-400 uppercase tracking-wide mb-2">データ</h4>
          <MenuItem 
            icon="📊" 
            label="学習統計" 
            description="詳細な学習分析"
            @click="showStudyStats = true"
          />
          <MenuItem 
            icon="🏆" 
            label="実績一覧" 
            description="獲得した実績"
            @click="showAchievements = true"
          />
        </div>

        <!-- Support Section -->
        <div class="py-3">
          <h4 class="text-xs text-gray-400 uppercase tracking-wide mb-2">サポート</h4>
          <MenuItem 
            icon="❓" 
            label="使い方ガイド" 
            @click="showGuide = true"
          />
          <MenuItem 
            icon="�" 
            label="ヘルプを書いてみよう" 
            description="アプリの使い方を共有"
            @click="showHelpEditor = true"
          />
          <MenuItem 
            icon="�📝" 
            label="フィードバック" 
            @click="openFeedback"
          />
          <MenuItem 
            icon="ℹ️" 
            label="アプリについて" 
            :description="`Version ${appVersion}`"
            @click="showAbout = true"
          />
        </div>

        <!-- Admin Section -->
        <div v-if="userStore.isAdmin" class="py-3">
          <h4 class="text-xs text-gray-400 uppercase tracking-wide mb-2">管理者</h4>
          <MenuItem 
            icon="🔧" 
            label="管理者メニュー" 
            description="承認・設定管理"
            @click="emit('admin')"
          />
        </div>
      </div>
    </GlassPanel>

    <!-- Debug Info (Dev only) -->
    <GlassPanel v-if="isDev" class="opacity-50">
      <h4 class="text-xs text-gray-400 mb-2">🔧 Debug Info</h4>
      <div class="text-xs text-gray-500 space-y-1">
        <p>User ID: {{ userStore.currentUserId }}</p>
        <p>Guest Mode: {{ userStore.isGuestMode }}</p>
        <p>Role: {{ userStore.user.role }}</p>
      </div>
    </GlassPanel>

    <!-- Guide Modal -->
    <Modal v-if="showGuide" @close="showGuide = false">
      <div class="p-6">
        <h3 class="text-xl font-bold mb-4">📖 使い方ガイド</h3>
        <div class="space-y-4 text-sm text-gray-600">
          <div>
            <h4 class="font-bold text-gray-800 mb-1">📖 勉強タブ</h4>
            <p>勉強を開始・記録します。科目を選んでタイマーをスタート！</p>
          </div>
          <div>
            <h4 class="font-bold text-gray-800 mb-1">⚔️ ゲームタブ</h4>
            <p>勉強で溜まったエネルギーでモンスターとバトル！進化ゲームも楽しめます。</p>
          </div>
          <div>
            <h4 class="font-bold text-gray-800 mb-1">📊 データタブ</h4>
            <p>学習記録やランキングを確認できます。</p>
          </div>
          <div>
            <h4 class="font-bold text-gray-800 mb-1">🛒 ショップ</h4>
            <p>勉強で稼いだEXPでご褒美アイテムと交換！</p>
          </div>
        </div>
      </div>
    </Modal>

    <!-- About Modal -->
    <Modal v-if="showAbout" @close="showAbout = false">
      <div class="p-6 text-center">
        <div class="text-6xl mb-4">📚</div>
        <h3 class="text-xl font-bold mb-2">Study Guardian</h3>
        <p class="text-gray-500 text-sm mb-4">Version {{ appVersion }}</p>
        <p class="text-sm text-gray-600 mb-4">
          学習習慣を楽しく身につける<br/>
          ゲーミフィケーション学習アプリ
        </p>
        <div class="text-xs text-gray-400">
          <p>© 2025-2026 ISSA Family</p>
          <p class="mt-1">Made with ❤️ for better studying</p>
        </div>
      </div>
    </Modal>

    <!-- Achievements Modal -->
    <Modal v-if="showAchievements" @close="showAchievements = false">
      <div class="p-6">
        <h3 class="text-xl font-bold mb-4">🏆 実績一覧</h3>
        <div v-if="achievements.length === 0" class="text-center py-8 text-gray-500">
          <span class="text-4xl block mb-2">🎯</span>
          <p>まだ実績がありません</p>
          <p class="text-sm">勉強を続けて実績を獲得しよう！</p>
        </div>
        <div v-else class="space-y-2">
          <div 
            v-for="achievement in achievements" 
            :key="achievement.id"
            class="flex items-center gap-3 p-3 bg-gradient-to-r from-yellow-50 to-amber-50 rounded-xl"
          >
            <span class="text-2xl">{{ achievement.icon || '🏅' }}</span>
            <div>
              <p class="font-bold text-gray-800">{{ achievement.name }}</p>
              <p class="text-xs text-gray-500">{{ achievement.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <!-- Study Stats Modal -->
    <Modal v-if="showStudyStats" @close="showStudyStats = false">
      <div class="p-6">
        <h3 class="text-xl font-bold mb-4">📊 学習統計</h3>
        <div class="space-y-4">
          <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4">
            <p class="text-sm text-gray-500">総学習時間</p>
            <p class="text-2xl font-bold text-indigo-600">
              {{ formatHours(userStore.user.total_hours || 0) }}
            </p>
          </div>
          <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4">
            <p class="text-sm text-gray-500">累計EXP</p>
            <p class="text-2xl font-bold text-green-600">
              {{ (userStore.user.xp || 0).toLocaleString() }} EXP
            </p>
          </div>
          <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4">
            <p class="text-sm text-gray-500">現在のレベル</p>
            <p class="text-2xl font-bold text-purple-600">
              Lv.{{ userStore.user.level }}
            </p>
          </div>
        </div>
      </div>
    </Modal>

    <!-- Theme Selection Modal -->
    <Modal v-if="showThemeModal" @close="showThemeModal = false">
      <div class="p-6">
        <h3 class="text-xl font-bold mb-4">🎨 テーマの選択</h3>
        <div class="space-y-2">
          <button
            v-for="theme in themes"
            :key="theme.id"
            @click="selectTheme(theme.id)"
            :class="[
              'w-full flex items-center gap-3 p-4 rounded-xl border-2 transition-all',
              currentTheme === theme.id 
                ? 'border-indigo-500 bg-indigo-50' 
                : 'border-gray-200 hover:border-gray-300'
            ]"
          >
            <div 
              class="w-10 h-10 rounded-lg flex items-center justify-center"
              :style="{ background: theme.preview }"
            >
              <span class="text-white text-lg">{{ theme.icon }}</span>
            </div>
            <div class="flex-1 text-left">
              <p class="font-bold text-gray-800">{{ theme.name }}</p>
              <p class="text-xs text-gray-500">{{ theme.description }}</p>
            </div>
            <span v-if="currentTheme === theme.id" class="text-indigo-500 text-xl">✓</span>
          </button>
        </div>
      </div>
    </Modal>

    <!-- Help Editor Modal -->
    <Modal v-if="showHelpEditor" @close="showHelpEditor = false">
      <div class="p-6">
        <h3 class="text-xl font-bold mb-4">📚 ヘルプを書いてみよう</h3>
        <p class="text-sm text-gray-500 mb-4">
          アプリの使い方や、便利な機能を他のユーザーに教えてあげよう！
        </p>
        <textarea
          v-model="helpText"
          placeholder="例: 勉強を始める前に科目を選ぶと、後から振り返りやすいよ！"
          class="w-full h-32 p-3 border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <div class="flex gap-2 mt-4">
          <button
            @click="showHelpEditor = false"
            class="flex-1 py-2 px-4 rounded-xl border border-gray-300 text-gray-600 hover:bg-gray-50"
          >
            キャンセル
          </button>
          <button
            @click="submitHelp"
            class="flex-1 py-2 px-4 rounded-xl bg-indigo-500 text-white hover:bg-indigo-600"
          >
            送信する
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useToastStore } from '@/stores/toast'
import GlassPanel from '@/components/common/GlassPanel.vue'
import Modal from '@/components/common/Modal.vue'

const emit = defineEmits(['admin'])

const userStore = useUserStore()
const toastStore = useToastStore()

// State
const showGuide = ref(false)
const showAbout = ref(false)
const showAchievements = ref(false)
const showStudyStats = ref(false)
const showThemeModal = ref(false)
const showHelpEditor = ref(false)
const achievements = ref([])
const currentTheme = ref(localStorage.getItem('sg_theme') || 'default')
const helpText = ref('')

// Constants
const appVersion = '1.0.0'
const isDev = import.meta.env.DEV

const themes = [
  { 
    id: 'default', 
    name: 'スタンダード', 
    description: '標準のカラーテーマ',
    icon: '☀️',
    preview: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  { 
    id: 'ocean', 
    name: 'オーシャン', 
    description: '爽やかな海のテーマ',
    icon: '🌊',
    preview: 'linear-gradient(135deg, #00c6fb 0%, #005bea 100%)'
  },
  { 
    id: 'forest', 
    name: 'フォレスト', 
    description: '自然を感じる緑のテーマ',
    icon: '🌲',
    preview: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)'
  },
  { 
    id: 'sunset', 
    name: 'サンセット', 
    description: '暖かみのある夕焼けテーマ',
    icon: '🌅',
    preview: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  },
  { 
    id: 'dark', 
    name: 'ダークモード', 
    description: '目に優しいダークテーマ',
    icon: '🌙',
    preview: 'linear-gradient(135deg, #232526 0%, #414345 100%)'
  }
]

// Computed
const currentThemeName = computed(() => {
  const theme = themes.find(t => t.id === currentTheme.value)
  return theme ? theme.name : 'スタンダード'
})

// Methods
const formatHours = (hours) => {
  if (hours < 1) {
    return `${Math.round(hours * 60)}分`
  }
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  return m > 0 ? `${h}時間${m}分` : `${h}時間`
}

const openNotificationSettings = () => {
  toastStore.info('通知設定は準備中です')
}

const openSoundSettings = () => {
  toastStore.info('サウンド設定は準備中です')
}

const openFeedback = () => {
  toastStore.info('フィードバック機能は準備中です')
}

const selectTheme = (themeId) => {
  currentTheme.value = themeId
  localStorage.setItem('sg_theme', themeId)
  toastStore.success(`テーマを「${currentThemeName.value}」に変更しました`)
  showThemeModal.value = false
  // TODO: 実際のテーマ変更処理を実装
}

const submitHelp = async () => {
  if (!helpText.value.trim()) {
    toastStore.warning('ヘルプ内容を入力してください')
    return
  }
  
  try {
    // ヘルプを送信（APIがあれば）
    toastStore.success('ヘルプを送信しました！ありがとう！ 🎉')
    helpText.value = ''
    showHelpEditor.value = false
  } catch (e) {
    toastStore.error('送信に失敗しました')
  }
}

// Fetch achievements on mount
onMounted(async () => {
  if (userStore.currentUserId) {
    try {
      const res = await fetch(`/api/user/${userStore.currentUserId}/achievements`)
      const data = await res.json()
      if (data.status === 'ok') {
        achievements.value = data.achievements || []
      }
    } catch (e) {
      console.warn('Failed to load achievements:', e)
    }
  }
})
</script>

<script>
// MenuItem Component (inline)
import { defineComponent } from 'vue'

const MenuItem = defineComponent({
  props: {
    icon: String,
    label: String,
    description: String
  },
  template: `
    <button 
      class="w-full flex items-center gap-3 py-3 px-2 hover:bg-gray-50 rounded-lg transition-colors text-left"
      @click="$emit('click')"
    >
      <span class="text-xl">{{ icon }}</span>
      <div class="flex-1">
        <p class="font-medium text-gray-800">{{ label }}</p>
        <p v-if="description" class="text-xs text-gray-500">{{ description }}</p>
      </div>
      <span class="text-gray-400">›</span>
    </button>
  `
})

export default {
  components: { MenuItem }
}
</script>
