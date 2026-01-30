<template>
  <div class="space-y-4 mt-8">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-white">⚙️ 管理者メニュー</h2>
      <button
        @click="emit('exit')"
        class="text-white/70 hover:text-white"
      >
        ✕ 閉じる
      </button>
    </div>

    <!-- ローディング表示 -->
    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin text-4xl">⏳</div>
      <p class="text-white/70 mt-2">読み込み中...</p>
    </div>

    <!-- 承認待ち一覧（一番上に移動） -->
    <GlassPanel v-else>
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-gray-700">📋 承認待ち一覧</h3>
        <button
          @click="fetchPending"
          class="text-blue-500 text-sm hover:text-blue-700"
        >
          🔄 更新
        </button>
      </div>

      <div v-if="pendingItems.length === 0" class="text-gray-500 text-center py-4">
        承認待ちの項目はありません
      </div>
      
      <!-- タブ切り替え -->
      <div v-else>
        <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'px-3 py-1 rounded-full text-sm whitespace-nowrap transition-all',
              activeTab === tab.key 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            ]"
          >
            {{ tab.icon }} {{ tab.label }} ({{ countByType(tab.key) }})
          </button>
        </div>

        <!-- フィルタされた一覧 -->
        <div class="space-y-2 max-h-96 overflow-y-auto">
          <div 
            v-for="item in filteredItems" 
            :key="item.id"
            class="p-3 bg-gray-50 rounded-lg border border-gray-200"
          >
            <!-- ヘッダー -->
            <div class="flex justify-between items-start mb-2">
              <div class="flex items-center gap-2">
                <span class="text-lg">{{ getTypeIcon(item.type) }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="getTypeBadgeClass(item.type)">
                  {{ getTypeLabel(item.type) }}
                </span>
              </div>
              <span class="text-xs text-gray-400">{{ formatDate(item.date) }}</span>
            </div>
            
            <!-- コンテンツ -->
            <div class="mb-3">
              <p class="font-medium text-gray-800">{{ item.title }}</p>
              <p class="text-sm text-gray-500">👤 {{ item.userName || item.userId }}</p>
              <p v-if="item.detail" class="text-xs text-gray-400 mt-1">{{ item.detail }}</p>
              <p v-if="item.reward" class="text-sm text-yellow-600 mt-1">
                💰 報酬: {{ item.reward }} XP
              </p>
            </div>

            <!-- アクションボタン -->
            <div class="flex gap-2 justify-end">
              <button
                @click="approve(item)"
                :disabled="processing"
                class="bg-green-500 hover:bg-green-600 disabled:bg-gray-300 text-white px-4 py-1.5 rounded text-sm font-medium transition-colors"
              >
                ✅ 承認
              </button>
              <button
                @click="promptReject(item)"
                :disabled="processing"
                class="bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white px-4 py-1.5 rounded text-sm font-medium transition-colors"
              >
                ❌ 却下
              </button>
            </div>
          </div>
        </div>
      </div>
    </GlassPanel>

    <!-- 管理者アクション -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-3">⚡ 管理者アクション</h3>
      <div class="grid grid-cols-3 gap-2">
        <button
          @click="activeAction = 'job'"
          :class="['py-3 rounded-xl font-bold text-sm transition-colors', activeAction === 'job' ? 'bg-orange-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
        >
          🔧 ジョブ
        </button>
        <button
          @click="activeAction = 'point'"
          :class="['py-3 rounded-xl font-bold text-sm transition-colors', activeAction === 'point' ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
        >
          💰 ポイント
        </button>
        <button
          @click="activeAction = 'study'"
          :class="['py-3 rounded-xl font-bold text-sm transition-colors', activeAction === 'study' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300']"
        >
          📚 勉強記録
        </button>
      </div>
      
      <!-- ジョブ追加フォーム -->
      <div v-if="activeAction === 'job'" class="mt-4 space-y-3">
        <input
          v-model="newJob.title"
          type="text"
          placeholder="タスク名（例：風呂掃除）"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-orange-400 focus:outline-none"
        />
        <input
          v-model.number="newJob.reward"
          type="number"
          placeholder="報酬 XP（例：100）"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-orange-400 focus:outline-none"
        />
        <button
          @click="createJob"
          :disabled="!newJob.title || !newJob.reward || processing"
          class="w-full py-3 rounded-xl font-bold text-white bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          🔧 ジョブを追加
        </button>
      </div>
      
      <!-- ポイント付与フォーム -->
      <div v-if="activeAction === 'point'" class="mt-4 space-y-3">
        <select 
          v-model="pointGrant.userId"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-green-400 focus:outline-none"
        >
          <option value="">ユーザーを選択...</option>
          <option v-for="u in allUsers" :key="u.user_id" :value="u.user_id">
            {{ u.user_name }}
          </option>
        </select>
        <input
          v-model.number="pointGrant.amount"
          type="number"
          placeholder="付与ポイント（例：100）"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-green-400 focus:outline-none"
        />
        <button
          @click="grantPoints"
          :disabled="!pointGrant.userId || !pointGrant.amount || processing"
          class="w-full py-3 rounded-xl font-bold text-white bg-green-500 hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          💰 ポイントを付与
        </button>
      </div>
      
      <!-- 勉強記録追加フォーム -->
      <div v-if="activeAction === 'study'" class="mt-4 space-y-3">
        <select 
          v-model="manualStudy.userId"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-blue-400 focus:outline-none"
        >
          <option value="">ユーザーを選択...</option>
          <option v-for="u in allUsers" :key="u.user_id" :value="u.user_id">
            {{ u.user_name }}
          </option>
        </select>
        <select 
          v-model="manualStudy.subject"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-blue-400 focus:outline-none"
        >
          <option value="">科目を選択...</option>
          <option value="国語">国語</option>
          <option value="数学">数学</option>
          <option value="英語">英語</option>
          <option value="理科">理科</option>
          <option value="社会">社会</option>
          <option value="その他">その他</option>
        </select>
        <input
          v-model.number="manualStudy.minutes"
          type="number"
          placeholder="勉強時間（分）"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-blue-400 focus:outline-none"
        />
        <input
          v-model="manualStudy.comment"
          type="text"
          placeholder="コメント（任意）"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-blue-400 focus:outline-none"
        />
        <button
          @click="addManualStudy"
          :disabled="!manualStudy.userId || !manualStudy.subject || !manualStudy.minutes || processing"
          class="w-full py-3 rounded-xl font-bold text-white bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          📚 勉強記録を追加
        </button>
      </div>
    </GlassPanel>

    <!-- ユーザー視点切り替え -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-3">👁️ ユーザー視点で確認</h3>
      <p class="text-xs text-gray-500 mb-3">他のユーザーの画面を一時的に確認できます</p>
      
      <div v-if="loadingUsers" class="text-center py-4">
        <span class="text-gray-500">ユーザー読み込み中...</span>
      </div>
      
      <div v-else class="space-y-2">
        <select 
          v-model="selectedUserId"
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none"
        >
          <option value="">ユーザーを選択...</option>
          <option 
            v-for="u in allUsers" 
            :key="u.user_id" 
            :value="u.user_id"
          >
            {{ u.user_name }} {{ u.user_id === userStore.originalUserId ? '(あなた)' : '' }}
          </option>
        </select>
        
        <button
          @click="viewAsSelectedUser"
          :disabled="!selectedUserId || selectedUserId === userStore.currentUserId"
          class="w-full py-2 rounded-xl font-bold text-white bg-indigo-500 hover:bg-indigo-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          👁️ この視点で見る
        </button>
      </div>
    </GlassPanel>

    <!-- お知らせ送信 -->
    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-3">📢 お知らせを送信</h3>
      <p class="text-xs text-gray-500 mb-3">LINE通知を送信します</p>
      
      <div class="space-y-3">
        <!-- 通知先選択 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">通知先</label>
          <select 
            v-model="announcement.target"
            class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:outline-none"
          >
            <option value="all">👨‍👩‍👧‍👦 全員（ADMIN含む）</option>
            <option value="users">👦 USERのみ</option>
            <option value="individual">👤 個別ユーザー</option>
          </select>
        </div>
        
        <!-- 個別ユーザー選択（individualの場合） -->
        <div v-if="announcement.target === 'individual'">
          <label class="block text-sm font-medium text-gray-700 mb-1">送信先ユーザー</label>
          <select 
            v-model="announcement.targetUserId"
            class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:outline-none"
          >
            <option value="">ユーザーを選択...</option>
            <option v-for="u in allUsers" :key="u.user_id" :value="u.user_id">
              {{ u.user_name }}
            </option>
          </select>
        </div>
        
        <textarea
          v-model="announcement.message"
          rows="3"
          placeholder="お知らせ内容を入力..."
          class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-purple-400 focus:outline-none resize-none"
        />
        
        <button
          @click="sendAnnouncement"
          :disabled="!canSendAnnouncement || processing"
          class="w-full py-3 rounded-xl font-bold text-white bg-purple-500 hover:bg-purple-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          📢 {{ announcement.target === 'individual' ? '送信' : (announcement.target === 'users' ? 'USERに送信' : '全員に送信') }}
        </button>
      </div>
    </GlassPanel>

    <!-- 却下確認ダイアログ -->
    <div 
      v-if="showRejectConfirm"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      @click.self="showRejectConfirm = false"
    >
      <div class="bg-white rounded-2xl p-6 mx-4 max-w-sm w-full shadow-xl">
        <h3 class="text-lg font-bold text-gray-800 mb-3">⚠️ 却下の確認</h3>
        <p class="text-gray-600 mb-4">
          「{{ rejectTarget?.title }}」を本当に却下しますか？
        </p>
        <div class="flex gap-3">
          <button
            @click="showRejectConfirm = false"
            class="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300"
          >
            キャンセル
          </button>
          <button
            @click="confirmReject"
            :disabled="processing"
            class="flex-1 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 disabled:bg-gray-300"
          >
            却下する
          </button>
        </div>
      </div>
    </div>

    <!-- 処理結果メッセージ -->
    <div 
      v-if="message"
      :class="[
        'fixed bottom-4 left-1/2 transform -translate-x-1/2 px-4 py-2 rounded-lg shadow-lg transition-opacity',
        messageType === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      ]"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import GlassPanel from '@/components/common/GlassPanel.vue'
