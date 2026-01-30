import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  // State
  const toasts = ref([])

  // Actions
  const show = (message, type = 'info', duration = 3000) => {
    const id = Date.now()
    toasts.value.push({
      id,
      message,
      type, // 'success', 'error', 'warning', 'info'
      duration
    })

    // 自動削除
    if (duration > 0) {
      setTimeout(() => {
        dismiss(id)
      }, duration)
    }
  }

  const success = (message, duration = 3000) => {
    show(message, 'success', duration)
  }

  const error = (message, duration = 5000) => {
    show(message, 'error', duration)
  }

  const warning = (message, duration = 4000) => {
    show(message, 'warning', duration)
  }

  const info = (message, duration = 3000) => {
    show(message, 'info', duration)
  }

  // 429専用エラーメッセージ
  const showRateLimitError = () => {
    show('429 error!!\n無料のスプレッドシート使ってるから\nAPIが限界やわ!!😱\nちょっと待ってな〜', 'error', 5000)
  }

  const dismiss = (id) => {
    const index = toasts.value.findIndex(t => t.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }

  const dismissAll = () => {
    toasts.value = []
  }

  return {
    toasts,
    show,
    success,
    error,
    warning,
    info,
    showRateLimitError,
    dismiss,
    dismissAll
  }
})
