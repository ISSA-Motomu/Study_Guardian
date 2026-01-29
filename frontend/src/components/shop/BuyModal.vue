<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center px-6">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-fadeInUp">
        <!-- Header -->
        <div class="bg-gradient-to-r from-amber-500 to-orange-500 p-4">
          <h3 class="text-white font-bold text-lg text-center">🛒 購入確認</h3>
        </div>

        <!-- Item Details -->
        <div class="p-6 text-center">
          <p class="text-4xl mb-2">{{ item?.icon }}</p>
          <h4 class="text-xl font-bold text-gray-800">{{ item?.name }}</h4>
          <p class="text-amber-600 font-bold text-lg mt-2">
            {{ item?.cost }} XP
          </p>
        </div>

        <!-- Comment Input -->
        <div class="px-6 pb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            💬 コメント (任意)
          </label>
          <input
            v-model="comment"
            type="text"
            class="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-amber-500 focus:border-transparent"
            placeholder="親へのメッセージ..."
          >
        </div>

        <!-- Actions -->
        <div class="p-4 border-t flex gap-3">
          <button
            @click="emit('cancel')"
            class="flex-1 py-3 bg-gray-200 text-gray-700 rounded-xl font-medium"
          >
            キャンセル
          </button>
          <button
            @click="handleConfirm"
            class="flex-1 py-3 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl font-bold"
          >
            購入申請
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  item: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['confirm', 'cancel'])
const comment = ref('')

const handleConfirm = () => {
  emit('confirm', comment.value)
  comment.value = ''
}
</script>