import { useConfirmDialog } from '@/composables/useConfirmDialog'

const emit = defineEmits(['exit', 'viewAsUser'])
const userStore = useUserStore()
const { showConfirm } = useConfirmDialog()

const loading = ref(true)
const processing = ref(false)
const pendingItems = ref([])
const activeTab = ref('all')
const message = ref('')
const messageType = ref('success')
const showRejectConfirm = ref(false)
const rejectTarget = ref(null)

// ユーザー視点切り替え用
const loadingUsers = ref(true)
const allUsers = ref([])
const selectedUserId = ref('')

// 管理者アクション用
const activeAction = ref(null)
const newJob = ref({ title: '', reward: 0 })
const pointGrant = ref({ userId: '', amount: 0 })
const manualStudy = ref({ userId: '', subject: '', minutes: 0, comment: '' })
const announcement = ref({ message: '', target: 'users', targetUserId: '' })

// お知らせ送信可能かどうか
const canSendAnnouncement = computed(() => {
  if (!announcement.value.message.trim()) return false
  if (announcement.value.target === 'individual' && !announcement.value.targetUserId) return false
  return true
})

const tabs = [
  { key: 'all', label: 'すべて', icon: '📋' },
  { key: 'study', label: '勉強', icon: '📚' },
  { key: 'job', label: 'お手伝い', icon: '🔧' },
  { key: 'shop', label: 'ショップ', icon: '🛒' },
  { key: 'mission', label: 'ミッション', icon: '🎯' }
]

