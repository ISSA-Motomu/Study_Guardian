import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useUserStore } from './user'
import { useSound } from '@/composables/useSound'

export const useShopStore = defineStore('shop', () => {
  const userStore = useUserStore()
  const { playSound } = useSound()

  // State
  const shopItems = ref([])
  const selectedItem = ref(null)
  const showBuyModal = ref(false)
  const loading = ref(false)

  // Actions
  const fetchItems = async () => {
    loading.value = true
    try {
      const res = await fetch('/api/shop/items')
      const json = await res.json()
      if (json.status === 'ok') {
        shopItems.value = json.data
      } else {
        alert('ショップ情報の取得に失敗しました')
      }
    } catch (e) {
      console.error(e)
      alert('通信エラー')
    } finally {
      loading.value = false
    }
  }

  const openBuyModal = (item) => {
    selectedItem.value = item
    showBuyModal.value = true
  }

  const confirmBuy = async (comment) => {
    if (!selectedItem.value) return

    if ((userStore.user.xp || 0) < selectedItem.value.cost) {
      alert('XPが足りません！')
      return
    }

    playSound('select3')
    try {
      const res = await fetch('/api/shop/buy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.currentUserId,
          item_key: selectedItem.value.key,
          comment: comment
        })
      })
      const json = await res.json()
      if (json.status === 'ok') {
        alert('購入リクエストを送りました！\n親の承認をお待ちください。')
        showBuyModal.value = false
        await userStore.fetchUserData(userStore.currentUserId)
      } else {
        alert('購入エラー: ' + json.message)
      }
    } catch (e) {
      alert('通信エラー')
    }
  }

  return {
    // State
    shopItems,
    selectedItem,
    showBuyModal,
    loading,
    // Actions
    fetchItems,
    openBuyModal,
    confirmBuy
  }
})
