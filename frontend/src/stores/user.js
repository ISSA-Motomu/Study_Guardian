import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // State
  const loading = ref(true)
  const currentUserId = ref(null)
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

  return {
    // State
    loading,
    currentUserId,
    user,
    // Computed
    expPercentage,
    isAdmin,
    // Actions
    setUserId,
    fetchUserData,
    setLoading
  }
})