const filteredItems = computed(() => {
  if (activeTab.value === 'all') return pendingItems.value
  return pendingItems.value.filter(item => item.type === activeTab.value)
})

const countByType = (type) => {
  if (type === 'all') return pendingItems.value.length
  return pendingItems.value.filter(item => item.type === type).length
}

const getTypeIcon = (type) => {
  const icons = { study: '📚', job: '🔧', shop: '🛒', mission: '🎯' }
  return icons[type] || '📋'
}

const getTypeLabel = (type) => {
  const labels = { study: '勉強', job: 'お手伝い', shop: 'ショップ', mission: 'ミッション' }
  return labels[type] || type
}

const getTypeBadgeClass = (type) => {
  const classes = {
    study: 'bg-blue-100 text-blue-700',
    job: 'bg-orange-100 text-orange-700',
    shop: 'bg-purple-100 text-purple-700',
    mission: 'bg-green-100 text-green-700'
  }
  return classes[type] || 'bg-gray-100 text-gray-700'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleString('ja-JP', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateStr
  }
}

const showMessage = (text, type = 'success') => {
  message.value = text
  messageType.value = type
  setTimeout(() => { message.value = '' }, 3000)
}

const fetchPending = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/admin/pending')
    const json = await res.json()
    
    if (json.status === 'ok' && json.data) {
      pendingItems.value = json.data.map(item => normalizeItem(item))
    } else {
      pendingItems.value = []
    }
  } catch (err) {
    console.error('Fetch pending error:', err)
    showMessage('データの取得に失敗しました', 'error')
  } finally {
    loading.value = false
  }
}

