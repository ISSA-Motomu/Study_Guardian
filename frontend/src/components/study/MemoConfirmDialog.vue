<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[9999] flex items-center justify-center px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fadeInUp max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-green-500 to-emerald-600 p-4 flex-shrink-0">
          <h3 class="text-white font-bold text-lg text-center">🧠 学習の振り返り</h3>
          <p class="text-green-100 text-xs text-center mt-1">ファインマンテクニックで記憶定着！</p>
        </div>

        <!-- Scrollable Content -->
        <div class="p-4 overflow-y-auto flex-1">
          <!-- Feynman Technique Explanation -->
          <div class="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-4">
            <div class="flex items-start gap-2">
              <span class="text-xl">💡</span>
              <div class="text-xs text-amber-800">
                <p class="font-bold mb-1">ファインマンテクニックとは？</p>
                <p>学んだことを「誰かに教えるように」説明することで、理解度が格段にアップ！自分の言葉で書いてみよう。</p>
              </div>
            </div>
          </div>

          <!-- Learning Reflection Input -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-gray-700 mb-2">
              📝 今日学んだことを説明してね
            </label>
            <textarea
              v-model="learningReflection"
              class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm resize-none"
              rows="3"
              placeholder="例：因数分解は、式をかけ算の形に分解すること。x²+5x+6は(x+2)(x+3)になる！"
            ></textarea>
          </div>

          <!-- Quick Select Tags -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-gray-700 mb-2">
              🏷️ 理解度はどのくらい？
            </label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="level in understandingLevels"
                :key="level.value"
                @click="selectedUnderstanding = level.value"
                class="px-3 py-1.5 rounded-full text-xs font-medium transition-all"
                :class="selectedUnderstanding === level.value 
                  ? 'bg-emerald-500 text-white scale-105' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
              >
                {{ level.emoji }} {{ level.label }}
              </button>
            </div>
          </div>

          <!-- What to Review Next -->
          <div class="mb-4">
            <label class="block text-sm font-bold text-gray-700 mb-2">
              🔄 次回復習したいこと（任意）
            </label>
            <input
              v-model="reviewNote"
              type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm"
              placeholder="例：公式の導出をもう一度確認"
            />
          </div>

          <!-- Original Memo Display (Collapsed) -->
          <div v-if="memo" class="mb-4">
            <button 
              @click="showOriginalMemo = !showOriginalMemo"
              class="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
            >
              <span>{{ showOriginalMemo ? '▼' : '▶' }}</span>
              勉強中のメモを見る
            </button>
            <div v-if="showOriginalMemo" class="mt-2 bg-gray-50 rounded-lg p-3">
              <p class="text-gray-600 text-xs whitespace-pre-wrap">{{ memo }}</p>
            </div>
          </div>

          <!-- Gem Bonus Hint -->
          <div class="bg-purple-50 border border-purple-200 rounded-xl p-3">
            <div class="flex items-center gap-2">
              <span class="text-lg">💎</span>
              <p class="text-xs text-purple-700">
                <span class="font-bold">ボーナス！</span>
                振り返りを書くと、勉強石が+1もらえるよ！
              </p>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="p-4 border-t flex gap-3 flex-shrink-0">
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
            記録完了 ✨
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useSound } from '@/composables/useSound'

const props = defineProps({
  memo: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['confirm', 'cancel'])
const { playSound } = useSound()

// State
const learningReflection = ref('')
const selectedUnderstanding = ref(null)
const reviewNote = ref('')
const showOriginalMemo = ref(false)

// Understanding levels
const understandingLevels = [
  { value: 'perfect', emoji: '🌟', label: 'バッチリ！' },
  { value: 'good', emoji: '😊', label: 'だいたいOK' },
  { value: 'partial', emoji: '🤔', label: '半分くらい' },
  { value: 'confused', emoji: '😵', label: 'まだ難しい' }
]

const handleConfirm = () => {
  playSound('select2')
  
  // Combine reflection data
  const reflectionData = {
    reflection: learningReflection.value,
    understanding: selectedUnderstanding.value,
    reviewNote: reviewNote.value,
    hasReflection: learningReflection.value.trim().length > 0
  }
  
  emit('confirm', reflectionData)
}

const handleCancel = () => {
  playSound('click')
  emit('cancel')
}
</script>
