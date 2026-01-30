import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // State
  const loading = ref(true)
  const currentUserId = ref(null)
  const originalUserId = ref(null) // 管理者の元のID（なりすまし時に保持）
  const isViewingAsOther = ref(false) // 他ユーザーとして表示中
  const user = ref({
    name: 'Guest',
    level: 1,
    exp: 0,
    next_exp: 100,
    xp: 0,
    total_hours: 0,
    rank_name: 'Beginner',
    avatar_url: '',
    role: 'USER'
  })

  // Computed
  const expPercentage = computed(() => {
    if (user.value.next_exp === 0) return 100
    return Math.min(100, (user.value.exp / user.value.next_exp) * 100)
  })

  const isAdmin = computed(() => user.value.role === 'ADMIN')

  // Actions
  const setUserId = (id) => {
    currentUserId.value = id
    if (!originalUserId.value) {
      originalUserId.value = id
    }
  }

  const fetchUserData = async (userId) => {
    try {
      const response = await fetch(`/api/user/${userId}/status`)
      if (!response.ok) throw new Error('API Error')

      const data = await response.json()
      if (data.status === 'ok') {
        user.value = data.data
      }
    } catch (e) {
      console.error(e)
      // Mock data for development
      user.value = {
        name: '勇者アルス',
        level: 12,
        exp: 1450,
        next_exp: 2000,
        xp: 500,
        total_hours: 42.5,
        rank_name: 'Rank C: 熟練者',
        avatar_url: 'https://cdn-icons-png.flaticon.com/512/4333/4333609.png',
        role: 'USER'
      }
    }
  }

  const setLoading = (value) => {
    loading.value = value
  }

  // 他ユーザーとして表示（管理者専用）
  const viewAsUser = async (targetUserId, targetUserName) => {
    if (!isAdmin.value) return false
    
    isViewingAsOther.value = true
    currentUserId.value = targetUserId
    await fetchUserData(targetUserId)
    return true
  }

  // 元の管理者に戻る
  const exitViewAsUser = async () => {
    if (!originalUserId.value) return
    
    isViewingAsOther.value = false
    currentUserId.value = originalUserId.value
    await fetchUserData(originalUserId.value)
  }

  return {
    // State
    loading,
    currentUserId,
    originalUserId,
    isViewingAsOther,
    user,
    // Computed
    expPercentage,
    isAdmin,
    // Actions
    setUserId,
    fetchUserData,
    setLoading,
    viewAsUser,
    exitViewAsUser
  }
})