const normalizeItem = (item) => {
  // ApprovalServiceから返されるデータを正規化
  const data = item.data || item
  const type = item.type || 'unknown'
  
  let id, title, userId, userName, date, detail, reward
  
  switch (type) {
    case 'study':
      id = `study_${data.row_index}`
      title = `${data.subject || '勉強'} - ${data.minutes || 0}分`
      userId = data.user_id
      userName = data.user_name || data.user_id
      date = data.date
      detail = data.comment || ''
      reward = data.minutes || 0
      break
    
    case 'job':
      id = data.job_id
      title = data.title || 'お手伝い'
      userId = data.worker_id
      userName = data.worker_name || data.worker_id
      date = data.finished_at || data.created_at
      detail = data.comment || data.description || ''
      reward = data.reward || 0
      break
    
    case 'shop':
      id = data.request_id
      title = data.item_name || data.item_key || '商品'
      userId = data.user_id
      userName = data.user_name || data.user_id
      date = data.created_at
      detail = ''
      reward = data.cost || 0
      break
    
    case 'mission':
      id = data.mission_id
      title = data.title || 'ミッション'
      userId = data.user_id
      userName = data.user_name || data.user_id
      date = data.created_at
      detail = data.description || ''
      reward = data.reward || 0
      break
    
    default:
      id = `unknown_${Date.now()}`
      title = '不明な項目'
      userId = ''
      userName = ''
      date = ''
      detail = ''
      reward = 0
  }
  
  return {
    id,
    type,
    title,
    userId,
    userName,
    date,
    detail,
    reward,
    rawData: data  // 元データを保持
  }
}

