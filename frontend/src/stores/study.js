import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import { useSound } from '@/composables/useSound'

export const useStudyStore = defineStore('study', () => {
  const userStore = useUserStore()
  const { playSound } = useSound()

  // State
  const subjects = ref({})
  const studying = ref(false)
  const inSession = ref(false)
  const lastSessionTime = ref('00:00:00')
  const currentSubject = ref('')
  const currentSubjectColor = ref('#000')
  const startTime = ref(null)
  const timerInterval = ref(null)
  const timerDisplay = ref('00:00:00')

  const showSubjectModal = ref(false)
  const studyMemo = ref('')
  const showMemoConfirm = ref(false)
  const memoToSend = ref('')

  // Actions
  const openSubjectModal = async () => {
    playSound('click')
    showSubjectModal.value = true

    if (Object.keys(subjects.value).length === 0) {
      try {
        const res = await fetch('/api/study/subjects')
        const json = await res.json()
        if (json.status === 'ok') {
          subjects.value = json.data
        }
      } catch (e) {
        console.error(e)
      }
    }
  }

  const startStudy = async (subject) => {
    playSound('select1')

    if (!userStore.currentUserId) {
      alert('エラー: ユーザーIDが取得できていません。再読み込みしてください。')
      return
    }

    studying.value = true
    try {
      const res = await fetch('/api/study/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          subject: subject
        })
      })

      if (!res.ok) {
        throw new Error(`Server Error (${res.status})`)
      }

      const json = await res.json()
      if (json.status === 'ok') {
        currentSubject.value = subject
        currentSubjectColor.value = subjects.value[subject]
        startTime.value = new Date()
        startTimerTick()
        inSession.value = true
        showSubjectModal.value = false
      } else {
        alert('開始失敗: ' + json.message)
      }
    } catch (e) {
      alert('通信エラー: ' + e.message)
      console.error(e)
    } finally {
      studying.value = false
    }
  }

  const startTimerTick = () => {
    if (timerInterval.value) clearInterval(timerInterval.value)
    timerInterval.value = setInterval(() => {
      const now = new Date()
      const diff = now - startTime.value
      const hours = Math.floor(diff / 3600000)
      const minutes = Math.floor((diff % 3600000) / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      timerDisplay.value =
        (hours > 0 ? String(hours).padStart(2, '0') + ':' : '') +
        String(minutes).padStart(2, '0') + ':' +
        String(seconds).padStart(2, '0')
    }, 1000)
  }

  const openMemoConfirm = () => {
    memoToSend.value = studyMemo.value
    showMemoConfirm.value = true
  }

  const finishStudy = async () => {
    playSound('levelup')
    showMemoConfirm.value = false

    try {
      const res = await fetch('/api/study/finish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          memo: memoToSend.value
        })
      })

      if (!res.ok) throw new Error(`Server returned ${res.status}`)

      const json = await res.json()
      if (json.status === 'ok') {
        alert(`お疲れ様でした！\n${json.minutes}分 勉強しました。`)
        resetSession()
        await userStore.fetchUserData(userStore.currentUserId)
        return json.minutes
      } else {
        alert('終了処理に失敗しました: ' + json.message)
      }
    } catch (e) {
      console.error(e)
      alert('通信エラーが発生しました。')
    }
    return 0
  }

  const cancelStudy = async () => {
    if (!confirm('本当に記録を取り消しますか？\n(この時間はカウントされません)')) return

    playSound('click')
    try {
      const res = await fetch('/api/study/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userStore.currentUserId })
      })
      const json = await res.json()
      if (json.status === 'ok') {
        alert('記録を取り消しました。')
        resetSession()
      } else {
        alert('取消に失敗しました')
      }
    } catch (e) {
      alert('通信エラー')
    }
  }

  const pauseStudy = async (closeApp = false) => {
    playSound('click')
    if (!confirm('勉強を一時中断してメニューに戻りますか？\n(時間はここでストップします)')) return false

    lastSessionTime.value = timerDisplay.value

    try {
      const res = await fetch('/api/study/pause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userStore.currentUserId })
      })
      const json = await res.json()
      if (json.status === 'ok') {
        studying.value = false
        clearInterval(timerInterval.value)
        // inSession remains true (paused state)

        if (closeApp && window.liff) {
          liff.closeWindow()
        }
        return true
      } else {
        alert('中断処理に失敗しました')
      }
    } catch (e) {
      alert('通信エラー')
    }
    return false
  }

  const checkActiveSession = async (userId) => {
    try {
      const res = await fetch(`/api/user/${userId}/active_session`)
      const json = await res.json()
      if (json.status === 'ok' && json.active) {
        currentSubject.value = json.data.subject
        currentSubjectColor.value = subjects.value[json.data.subject] || '#000'

        const startTimeParts = json.data.start_time.split(':')
        const now = new Date()
        const startDate = new Date(
          now.getFullYear(), now.getMonth(), now.getDate(),
          Number(startTimeParts[0]), Number(startTimeParts[1]), Number(startTimeParts[2])
        )
        if (startDate > now) startDate.setDate(startDate.getDate() - 1)

        startTime.value = startDate
        startTimerTick()
        inSession.value = true
        return true
      }
    } catch (e) {
      console.error(e)
    }
    inSession.value = false
    return false
  }

  const resetSession = () => {
    studying.value = false
    clearInterval(timerInterval.value)
    inSession.value = false
    studyMemo.value = ''
    memoToSend.value = ''
    timerDisplay.value = '00:00:00'
  }

  return {
    // State
    subjects,
    studying,
    inSession,
    lastSessionTime,
    currentSubject,
    currentSubjectColor,
    timerDisplay,
    showSubjectModal,
    studyMemo,
    showMemoConfirm,
    memoToSend,
    // Actions
    openSubjectModal,
    startStudy,
    openMemoConfirm,
    finishStudy,
    cancelStudy,
    pauseStudy,
    checkActiveSession,
    resetSession
  }
})
