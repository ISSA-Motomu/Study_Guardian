import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'

const liffId = import.meta.env.VITE_LIFF_ID || '2008998497-Vfli3v7u'
const isInitialized = ref(false)
const liffError = ref(null)

// ユーザーID永続化キー
const USER_ID_KEY = 'sg_user_id'

// ユーザーIDをLocalStorageに保存
const saveUserId = (userId) => {
  try {
    localStorage.setItem(USER_ID_KEY, userId)
  } catch (e) {
    console.warn('Failed to save user ID:', e)
  }
}

// LocalStorageからユーザーIDを復元
const getSavedUserId = () => {
  try {
    return localStorage.getItem(USER_ID_KEY)
  } catch (e) {
    return null
  }
}

// プログレス更新ヘルパー
const updateProgress = (percent, status) => {
  if (typeof window !== 'undefined' && window.updateProgress) {
    window.updateProgress(percent, status)
  }
}

const showError = (msg) => {
  if (typeof window !== 'undefined' && window.showError) {
    window.showError(msg)
  }
}

const hideLoader = () => {
  if (typeof window !== 'undefined' && window.hideLoader) {
    window.hideLoader()
  }
}

export function useLiff() {
  const userStore = useUserStore()
  const studyStore = useStudyStore()

  const initLiff = async () => {
    try {
      updateProgress(65, 'LINE認証を初期化中...')

      // Check if LIFF SDK is loaded
      if (typeof liff === 'undefined') {
        throw new Error('LIFF SDK not loaded')
      }

      await liff.init({ liffId })
      isInitialized.value = true
      updateProgress(70, 'LINE認証完了')

      if (!liff.isLoggedIn()) {
        updateProgress(75, 'LINEログイン画面へ移動...')
        liff.login()
        return
      }

      updateProgress(80, 'プロフィール取得中...')
      const profile = await liff.getProfile()
      const userId = profile.userId

      // ユーザーIDを永続化
      saveUserId(userId)

      // Send profile to server to update avatar_url
      try {
        await fetch('/api/user/update_profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            display_name: profile.displayName,
            avatar_url: profile.pictureUrl || ''
          })
        })
      } catch (profileErr) {
        console.warn('Profile update failed:', profileErr)
      }

      userStore.setUserId(userId)

      updateProgress(85, 'ユーザーデータ取得中...')
      await userStore.fetchUserData(userId)

      updateProgress(90, 'セッション確認中...')
      await studyStore.checkActiveSession(userId)

      updateProgress(100, '準備完了！')
      userStore.setLoading(false)

      // Hide loader after a short delay
      setTimeout(hideLoader, 300)
    } catch (e) {
      console.error('LIFF init error:', e)
      liffError.value = e.message

      // Development fallback or non-LINE browser
      const isDev = import.meta.env.DEV || window.location.hostname === 'localhost'
      const isNonLineBrowser = !window.location.href.includes('liff.line.me')

      if (isDev || isNonLineBrowser) {
        console.warn('Using development/browser mode')
        updateProgress(80, 'ブラウザモードで起動中...')

        // Try to get user from URL, saved ID, or use mock
        const urlParams = new URLSearchParams(window.location.search)
        const mockUserId = urlParams.get('user_id') || getSavedUserId() || 'dev_user_123'

        // ユーザーIDを永続化
        saveUserId(mockUserId)
        userStore.setUserId(mockUserId)

        updateProgress(90, 'ユーザーデータ取得中...')
        await userStore.fetchUserData(mockUserId)

        updateProgress(100, '準備完了！')
        userStore.setLoading(false)
        setTimeout(hideLoader, 300)
      } else {
        // Show error on loader
        showError('初期化エラー: ' + e.message + '\nページを再読み込みしてください')
        updateProgress(0, 'エラーが発生しました')
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
