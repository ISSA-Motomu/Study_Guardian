import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useUserStore } from './user'
import { useToastStore } from './toast'
import { useSound } from '@/composables/useSound'
import { useConfirmDialog } from '@/composables/useConfirmDialog'

/**
 * セッション状態（原子的な状態管理）
 * - IDLE: 勉強していない
 * - STUDYING: 勉強中（タイマー動作中）
 * - PAUSED: 一時中断中（タイマー停止、セッションあり）
 * - CONFIRMING: 終了確認中（振り返り画面表示中）
 */
const SessionState = {
  IDLE: 'IDLE',
  STUDYING: 'STUDYING',
  PAUSED: 'PAUSED',
  CONFIRMING: 'CONFIRMING'
}

export const useStudyStore = defineStore('study', () => {
  const userStore = useUserStore()
  const toastStore = useToastStore()
  const { playSound } = useSound()
  const { showConfirm } = useConfirmDialog()

  // ===== Core State (原子的) =====
  const sessionState = ref(SessionState.IDLE)
  const subjects = ref({})
  const currentSubject = ref('')
  const currentSubjectColor = ref('#000')
  const currentMaterial = ref(null)
  const startTime = ref(null)
  const pausedDuration = ref(0) // 中断時の経過時間（ミリ秒）
  const timerInterval = ref(null)
  const timerDisplay = ref('00:00:00')

  // UI State
  const showSubjectModal = ref(false)
  const studyMemo = ref('')
  const showMemoConfirm = ref(false)
  const memoToSend = ref('')
  const isLoading = ref(false) // API呼び出し中

  // ===== Computed (後方互換性のため) =====
  const inSession = computed(() => sessionState.value !== SessionState.IDLE)
  const isPaused = computed(() => sessionState.value === SessionState.PAUSED)
  const isTimerRunning = computed(() => sessionState.value === SessionState.STUDYING)
  const isConfirming = computed(() => sessionState.value === SessionState.CONFIRMING)
  const studying = computed(() => isLoading.value) // 後方互換
  const lastSessionTime = computed(() => {
    if (pausedDuration.value === 0) return timerDisplay.value
    const diff = pausedDuration.value
    const hours = Math.floor(diff / 3600000)
    const minutes = Math.floor((diff % 3600000) / 60000)
    const seconds = Math.floor((diff % 60000) / 1000)
    return (hours > 0 ? String(hours).padStart(2, '0') + ':' : '') +
      String(minutes).padStart(2, '0') + ':' +
      String(seconds).padStart(2, '0')
  })

  // ===== Helper Functions =====
  const getSubjectColor = (subject) => {
    const colors = {
      '国語': '#EF5350',
      '数学': '#42A5F5',
      '理科': '#66BB6A',
      '社会': '#AB47BC',
      '英語': '#7986CB',
      'その他': '#90A4AE'
    }
    return colors[subject] || '#90A4AE'
  }

  const startTimerTick = () => {
    stopTimerTick() // 既存のタイマーをクリア
    timerInterval.value = setInterval(() => {
      if (!startTime.value) return
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

  const stopTimerTick = () => {
    if (timerInterval.value) {
      clearInterval(timerInterval.value)
      timerInterval.value = null
    }
  }

  // ===== Actions =====
  const openSubjectModal = async () => {
    // 勉強中の場合は警告
    if (inSession.value) {
      toastStore.warning('勉強中です。タイマー画面から操作してください。')
      return
    }

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

  const startStudy = async (subject, material = null) => {
    // ガード: 既に勉強中なら開始しない
    if (inSession.value) {
      toastStore.warning('既に勉強中です。')
      return false
    }
    // ガード: ローディング中なら開始しない（連打防止）
    if (isLoading.value) {
      return false
    }

    playSound('select1')

    if (!userStore.currentUserId) {
      toastStore.error('ユーザーIDが取得できていません。再読み込みしてください。')
      return false
    }

    isLoading.value = true
    try {
      const subjectWithMaterial = material
        ? `${subject}（${material.title}）`
        : subject

      const res = await fetch('/api/study/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          subject: subjectWithMaterial
        })
      })

      if (!res.ok) {
        throw new Error(`Server Error (${res.status})`)
      }

      const json = await res.json()
      if (json.status === 'ok') {
        // 状態を原子的に更新
        currentSubject.value = subject
        currentSubjectColor.value = subjects.value[subject] || getSubjectColor(subject)
        currentMaterial.value = material
        startTime.value = new Date()
        pausedDuration.value = 0
        studyMemo.value = ''
        sessionState.value = SessionState.STUDYING
        startTimerTick()
        showSubjectModal.value = false
        return true
      } else {
        toastStore.error('開始失敗: ' + json.message)
        return false
      }
    } catch (e) {
      toastStore.error('通信エラー: ' + e.message)
      console.error(e)
      return false
    } finally {
      isLoading.value = false
    }
  }

  const openMemoConfirm = () => {
    // ガード: 勉強中でなければ無視
    if (sessionState.value !== SessionState.STUDYING) {
      toastStore.warning('勉強中ではありません。')
      return
    }
    memoToSend.value = studyMemo.value
    showMemoConfirm.value = true
    sessionState.value = SessionState.CONFIRMING
    // タイマーは継続（ファインマンテクニックの時間も勉強時間に含める）
  }

  const cancelMemoConfirm = () => {
    showMemoConfirm.value = false
    if (sessionState.value === SessionState.CONFIRMING) {
      sessionState.value = SessionState.STUDYING
    }
  }

  // 学習記録を保存
  const saveLearningRecord = (reflectionData, studyMinutes, subject) => {
    if (!reflectionData) return

    const records = JSON.parse(localStorage.getItem('study_learning_records') || '[]')
    const newRecord = {
      date: new Date().toISOString(),
      subject: subject,
      minutes: studyMinutes,
      reflection: reflectionData.reflection || '',
      understanding: reflectionData.understanding || null,
      reviewNote: reflectionData.reviewNote || ''
    }
    records.push(newRecord)

    // 最新100件のみ保持
    if (records.length > 100) {
      records.splice(0, records.length - 100)
    }

    localStorage.setItem('study_learning_records', JSON.stringify(records))
  }

  const finishStudy = async (reflectionData = null) => {
    // ガード: 勉強中・確認中でなければ終了しない
    if (sessionState.value !== SessionState.STUDYING && sessionState.value !== SessionState.CONFIRMING) {
      toastStore.warning('勉強中ではありません。')
      return 0
    }
    // ガード: ローディング中なら無視（連打防止）
    if (isLoading.value) {
      return 0
    }

    playSound('levelup')
    stopTimerTick()
    showMemoConfirm.value = false
    isLoading.value = true

    const hasReflection = reflectionData?.hasReflection || false

    try {
      // 振り返り内容をメモに追加
      let finalMemo = memoToSend.value
      if (reflectionData?.reflection) {
        finalMemo += (finalMemo ? '\n\n' : '') + '【振り返り】\n' + reflectionData.reflection
      }
      if (reflectionData?.understanding) {
        const understandingLabels = {
          perfect: '🌟 バッチリ！',
          good: '😊 だいたいOK',
          partial: '🤔 半分くらい',
          confused: '😵 まだ難しい'
        }
        finalMemo += '\n理解度: ' + (understandingLabels[reflectionData.understanding] || '')
      }
      if (reflectionData?.reviewNote) {
        finalMemo += '\n次回復習: ' + reflectionData.reviewNote
      }

      const res = await fetch('/api/study/finish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          memo: finalMemo
        })
      })

      if (!res.ok) {
        throw new Error(`HTTPステータス: ${res.status} (${res.statusText})`)
      }

      const json = await res.json()
      if (json.status === 'ok') {
        const studyMinutes = json.minutes

        // 学習記録をローカルに保存
        saveLearningRecord(reflectionData, studyMinutes, currentSubject.value)

        // 進化ゲームにブーストを発動（エラーがあっても無視）
        let gemsEarned = 0
        let reflectionBonus = 0
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

            // 振り返りボーナス！（ファインマンテクニック報酬）
            if (hasReflection && studyMinutes >= 15) {
              reflectionBonus = 1
              evolutionStore.studyGems.value += reflectionBonus
              evolutionStore.totalStudyGems.value += reflectionBonus
            }

            // ブースト発動をトーストで通知
            let message = `お疲れ様でした！\n${studyMinutes}分 勉強しました。`

            // 勉強石獲得メッセージ
            const totalGems = gemsEarned + reflectionBonus
            if (totalGems > 0) {
              message += `\n\n💎 勉強石 ×${totalGems} 獲得！`
              if (reflectionBonus > 0) {
                message += ' (振り返りボーナス+1)'
              }
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
        // 失敗時は状態を戻す
        sessionState.value = SessionState.STUDYING
        startTimerTick()
      }
    } catch (e) {
      console.error(e)
      toastStore.error(`通信エラーが発生しました\n${e.message}`)
      // 失敗時は状態を戻す
      sessionState.value = SessionState.STUDYING
      startTimerTick()
    } finally {
      isLoading.value = false
    }
    return 0
  }

  const cancelStudy = async () => {
    // ガード: 勉強中でなければ無視
    if (!inSession.value) {
      toastStore.warning('勉強中ではありません。')
      return
    }
    // ガード: ローディング中なら無視
    if (isLoading.value) {
      return
    }

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
    isLoading.value = true
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
    } finally {
      isLoading.value = false
    }
  }

  const pauseStudy = async (closeApp = false) => {
    // ガード: 勉強中でなければ無視
    if (sessionState.value !== SessionState.STUDYING && sessionState.value !== SessionState.CONFIRMING) {
      toastStore.warning('勉強中ではありません。')
      return false
    }
    // ガード: ローディング中なら無視
    if (isLoading.value) {
      return false
    }

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

    // 現在の経過時間を保存
    if (startTime.value) {
      pausedDuration.value = new Date() - startTime.value
    }

    isLoading.value = true
    try {
      const res = await fetch('/api/study/pause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userStore.currentUserId })
      })
      const json = await res.json()
      if (json.status === 'ok') {
        stopTimerTick()
        sessionState.value = SessionState.PAUSED
        showMemoConfirm.value = false

        if (closeApp && window.liff) {
          liff.closeWindow()
        }
        return true
      } else {
        toastStore.error('中断処理に失敗しました')
      }
    } catch (e) {
      toastStore.error(`通信エラー: ${e.message}`)
    } finally {
      isLoading.value = false
    }
    return false
  }

  const checkActiveSession = async (userId) => {
    try {
      const res = await fetch(`/api/user/${userId}/active_session`)
      const json = await res.json()
      if (json.status === 'ok' && json.active) {
        // 科目情報を復元（教材名付きの場合も対応）
        const rawSubject = json.data.subject || ''
        const subjectMatch = rawSubject.match(/^([^（]+)/)
        const subject = subjectMatch ? subjectMatch[1] : rawSubject

        currentSubject.value = subject
        currentSubjectColor.value = subjects.value[subject] || getSubjectColor(subject)

        const startTimeParts = json.data.start_time.split(':')
        const now = new Date()
        const startDate = new Date(
          now.getFullYear(), now.getMonth(), now.getDate(),
          Number(startTimeParts[0]), Number(startTimeParts[1]), Number(startTimeParts[2])
        )
        if (startDate > now) startDate.setDate(startDate.getDate() - 1)
        startTime.value = startDate

        // PENDING（一時中断中）の場合
        if (json.data.status === 'PENDING') {
          if (json.data.end_time) {
            const endParts = json.data.end_time.split(':')
            const endDate = new Date(
              now.getFullYear(), now.getMonth(), now.getDate(),
              Number(endParts[0]), Number(endParts[1]), Number(endParts[2])
            )
            if (endDate < startDate) endDate.setDate(endDate.getDate() + 1)
            pausedDuration.value = endDate - startDate
          }
          sessionState.value = SessionState.PAUSED
        } else {
          // STARTED: 通常通りタイマーを開始
          sessionState.value = SessionState.STUDYING
          startTimerTick()
        }

        return true
      }
    } catch (e) {
      console.error(e)
    }
    sessionState.value = SessionState.IDLE
    return false
  }

  const resetSession = () => {
    stopTimerTick()
    sessionState.value = SessionState.IDLE
    currentSubject.value = ''
    currentSubjectColor.value = '#000'
    currentMaterial.value = null
    startTime.value = null
    pausedDuration.value = 0
    studyMemo.value = ''
    memoToSend.value = ''
    timerDisplay.value = '00:00:00'
    showMemoConfirm.value = false
  }

  // 中断中のセッションを再開
  const resumeStudy = async () => {
    // ガード: 中断中でなければ無視
    if (sessionState.value !== SessionState.PAUSED) {
      toastStore.warning('中断中のセッションがありません。')
      return false
    }
    // ガード: ローディング中なら無視
    if (isLoading.value) {
      return false
    }

    playSound('select1')

    if (!userStore.currentUserId) {
      toastStore.error('ユーザーIDが取得できていません')
      return false
    }

    isLoading.value = true
    try {
      const res = await fetch('/api/study/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userStore.currentUserId })
      })
      const json = await res.json()
      if (json.status === 'ok') {
        // 開始時刻を再計算して、タイマーを再開
        if (json.data?.start_time) {
          const startTimeParts = json.data.start_time.split(':')
          const now = new Date()
          const startDate = new Date(
            now.getFullYear(), now.getMonth(), now.getDate(),
            Number(startTimeParts[0]), Number(startTimeParts[1]), Number(startTimeParts[2])
          )
          if (startDate > now) startDate.setDate(startDate.getDate() - 1)
          startTime.value = startDate
        }
        sessionState.value = SessionState.STUDYING
        startTimerTick()
        return true
      } else {
        toastStore.error('再開に失敗しました: ' + (json.message || ''))
      }
    } catch (e) {
      toastStore.error(`通信エラー: ${e.message}`)
    } finally {
      isLoading.value = false
    }
    return false
  }

  return {
    // State
    subjects,
    inSession,
    lastSessionTime,
    currentSubject,
    currentSubjectColor,
    currentMaterial,
    timerDisplay,
    showSubjectModal,
    studyMemo,
    showMemoConfirm,
    memoToSend,
    isLoading,
    // Computed
    isPaused,
    isTimerRunning,
    isConfirming,
    studying, // 後方互換
    // Actions
    openSubjectModal,
    startStudy,
    openMemoConfirm,
    cancelMemoConfirm,
    finishStudy,
    cancelStudy,
    pauseStudy,
    resumeStudy,
    checkActiveSession,
    resetSession
  }
})
