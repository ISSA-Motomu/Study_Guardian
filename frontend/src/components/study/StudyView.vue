<template>
  <div class="space-y-6">
    <!-- User Profile Card -->
    <GlassPanel class="text-center">
      <div class="flex items-center gap-4">
        <img 
          :src="userStore.user.avatar_url || defaultAvatar"
          class="w-16 h-16 rounded-full border-2 border-indigo-300"
          alt="avatar"
        >
        <div class="text-left flex-1">
          <h2 class="font-bold text-lg text-gray-800">{{ userStore.user.name }}</h2>
          <p class="text-sm text-gray-500">{{ userStore.user.rank_name }}</p>
          
          <!-- EXP Bar -->
          <div class="mt-2">
            <div class="flex justify-between text-xs text-gray-600 mb-1">
              <span>Lv.{{ userStore.user.level }}</span>
              <span>{{ userStore.user.exp }} / {{ userStore.user.next_exp }} XP</span>
            </div>
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                :style="{ width: userStore.expPercentage + '%' }"
              />
            </div>
          </div>
        </div>
      </div>
    </GlassPanel>

    <!-- Stats Cards -->
    <div class="grid grid-cols-2 gap-4">
      <GlassPanel class="text-center">
        <p class="text-3xl font-bold text-indigo-600">
          {{ userStore.user.total_hours?.toFixed(1) || '0' }}
        </p>
        <p class="text-sm text-gray-500">累計時間</p>
      </GlassPanel>
      
      <GlassPanel class="text-center">
        <p class="text-3xl font-bold text-amber-500">
          {{ userStore.user.xp || 0 }}
        </p>
        <p class="text-sm text-gray-500">所持 XP</p>
      </GlassPanel>
    </div>

    <!-- Session Resume Card (一時中断中のみ表示) -->
    <GlassPanel v-if="studyStore.isPaused" class="border-2 border-amber-300 animate-pulse">
      <div class="flex items-center justify-between">
        <div>
          <p class="text-amber-600 font-bold">⏸️ 勉強中断中</p>
          <p class="text-sm text-gray-600">
            {{ studyStore.currentSubject }} - {{ studyStore.lastSessionTime }}
          </p>
        </div>
        <button 
          @click="handleResume"
          class="bg-amber-500 text-white px-4 py-2 rounded-lg font-bold"
        >
          再開
        </button>
      </div>
    </GlassPanel>

    <!-- Today's Study Todo -->
    <GlassPanel>
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-bold text-gray-700">📌 今日の学習計画</h3>
        <button 
          @click="showTodoModal = true"
          class="text-xs px-3 py-1.5 rounded-lg bg-emerald-100 text-emerald-600 font-medium hover:bg-emerald-200 transition-colors"
        >
          + 追加
        </button>
      </div>
      
      <!-- Progress Summary -->
      <div class="flex items-center gap-3 mb-3 p-2 bg-gray-50 rounded-lg">
        <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all duration-300"
            :style="{ width: todoProgress + '%' }"
          />
        </div>
        <span class="text-xs font-medium text-gray-600">
          {{ completedTodos }}/{{ todayTodos.length }} 完了
        </span>
      </div>
      
      <!-- Todo List -->
      <div v-if="todayTodos.length === 0" class="text-center text-gray-400 py-4 text-sm">
        今日の学習計画を立てよう！📚
      </div>
      
      <div v-else class="space-y-2 max-h-48 overflow-y-auto">
        <div 
          v-for="todo in todayTodos" 
          :key="todo.id"
          :class="[
            'p-2.5 rounded-xl border transition-all',
            todo.completed 
              ? 'bg-green-50 border-green-200' 
              : 'bg-white border-gray-100 hover:border-emerald-200'
          ]"
        >
          <div class="flex items-start gap-2">
            <!-- Checkbox -->
            <button 
              @click="toggleTodo(todo.id)"
              :class="[
                'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-all',
                todo.completed 
                  ? 'bg-emerald-500 border-emerald-500 text-white' 
                  : 'border-gray-300 hover:border-emerald-400'
              ]"
            >
              <span v-if="todo.completed" class="text-xs">✓</span>
            </button>
            
            <!-- Content -->
            <div class="flex-1 min-w-0">
              <p :class="['text-sm font-medium', todo.completed ? 'text-gray-400 line-through' : 'text-gray-800']">
                {{ todo.title }}
              </p>
              <p v-if="todo.subject" class="text-[10px] text-gray-400">{{ todo.subject }}</p>
            </div>
            
            <!-- Time Goal Badge -->
            <span v-if="todo.targetMinutes" class="text-[10px] px-1.5 py-0.5 rounded bg-blue-100 text-blue-600 flex-shrink-0">
              {{ todo.targetMinutes }}分
            </span>
            
            <!-- Delete -->
            <button 
              @click="deleteTodo(todo.id)"
              class="text-gray-300 hover:text-red-400 text-xs flex-shrink-0"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
      
      <!-- Time Summary -->
      <div class="mt-3 pt-2 border-t border-gray-100 flex justify-between items-center text-xs text-gray-500">
        <span>今日の勉強: {{ todayMinutes }}分</span>
        <span v-if="totalTargetMinutes > 0">目標: {{ totalTargetMinutes }}分</span>
      </div>
    </GlassPanel>

    <!-- My Goals Section -->
    <GlassPanel>
      <div class="flex justify-between items-center mb-3">
        <h3 class="font-bold text-gray-700">🎯 マイ目標</h3>
        <button 
          @click="emit('openGoalModal')"
          class="text-xs px-3 py-1.5 rounded-lg bg-indigo-100 text-indigo-600 font-medium hover:bg-indigo-200 transition-colors"
        >
          + 追加
        </button>
      </div>
      
      <div v-if="myGoals.length === 0" class="text-center text-gray-400 py-4 text-sm">
        目標を設定してモチベーションアップ！
      </div>
      
      <div v-else class="space-y-2">
        <div 
          v-for="goal in myGoals" 
          :key="goal.id"
          class="p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <h4 class="font-bold text-gray-800 text-sm truncate">{{ goal.title }}</h4>
              <p v-if="goal.description" class="text-xs text-gray-500 truncate">{{ goal.description }}</p>
            </div>
            <span 
              class="text-xs px-2 py-0.5 rounded-full ml-2 flex-shrink-0"
              :class="getGoalUrgencyClass(goal.target_date)"
            >
              {{ formatGoalDays(goal.target_date) }}
            </span>
          </div>
          <div class="flex justify-between items-center mt-2">
            <span class="text-xs text-gray-400">🗓️ {{ formatGoalDate(goal.target_date) }}</span>
            <div class="flex gap-1">
              <button 
                @click="emit('editGoal', goal)"
                class="text-xs px-2 py-1 rounded bg-blue-100 text-blue-600 font-medium hover:bg-blue-200"
              >
                ✏️ 編集
              </button>
              <button 
                @click="completeGoal(goal.id)"
                class="text-xs px-2 py-1 rounded bg-green-100 text-green-600 font-medium hover:bg-green-200"
              >
                ✅ 達成
              </button>
            </div>
          </div>
        </div>
      </div>
    </GlassPanel>

    <!-- Menu Grid: Shop & Gacha (2 columns) -->
    <div class="grid grid-cols-2 gap-3">
      <button 
        @click="openShop"
        class="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg flex flex-col items-center justify-center gap-1 transition-transform active:scale-95 border-b-4 border-amber-200"
      >
        <span class="text-4xl">🏪</span>
        <span class="font-bold text-gray-700">ショップ</span>
      </button>

      <button 
        @click="openGacha"
        class="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg flex flex-col items-center justify-center gap-1 transition-transform active:scale-95 border-b-4 border-purple-200"
      >
        <span class="text-4xl">🔮</span>
        <span class="font-bold text-gray-700">ガチャ</span>
        <span class="text-[10px] text-red-500 font-bold bg-red-100 px-1.5 py-0.5 rounded-full">準備中</span>
      </button>
    </div>

    <!-- Menu Grid: Materials & Bookshelf (2 columns) -->
    <div class="grid grid-cols-2 gap-3">
      <button 
        @click="emit('openMaterials')"
        class="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg flex flex-col items-center justify-center gap-1 transition-transform active:scale-95 border-b-4 border-green-200"
      >
        <span class="text-4xl">📖</span>
        <span class="font-bold text-gray-700">教材</span>
      </button>

      <button 
        @click="emit('openBookshelf')"
        class="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-lg flex flex-col items-center justify-center gap-1 transition-transform active:scale-95 border-b-4 border-blue-200"
      >
        <span class="text-4xl">📚</span>
        <span class="font-bold text-gray-700">本棚</span>
      </button>
    </div>
    
    <!-- Today's Todo Modal -->
    <div v-if="showTodoModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-2xl shadow-xl w-full max-w-sm overflow-hidden">
        <div class="bg-gradient-to-r from-emerald-500 to-green-600 p-4 flex justify-between items-center">
          <h3 class="text-white font-bold">📝 学習計画を追加</h3>
          <button @click="showTodoModal = false" class="text-white/80 hover:text-white">✕</button>
        </div>
        <div class="p-4 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">何を学ぶ？ *</label>
            <input 
              v-model="newTodo.title"
              type="text"
              placeholder="例: 数学の二次方程式を理解する"
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-emerald-400 focus:outline-none"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">科目（任意）</label>
            <select 
              v-model="newTodo.subject"
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-emerald-400 focus:outline-none"
            >
              <option value="">選択しない</option>
              <option value="国語">国語</option>
              <option value="数学">数学</option>
              <option value="英語">英語</option>
              <option value="理科">理科</option>
              <option value="社会">社会</option>
              <option value="その他">その他</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">目標時間（分）</label>
            <input 
              v-model.number="newTodo.targetMinutes"
              type="number"
              min="0"
              max="120"
              placeholder="30"
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-emerald-400 focus:outline-none"
            >
          </div>
          <button 
            @click="addTodo"
            :disabled="!newTodo.title"
            class="w-full py-3 bg-emerald-500 text-white font-bold rounded-xl disabled:bg-gray-300 hover:bg-emerald-600 transition-colors"
          >
            追加する
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'
import { useShopStore } from '@/stores/shop'
import { useSound } from '@/composables/useSound'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToastStore } from '@/stores/toast'
import GlassPanel from '@/components/common/GlassPanel.vue'

