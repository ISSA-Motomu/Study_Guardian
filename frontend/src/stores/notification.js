import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'

// LocalStorage キー
const NOTIFICATIONS_KEY = 'sg_notifications'
const ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000 // 1週間

// LocalStorageから通知を復元
const loadNotifications = () => {
  try {
    const saved = localStorage.getItem(NOTIFICATIONS_KEY)
    if (saved) {
      const parsed = JSON.parse(saved)
      // 1週間以内の通知のみ保持
      const oneWeekAgo = Date.now() - ONE_WEEK_MS
      return parsed.filter(n => new Date(n.timestamp).getTime() > oneWeekAgo)
    }
  } catch (e) {
    console.warn('Failed to load notifications:', e)
  }
  return []
}

// LocalStorageに通知を保存
const saveNotifications = (notifications) => {
  try {
    localStorage.setItem(NOTIFICATIONS_KEY, JSON.stringify(notifications))
  } catch (e) {
    console.warn('Failed to save notifications:', e)
  }
}

export const useNotificationStore = defineStore('notification', () => {
  // State（LocalStorageから復元）
  const notifications = ref(loadNotifications())
  const unreadCount = ref(notifications.value.filter(n => !n.read).length)
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

    // 1週間以内の通知のみ保持（最大100件）
    const oneWeekAgo = Date.now() - ONE_WEEK_MS
    notifications.value = notifications.value
      .filter(n => new Date(n.timestamp).getTime() > oneWeekAgo)
      .slice(0, 100)

    // LocalStorageに保存
    saveNotifications(notifications.value)
  }

  const markAsRead = (id) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification && !notification.read) {
      notification.read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      saveNotifications(notifications.value)
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
    unreadCount.value = 0
    saveNotifications(notifications.value)
  }

  const clearAll = () => {
    notifications.value = []
    unreadCount.value = 0
    saveNotifications(notifications.value)
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

    // 初回チェック（少し遅延させて初期化完了を待つ）
    setTimeout(() => {
      checkPendingForAdmin()
      checkApprovalResults()
    }, 5000)

    // 60秒ごとにチェック（API負荷軽減）
    pollingInterval.value = setInterval(() => {
      checkPendingForAdmin()
      checkApprovalResults()
    }, 60000)
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
