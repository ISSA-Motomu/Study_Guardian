<template>
  <div class="space-y-4 mt-8">
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-bold text-white">⚙️ 管理者メニュー</h2>
      <button
        @click="emit('exit')"
        class="text-white/70 hover:text-white"
      >
        ✕ 閉じる
      </button>
    </div>

    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">📋 承認待ち</h3>
      <div v-if="pendingItems.length === 0" class="text-gray-500 text-center py-4">
        承認待ちの項目はありません
      </div>
      <div v-else class="space-y-2">
        <div 
          v-for="item in pendingItems" 
          :key="item.id"
          class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
        >
          <div>
            <p class="font-medium">{{ item.title }}</p>
            <p class="text-xs text-gray-500">{{ item.user }} - {{ item.date }}</p>
          </div>
          <div class="flex gap-2">
            <button
              @click="approve(item)"
              class="bg-green-500 text-white px-3 py-1 rounded text-sm"
            >
              承認
            </button>
            <button
              @click="reject(item)"
              class="bg-red-500 text-white px-3 py-1 rounded text-sm"
            >
              却下
            </button>
          </div>
        </div>
      </div>
    </GlassPanel>

    <GlassPanel>
      <h3 class="font-bold text-gray-700 mb-4">👥 ユーザー管理</h3>
      <p class="text-gray-500 text-sm">準備中...</p>
    </GlassPanel>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import GlassPanel from '@/components/common/GlassPanel.vue'

const emit = defineEmits(['exit'])

const pendingItems = ref([])

const approve = (item) => {
  console.log('Approve:', item)
  // TODO: API call
}

const reject = (item) => {
  console.log('Reject:', item)
  // TODO: API call
}
</script>