const userStore = useUserStore()
const studyStore = useStudyStore()
const shopStore = useShopStore()
const { playSound } = useSound()
const { showConfirm } = useConfirmDialog()
const toast = useToastStore()

const emit = defineEmits(['timer', 'openGoalModal', 'openMaterials', 'openBookshelf', 'editGoal'])

const defaultAvatar = 'https://cdn-icons-png.flaticon.com/512/4333/4333609.png'

// Goal data
const myGoals = ref([])

// Today's study minutes (fetched from API)
const todayMinutes = ref(0)

// ===== Today's Todo System =====
const showTodoModal = ref(false)
const todayTodos = ref([])
const newTodo = ref({
  title: '',
  subject: '',
  targetMinutes: 30
})

// Computed
const completedTodos = computed(() => todayTodos.value.filter(t => t.completed).length)
const todoProgress = computed(() => {
  if (todayTodos.value.length === 0) return 0
  return Math.round((completedTodos.value / todayTodos.value.length) * 100)
})
const totalTargetMinutes = computed(() => {
  return todayTodos.value.reduce((sum, t) => sum + (t.targetMinutes || 0), 0)
})

// Todo functions
const getTodayKey = () => {
  const today = new Date().toISOString().split('T')[0]
  return `study_todos_${userStore.currentUserId}_${today}`
}

