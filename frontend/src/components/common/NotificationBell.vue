<template>
  <div class="relative">
    <!-- Notification Bell -->
    <button 
      @click="showDropdown = !showDropdown"
      class="relative p-2 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
    >
      <span class="text-xl">🔔</span>
      <!-- Badge -->
      <span 
        v-if="notificationStore.unreadCount > 0"
        class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-[10px] font-bold animate-bounce"
      >
        {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
      </span>
    </button>

    <!-- Dropdown -->
    <transition name="fade-slide">
      <div 
        v-if="showDropdown"
        class="absolute right-0 top-full mt-2 w-80 max-h-96 overflow-y-auto bg-white rounded-2xl shadow-2xl border border-gray-200 z-50"
      >
        <!-- Header -->
        <div class="sticky top-0 bg-white p-4 border-b border-gray-100 flex justify-between items-center">
          <h3 class="font-bold text-gray-800">🔔 通知</h3>
          <button 
            v-if="notificationStore.notifications.length > 0"
            @click="notificationStore.markAllAsRead()"
            class="text-xs text-blue-500 hover:text-blue-700"
          >
            すべて既読
          </button>
        </div>

        <!-- Notification List -->
        <div v-if="notificationStore.notifications.length === 0" class="p-8 text-center text-gray-400">
          <span class="text-4xl block mb-2">📭</span>
          <p>通知はありません</p>
        </div>

        <div v-else class="divide-y divide-gray-100">
          <div 
            v-for="notification in notificationStore.notifications"
            :key="notification.id"
            @click="handleNotificationClick(notification)"
            :class="[
              'p-4 hover:bg-gray-50 cursor-pointer transition-colors',
              !notification.read && 'bg-blue-50'
            ]"
          >
            <div class="flex items-start gap-3">
              <span class="text-2xl">{{ notification.icon || '📌' }}</span>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-800 text-sm">{{ notification.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ notification.message }}</p>
                <p class="text-[10px] text-gray-400 mt-2">{{ formatTime(notification.timestamp) }}</p>
              </div>
              <span 
                v-if="!notification.read"
                class="w-2 h-2 bg-blue-500 rounded-full mt-1"
              />
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div v-if="notificationStore.notifications.length > 0" class="p-3 border-t border-gray-100">
          <button 
            @click="notificationStore.clearAll()"
            class="w-full text-center text-xs text-gray-400 hover:text-red-500"
          >
            すべてクリア
          </button>
        </div>
      </div>
    </transition>

    <!-- Backdrop -->
    <div 
      v-if="showDropdown"
      class="fixed inset-0 z-40"
      @click="showDropdown = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()
const showDropdown = ref(false)

const emit = defineEmits(['navigate'])

const handleNotificationClick = (notification) => {
  notificationStore.markAsRead(notification.id)
  
  // 通知タイプに応じてナビゲーション
  if (notification.type === 'pending') {
    emit('navigate', 'admin')
  }
  
  showDropdown.value = false
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = Math.floor((now - date) / 1000)
  
  if (diff < 60) return 'たった今'
  if (diff < 3600) return `${Math.floor(diff / 60)}分前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}時間前`
  return `${Math.floor(diff / 86400)}日前`
}

onMounted(() => {
  notificationStore.startPolling()
})

onUnmounted(() => {
  notificationStore.stopPolling()
})
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
