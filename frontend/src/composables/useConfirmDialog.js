import { ref, reactive } from 'vue'

const state = reactive({
  show: false,
  type: 'info',
  title: '確認',
  message: '',
  confirmText: 'はい',
  cancelText: 'キャンセル',
  icon: '',
  confirmIcon: '',
  onConfirm: null,
  onCancel: null
})

export function useConfirmDialog() {
  const showConfirm = ({
    type = 'info',
    title = '確認',
    message = 'この操作を実行しますか？',
    confirmText = 'はい',
    cancelText = 'キャンセル',
    icon = '',
    confirmIcon = ''
  } = {}) => {
    return new Promise((resolve) => {
      state.type = type
      state.title = title
      state.message = message
      state.confirmText = confirmText
      state.cancelText = cancelText
      state.icon = icon
      state.confirmIcon = confirmIcon
      state.onConfirm = () => resolve(true)
      state.onCancel = () => resolve(false)
      state.show = true
    })
  }

  const closeDialog = () => {
    state.show = false
  }

  const handleConfirm = () => {
    if (state.onConfirm) state.onConfirm()
    closeDialog()
  }

  const handleCancel = () => {
    if (state.onCancel) state.onCancel()
    closeDialog()
  }

  return {
    state,
    showConfirm,
    closeDialog,
    handleConfirm,
    handleCancel
  }
}

// Shortcut functions
export async function confirmInfo(message, title = '確認') {
  const { showConfirm } = useConfirmDialog()
  return showConfirm({ type: 'info', title, message })
}

export async function confirmWarning(message, title = '注意') {
  const { showConfirm } = useConfirmDialog()
  return showConfirm({ type: 'warning', title, message, icon: '⚠️' })
}

export async function confirmDanger(message, title = '削除確認') {
  const { showConfirm } = useConfirmDialog()
  return showConfirm({ type: 'danger', title, message, confirmText: '削除する', icon: '🗑️' })
}

export async function confirmSuccess(message, title = '完了確認') {
  const { showConfirm } = useConfirmDialog()
  return showConfirm({ type: 'success', title, message, confirmText: '完了！', icon: '🎉' })
}
