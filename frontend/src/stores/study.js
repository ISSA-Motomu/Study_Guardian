import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import { useToastStore } from './toast'
import { useSound } from '@/composables/useSound'
import { useConfirmDialog } from '@/composables/useConfirmDialog'

export const useStudyStore = defineStore('study', () => {
  const userStore = useUserStore()
  const toastStore = useToastStore()
  const { playSound } = useSound()
  const { showConfirm } = useConfirmDialog()

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

      if (!res.ok) {
        throw new Error(`HTTPステータス: ${res.status} (${res.statusText})`)
      }

      const json = await res.json()
      if (json.status === 'ok') {
        const studyMinutes = json.minutes

        // 進化ゲームにブーストを発動（エラーがあっても無視）
        let gemsEarned = 0
        try {
          // 動的インポートで循環参照を回避
          const { useEvolutionStore } = await import('./evolution')
          const evolutionStore = useEvolutionStore()

          if (evolutionStore) {
            const boostResult = evolutionStore.activateStudyBoost(studyMinutes)

            // 30分以上でデイリーチャレンジ達成
            let dailyBonus = null
            if (studyMinutes >= 30) {
              dailyBonus = evolutionStore.completeDailyChallenge()
            }

            // 勉強ポイントを付与（進化ゲーム連携）
            evolutionStore.earnFromStudy(studyMinutes)

            // 勉強石を獲得！（15分以上で獲得）
            gemsEarned = evolutionStore.earnStudyGems(studyMinutes)

            // ブースト発動をトーストで通知
            let message = `お疲れ様でした！\n${studyMinutes}分 勉強しました。`

            // 勉強石獲得メッセージ
            if (gemsEarned > 0) {
              message += `\n\n💎 勉強石 ×${gemsEarned} 獲得！`
            }

            if (boostResult) {
              const boostMins = Math.floor(boostResult.boostSeconds / 60)
              message += `\n🚀 ${boostMins}分間 ×${boostResult.multiplier}ブースト！`
            }
            if (dailyBonus) {
              message += `\n🎯 デイリーチャレンジ達成！`
            }

            toastStore.success(message)
          } else {
            toastStore.success(`お疲れ様でした！\n${studyMinutes}分 勉強しました。`)
          }
        } catch (e) {
          // 進化ゲームエラーは無視（メイン機能に影響させない）
          console.warn('Evolution boost error:', e)
          toastStore.success(`お疲れ様でした！\n${studyMinutes}分 勉強しました。`)
        }

        resetSession()
        await userStore.fetchUserData(userStore.currentUserId)
        return studyMinutes
      } else {
        toastStore.error('終了処理に失敗しました: ' + json.message)
      }
    } catch (e) {
      console.error(e)
      toastStore.error(`通信エラーが発生しました\n${e.message}`)
    }
    return 0
  }

  const cancelStudy = async () => {
    const confirmed = await showConfirm({
      type: 'warning',
      title: '記録の取消',
      message: '本当に記録を取り消しますか？\n(時間はカウントされません)',
      confirmText: '取り消す',
      cancelText: 'やめる',
      icon: '🗑️'
    })
    if (!confirmed) return

    playSound('click')
    try {
      const res = await fetch('/api/study/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userStore.currentUserId })
      })
      const json = await res.json()
      if (json.status === 'ok') {
        toastStore.info('記録を取り消しました。')
        resetSession()
      } else {
        toastStore.error('取消に失敗しました')
      }
    } catch (e) {
      toastStore.error(`通信エラー: ${e.message}`)
    }
  }

  const pauseStudy = async (closeApp = false) => {
    playSound('click')
    const confirmed = await showConfirm({
      type: 'info',
      title: '一時中断',
      message: '勉強を一時中断してメニューに戻りますか？\n(時間はここでストップします)',
      confirmText: '中断する',
      cancelText: '続ける',
      icon: '⏸️'
    })
    if (!confirmed) return false

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
        toastStore.error('中断処理に失敗しました')
      }
    } catch (e) {
      toastStore.error(`通信エラー: ${e.message}`)
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