const approve = async (item) => {
  if (processing.value) return
  processing.value = true
  
  try {
    let endpoint, body
    
    switch (item.type) {
      case 'study':
        endpoint = '/api/admin/approve/study'
        body = {
          row_index: item.rawData.row_index,
          user_id: item.userId,
          minutes: item.reward
        }
        break
      
      case 'job':
        endpoint = '/api/admin/approve/job'
        body = { job_id: item.rawData.job_id }
        break
      
      case 'shop':
        endpoint = '/api/admin/approve/shop'
        body = { request_id: item.rawData.request_id }
        break
      
      case 'mission':
        endpoint = '/api/admin/approve/mission'
        body = { mission_id: item.rawData.mission_id }
        break
      
      default:
        throw new Error('Unknown type')
    }
    
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    const json = await res.json()
    
    if (json.status === 'ok') {
      showMessage(`${item.title} を承認しました`, 'success')
      // リストから削除
      pendingItems.value = pendingItems.value.filter(i => i.id !== item.id)
    } else {
      showMessage(json.message || '承認に失敗しました', 'error')
    }
  } catch (err) {
    console.error('Approve error:', err)
    showMessage('承認処理でエラーが発生しました', 'error')
  } finally {
    processing.value = false
  }
}

// 却下ボタンが押されたら確認ダイアログを表示
const promptReject = (item) => {
  rejectTarget.value = item
  showRejectConfirm.value = true
}

// 確認後に実際に却下を実行
const confirmReject = async () => {
  if (!rejectTarget.value) return
  showRejectConfirm.value = false
  await reject(rejectTarget.value)
  rejectTarget.value = null
}

const reject = async (item) => {
  if (processing.value) return
  processing.value = true
  
  try {
    let endpoint, body
    
    switch (item.type) {
      case 'study':
        endpoint = '/api/admin/reject/study'
        body = {
          row_index: item.rawData.row_index,
          user_id: item.userId
        }
        break
      
      case 'job':
        endpoint = '/api/admin/reject/job'
        body = { job_id: item.rawData.job_id }
        break
      
      case 'shop':
        endpoint = '/api/admin/reject/shop'
        body = {
          request_id: item.rawData.request_id,
          user_id: item.userId,
          cost: item.reward  // 返金用
        }
        break
      
      case 'mission':
        endpoint = '/api/admin/reject/mission'
        body = { mission_id: item.rawData.mission_id }
        break
      
      default:
        throw new Error('Unknown type')
    }
    
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    
    const json = await res.json()
    
    if (json.status === 'ok') {
      showMessage(`${item.title} を却下しました`, 'success')
      // リストから削除
      pendingItems.value = pendingItems.value.filter(i => i.id !== item.id)
    } else {
      showMessage(json.message || '却下に失敗しました', 'error')
    }
  } catch (err) {
    console.error('Reject error:', err)
    showMessage('却下処理でエラーが発生しました', 'error')
  } finally {
    processing.value = false
  }
}

onMounted(() => {
  fetchPending()
  fetchAllUsers()
})

// ユーザー一覧を取得
const fetchAllUsers = async () => {
  loadingUsers.value = true
  try {
    const res = await fetch('/api/admin/users')
    const json = await res.json()
    if (json.status === 'success' && json.users) {
      allUsers.value = json.users
    }
  } catch (err) {
    console.error('Fetch users error:', err)
  } finally {
    loadingUsers.value = false
  }
}

// 選択したユーザー視点で見る
const viewAsSelectedUser = async () => {
  if (!selectedUserId.value) return
  
  const targetUser = allUsers.value.find(u => u.user_id === selectedUserId.value)
  const success = await userStore.viewAsUser(selectedUserId.value, targetUser?.user_name || '')
  
  if (success) {
    emit('viewAsUser')  // 親に通知して画面を切り替え
  }
}

// ジョブを追加
const createJob = async () => {
  if (processing.value || !newJob.value.title || !newJob.value.reward) return
  processing.value = true
  
  try {
    const res = await fetch('/api/admin/add_task', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: newJob.value.title,
        reward: newJob.value.reward
      })
    })
    const json = await res.json()
    
    if (json.status === 'success') {
      showMessage(`ジョブ「${newJob.value.title}」を追加しました`, 'success')
      newJob.value = { title: '', reward: 0 }
    } else {
      showMessage(json.message || 'ジョブの追加に失敗しました', 'error')
    }
  } catch (err) {
    console.error('Create job error:', err)
    showMessage('ジョブ追加でエラーが発生しました', 'error')
  } finally {
    processing.value = false
  }
}

