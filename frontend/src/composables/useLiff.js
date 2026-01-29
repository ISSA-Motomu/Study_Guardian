import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'

const liffId = import.meta.env.VITE_LIFF_ID || '2007525134-MmemlK4B'
const isInitialized = ref(false)
const liffError = ref(null)

export function useLiff() {
  const userStore = useUserStore()
  const studyStore = useStudyStore()

  const initLiff = async () => {
    try {
      // Check if LIFF SDK is loaded
      if (typeof liff === 'undefined') {
        throw new Error('LIFF SDK not loaded')
      }

      await liff.init({ liffId })
      isInitialized.value = true

      if (!liff.isLoggedIn()) {
        liff.login()
        return
      }

      const profile = await liff.getProfile()
      const userId = profile.userId

      userStore.setUserId(userId)
      await userStore.fetchUserData(userId)
      await studyStore.checkActiveSession(userId)

      userStore.setLoading(false)
    } catch (e) {
      console.error('LIFF init error:', e)
      liffError.value = e.message

      // Development fallback
      if (import.meta.env.DEV || window.location.hostname === 'localhost') {
        console.warn('Using development mock data')
        const mockUserId = 'dev_user_123'
        userStore.setUserId(mockUserId)
        await userStore.fetchUserData(mockUserId)
        userStore.setLoading(false)
      }
    }
  }

  const closeWindow = () => {
    if (typeof liff !== 'undefined' && liff.isInClient()) {
      liff.closeWindow()
    }
  }

  const isInApp = computed(() => {
    return typeof liff !== 'undefined' && liff.isInClient()
  })

  return {
    initLiff,
    closeWindow,
    isInitialized,
    liffError,
    isInApp
  }
}
