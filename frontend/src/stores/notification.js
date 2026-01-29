import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref([])
  const unreadCount = ref(0)
  const pollingInterval = ref(null)
  const lastChecked = ref(null)

  // Actions
  const addNotification = (notification) => {
    const id = Date.now()
    notifications.value.unshift({
      id,
      ...notification,
      read: false,
      timestamp: new Date().toISOString()
    })
    unreadCount.value++
    
    // 最大20件に制限
    if (notifications.value.length > 20) {
      notifications.value = notifications.value.slice(0, 20)
    }
  }

  const markAsRead = (id) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification && !notification.read) {
      notification.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
    unreadCount.value = 0
  }

  const clearAll = () => {
    notifications.value = []
    unreadCount.value = 0
  }

  // 承認待ちをポーリングで確認（Admin用）
  const checkPendingForAdmin = async () => {
    const userStore = useUserStore()
    if (!userStore.isAdmin) return

    try {
      const res = await fetch('/api/admin/pending')
      const data = await res.json()
      
      if (data.status === 'ok' && data.data) {
        const currentCount = data.data.length
        const previousCount = parseInt(localStorage.getItem('lastPendingCount') || '0')
        
        if (currentCount > previousCount && previousCount > 0) {
          // 新しい承認待ちがある
          const newItems = currentCount - previousCount
          addNotification({
            type: 'pending',
            title: '新しい承認待ち',
            message: `${newItems}件の新しい承認リクエストがあります`,
            icon: '📬'
          })
        }
        
        localStorage.setItem('lastPendingCount', currentCount.toString())
      }
    } catch (e) {
      console.error('Pending check error:', e)
    }
  }

  // ユーザーの承認結果をポーリングで確認
  const checkApprovalResults = async () => {
    const userStore = useUserStore()
    if (!userStore.currentUserId) return

    try {
      const res = await fetch(`/api/user/${userStore.currentUserId}/notifications`)
      const data = await res.json()
      
      if (data.status === 'ok' && data.notifications) {
        data.notifications.forEach(n => {
          // 既存の通知と重複しないようにチェック
          const exists = notifications.value.some(
            existing => existing.originalId === n.id
          )
          if (!exists) {
            addNotification({
              ...n,
              originalId: n.id
            })
          }
        })
      }
    } catch (e) {
      // API未実装の場合は静かに失敗
    }
  }

  // ポーリング開始
  const startPolling = () => {
    if (pollingInterval.value) return
    
    // 初回チェック
    checkPendingForAdmin()
    checkApprovalResults()
    
    // 30秒ごとにチェック
    pollingInterval.value = setInterval(() => {
      checkPendingForAdmin()
      checkApprovalResults()
    }, 30000)
  }

  // ポーリング停止
  const stopPolling = () => {
    if (pollingInterval.value) {
      clearInterval(pollingInterval.value)
      pollingInterval.value = null
    }
  }

  return {
    // State
    notifications,
    unreadCount,
    // Actions
    addNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    startPolling,
    stopPolling,
    checkPendingForAdmin
  }
})