const loadTodos = () => {
  try {
    const saved = localStorage.getItem(getTodayKey())
    if (saved) {
      todayTodos.value = JSON.parse(saved)
    } else {
      todayTodos.value = []
    }
  } catch (e) {
    todayTodos.value = []
  }
}

const saveTodos = () => {
  localStorage.setItem(getTodayKey(), JSON.stringify(todayTodos.value))
}

const addTodo = () => {
  if (!newTodo.value.title.trim()) return
  
  const todo = {
    id: Date.now(),
    title: newTodo.value.title.trim(),
    subject: newTodo.value.subject,
    targetMinutes: newTodo.value.targetMinutes || 0,
    completed: false,
    createdAt: new Date().toISOString()
  }
  
  todayTodos.value.push(todo)
  saveTodos()
  playSound('select1')
  
  // Reset form
  newTodo.value = { title: '', subject: '', targetMinutes: 30 }
  showTodoModal.value = false
}

const toggleTodo = (id) => {
  const todo = todayTodos.value.find(t => t.id === id)
  if (todo) {
    todo.completed = !todo.completed
    saveTodos()
    if (todo.completed) {
      playSound('success')
      toast.success('タスク完了！🎉')
    }
  }
}

const deleteTodo = async (id) => {
  const confirmed = await showConfirm({
    type: 'warning',
    title: '削除確認',
    message: 'この計画を削除しますか？',
    confirmText: '削除',
    cancelText: 'キャンセル'
  })
  if (confirmed) {
    todayTodos.value = todayTodos.value.filter(t => t.id !== id)
    saveTodos()
  }
}

