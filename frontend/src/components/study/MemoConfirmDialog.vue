<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center px-6">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-fadeInUp">
        <!-- Header -->
        <div class="bg-gradient-to-r from-green-500 to-emerald-600 p-4">
          <h3 class="text-white font-bold text-lg text-center">📝 勉強内容の確認</h3>
        </div>

        <!-- Content -->
        <div class="p-6">
          <div class="bg-gray-50 rounded-xl p-4 min-h-[100px]">
            <p class="text-gray-700 whitespace-pre-wrap">
              {{ memo || '(メモなし)' }}
            </p>
          </div>
          
          <p class="text-center text-gray-500 text-sm mt-4">
            この内容で記録を終了しますか？
          </p>
        </div>

        <!-- Actions -->
        <div class="p-4 border-t flex gap-3">
          <button
            @click="handleCancel"
            class="flex-1 py-3 bg-gray-200 text-gray-700 rounded-xl font-medium transition-colors hover:bg-gray-300 active:bg-gray-400"
          >
            戻る
          </button>
          <button
            @click="handleConfirm"
            class="flex-1 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl font-bold transition-transform hover:scale-105 active:scale-95"
          >
            記録して終了
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useSound } from '@/composables/useSound'

const props = defineProps({
  memo: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['confirm', 'cancel'])
const { playSound } = useSound()

const handleConfirm = () => {
  playSound('select2')
  emit('confirm')
}

const handleCancel = () => {
  playSound('click')
  emit('cancel')
}
</script>