// ポイントを付与
const grantPoints = async () => {
  if (processing.value || !pointGrant.value.userId || !pointGrant.value.amount) return
  processing.value = true
  
  try {
    const res = await fetch('/api/admin/grant_points', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: pointGrant.value.userId,
        amount: pointGrant.value.amount
      })
    })
    const json = await res.json()
    
    if (json.status === 'success') {
      const userName = allUsers.value.find(u => u.user_id === pointGrant.value.userId)?.user_name || 'ユーザー'
      showMessage(`${userName} に ${pointGrant.value.amount} XP を付与しました`, 'success')
      pointGrant.value = { userId: '', amount: 0 }
    } else {
      showMessage(json.message || 'ポイント付与に失敗しました', 'error')
    }
  } catch (err) {
    console.error('Grant points error:', err)
    showMessage('ポイント付与でエラーが発生しました', 'error')
  } finally {
    processing.value = false
  }
}

// 勉強記録を手動追加
const addManualStudy = async () => {
  if (processing.value || !manualStudy.value.userId || !manualStudy.value.subject || !manualStudy.value.minutes) return
  processing.value = true
  
  try {
    const res = await fetch('/api/admin/manual_study', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: manualStudy.value.userId,
        subject: manualStudy.value.subject,
        minutes: manualStudy.value.minutes,
        comment: manualStudy.value.comment || '管理者による手動記録'
      })
    })
    const json = await res.json()
    
    if (json.status === 'ok') {
      const userName = allUsers.value.find(u => u.user_id === manualStudy.value.userId)?.user_name || 'ユーザー'
      showMessage(`${userName} の勉強記録を追加しました（${manualStudy.value.minutes}分）`, 'success')
      manualStudy.value = { userId: '', subject: '', minutes: 0, comment: '' }
    } else {
      showMessage(json.message || '勉強記録の追加に失敗しました', 'error')
    }
  } catch (err) {
    console.error('Manual study error:', err)
    showMessage('勉強記録追加でエラーが発生しました', 'error')
  } finally {
    processing.value = false
  }
}

// お知らせを送信
const sendAnnouncement = async () => {
  if (processing.value || !canSendAnnouncement.value) return
  
  const targetLabel = announcement.value.target === 'all' ? '全員（ADMIN含む）' : 
                      announcement.value.target === 'users' ? 'USERのみ' : 
                      allUsers.value.find(u => u.user_id === announcement.value.targetUserId)?.user_name || '選択したユーザー'
  
  const confirmed = await showConfirm({
    type: 'info',
    title: 'お知らせ送信確認',
    message: `${targetLabel}にお知らせを送信しますか？\n\n「${announcement.value.message.trim().slice(0, 50)}${announcement.value.message.trim().length > 50 ? '...' : ''}」`,
    confirmText: '送信する',
    cancelText: 'キャンセル',
    icon: '📢'
  })
  if (!confirmed) return
  
  processing.value = true
  
  try {
    const res = await fetch('/api/admin/broadcast', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: announcement.value.message.trim(),
        target: announcement.value.target,
        target_user_id: announcement.value.targetUserId
      })
    })
    const json = await res.json()
    
    if (json.status === 'ok' || json.status === 'success') {
      showMessage(`お知らせを${json.sent_count || ''}人に送信しました`, 'success')
      announcement.value = { message: '', target: 'users', targetUserId: '' }
    } else {
      showMessage(json.message || 'お知らせ送信に失敗しました', 'error')
    }
  } catch (err) {
    console.error('Broadcast error:', err)
    showMessage('お知らせ送信でエラーが発生しました', 'error')
  } finally {
    processing.value = false
  }
}
</script>
