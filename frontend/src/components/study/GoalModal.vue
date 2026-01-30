<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="emit('close')">
    <div class="bg-white rounded-2xl p-6 w-[90%] max-w-md shadow-2xl animate-pop-in">
      <h3 class="text-xl font-bold text-gray-800 mb-4">
        {{ isEdit ? '✏️ 目標を編集' : '🎯 目標を設定' }}
      </h3>
      
      <!-- Title -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">タイトル *</label>
        <input 
          v-model="title"
          type="text"
          placeholder="例：期末テストで80点以上"
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none transition-colors"
          maxlength="50"
        >
      </div>

      <!-- Description -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">詳細（任意）</label>
        <textarea 
          v-model="description"
          placeholder="目標達成のための具体的な計画など..."
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none transition-colors resize-none"
          rows="3"
          maxlength="200"
        />
      </div>

      <!-- Target Date -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-1">目標日 *</label>
        <input 
          v-model="targetDate"
          type="date"
          :min="minDate"
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-400 focus:outline-none transition-colors"
        >
        <p class="text-xs text-gray-500 mt-1">目標達成を目指す日付を選んでください</p>
      </div>

      <!-- Days Until -->
      <div v-if="targetDate && daysUntil >= 0" class="mb-6 p-4 bg-indigo-50 rounded-xl">
        <p class="text-center">
          <span class="text-3xl font-bold text-indigo-600">{{ daysUntil }}</span>
          <span class="text-gray-600">日後</span>
        </p>
      </div>

      <!-- Buttons -->
      <div class="flex gap-3">
        <button 
          @click="emit('close')"
          class="flex-1 py-3 rounded-xl font-bold text-gray-600 bg-gray-100 hover:bg-gray-200 transition-colors"
        >
          キャンセル
        </button>
        <button 
          @click="handleSubmit"
          :disabled="!canSubmit || submitting"
          class="flex-1 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-indigo-500 to-purple-500 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ submitting ? '保存中...' : (isEdit ? '✏️ 更新する' : '🎯 設定する') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useToastStore } from '@/stores/toast'

const props = defineProps({
  editGoal: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'created', 'updated'])

const userStore = useUserStore()
const toast = useToastStore()

const title = ref('')
const description = ref('')
const targetDate = ref('')
const submitting = ref(false)

// 編集モードかどうか
const isEdit = computed(() => !!props.editGoal)

// 今日の日付（最小値として使用）
const minDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// 目標日までの日数
const daysUntil = computed(() => {
  if (!targetDate.value) return -1
  const target = new Date(targetDate.value)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  target.setHours(0, 0, 0, 0)
  return Math.ceil((target - today) / (1000 * 60 * 60 * 24))
})

const canSubmit = computed(() => {
  return title.value.trim() && targetDate.value && daysUntil.value >= 0
})

// 編集モードの場合、初期値を設定
onMounted(() => {
  if (props.editGoal) {
    title.value = props.editGoal.title || ''
    description.value = props.editGoal.description || ''
    targetDate.value = props.editGoal.target_date || ''
  }
})

const handleSubmit = async () => {
  if (!canSubmit.value || submitting.value) return
  
  submitting.value = true
  
  try {
    if (isEdit.value) {
      // 更新
      const response = await fetch(`/api/goals/${props.editGoal.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          title: title.value.trim(),
          description: description.value.trim(),
          target_date: targetDate.value
        })
      })
      
      const result = await response.json()
      
      if (result.status === 'ok') {
        emit('updated')
        emit('close')
      } else {
        toast.error('目標の更新に失敗しました: ' + (result.message || 'Unknown error'))
      }
    } else {
      // 新規作成
      const response = await fetch('/api/goals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          user_name: userStore.user.name,
          title: title.value.trim(),
          description: description.value.trim(),
          target_date: targetDate.value
        })
      })
      
      const result = await response.json()
      
      if (result.status === 'ok') {
        emit('created')
        emit('close')
      } else {
        toast.error('目標の保存に失敗しました: ' + (result.message || 'Unknown error'))
      }
    }
  } catch (e) {
    console.error('Goal save error:', e)
    toast.error('目標の保存に失敗しました')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.animate-pop-in {
  animation: popIn 0.2s ease-out;
}

@keyframes popIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