const openShop = () => {
  playSound('select1')
  shopStore.openShopList()
}

const openGacha = () => {
  playSound('select2') // Using a different sound just to acknowledge tap
  toast.info('ガチャは現在準備中です！\nアップデートをお楽しみに！')
}

// Fetch today's study minutes
const fetchTodayStats = async () => {
  if (!userStore.currentUserId) return
  try {
    const res = await fetch(`/api/user/${userStore.currentUserId}/stats`)
    const data = await res.json()
    if (Array.isArray(data.weekly) && data.weekly.length > 0) {
      // Get today's data (last item in weekly array)
      const today = data.weekly[data.weekly.length - 1]
      todayMinutes.value = today?.minutes || 0
    }
  } catch (e) {
    console.error('Failed to fetch today stats:', e)
  }
}

// Goal functions
const fetchMyGoals = async () => {
  if (!userStore.currentUserId) return
  try {
    const res = await fetch(`/api/goals/user/${userStore.currentUserId}`)
    const data = await res.json()
    if (data.status === 'ok') {
      myGoals.value = data.goals || []
    }
  } catch (e) {
    console.error('Failed to fetch goals:', e)
  }
}

const formatGoalDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

const formatGoalDays = (targetDate) => {
  if (!targetDate) return ''
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  const days = Math.ceil((target - today) / (1000 * 60 * 60 * 24))
  if (days < 0) return '期限切れ'
  if (days === 0) return '今日!'
  if (days === 1) return '明日'
  return `あと${days}日`
}

const getGoalUrgencyClass = (targetDate) => {
  if (!targetDate) return 'bg-gray-100 text-gray-600'
  const target = new Date(targetDate)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  const days = Math.ceil((target - today) / (1000 * 60 * 60 * 24))
  if (days < 0) return 'bg-red-100 text-red-600'
  if (days <= 3) return 'bg-orange-100 text-orange-600'
  if (days <= 7) return 'bg-yellow-100 text-yellow-600'
  return 'bg-green-100 text-green-600'
}

const completeGoal = async (goalId) => {
  const confirmed = await showConfirm({
    type: 'success',
    title: '目標達成！🎉',
    message: 'この目標を達成済みにしますか？\nおめでとう！頑張ったね！',
    confirmText: '達成！',
    cancelText: 'まだ続ける',
    icon: '🏆'
  })
  if (!confirmed) return
  
  try {
    const res = await fetch(`/api/goals/${goalId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userStore.currentUserId })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      playSound('success')
      await fetchMyGoals()
    } else {
      toast.error('完了処理に失敗しました')
    }
  } catch (e) {
    console.error('Complete goal error:', e)
    toast.error('完了処理に失敗しました')
  }
}

const onGoalCreated = () => {
  fetchMyGoals()
}

// 中断中のセッションを再開
const handleResume = async () => {
  const success = await studyStore.resumeStudy()
  if (success) {
    emit('timer')
  }
}

onMounted(() => {
  fetchTodayStats()
  fetchMyGoals()
  loadTodos()
})

// Expose for parent component
defineExpose({ fetchMyGoals })
</script>
