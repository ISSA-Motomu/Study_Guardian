<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center px-6">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-fadeInUp max-h-[80vh] flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-amber-500 to-orange-500 p-4 shrink-0">
          <h3 class="text-white font-bold text-lg text-center">🏪 ショップ</h3>
        </div>

        <!-- Content -->
        <div class="p-4 overflow-y-auto flex-1">
          <div v-if="shopStore.loading" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-4 border-amber-300 border-t-amber-600 mx-auto" />
            <p class="mt-2 text-gray-500">読み込み中...</p>
          </div>

          <div v-else-if="shopStore.shopItems.length === 0" class="text-center text-gray-500 py-8">
            商品がありません
          </div>

          <div v-else class="space-y-3">
            <button
              v-for="item in shopStore.shopItems"
              :key="item.key"
              @click="shopStore.openBuyModal(item)"
              class="w-full bg-white border border-gray-200 rounded-xl p-3 flex items-center gap-4 transition-all hover:shadow-md active:scale-95 text-left"
            >
              <span class="text-3xl">{{ item.icon }}</span>
              <div class="flex-1">
                <p class="font-bold text-gray-800">{{ item.name }}</p>
                <p class="text-xs text-gray-500">{{ item.description }}</p>
              </div>
              <div class="text-amber-600 font-bold whitespace-nowrap">
                {{ item.cost }} XP
              </div>
            </button>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t shrink-0">
          <button
            @click="emit('close')"
            class="w-full py-3 bg-gray-100 text-gray-600 rounded-xl font-medium transition-colors hover:bg-gray-200"
          >
            閉じる
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useShopStore } from '@/stores/shop'

const shopStore = useShopStore()
const emit = defineEmits(['close'])
</script>
