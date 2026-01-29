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

    <!-- 承認待ち一覧 -->
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
import GlassPanel from '@/components/common/GlassPanel.vue'

const emit = defineEmits(['exit'])

const loading = ref(true)
const processing = ref(false)
const pendingItems = ref([])
const activeTab = ref('all')
const message = ref('')
const messageType = ref('success')
const showRejectConfirm = ref(false)
const rejectTarget = ref(null)

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
})
</script>
