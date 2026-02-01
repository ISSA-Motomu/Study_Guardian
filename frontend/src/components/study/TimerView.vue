<template>
  <div class="space-y-6 mt-8">
    <!-- Timer Display -->
    <GlassPanel class="text-center py-8">
      <p class="text-6xl font-mono font-bold text-indigo-700 tracking-wider">
        {{ studyStore.timerDisplay }}
      </p>
      <p class="mt-2 text-gray-600">
        <span 
          class="inline-block px-3 py-1 rounded-full text-sm font-medium text-white"
          :style="{ backgroundColor: studyStore.currentSubjectColor }"
        >
          {{ studyStore.currentSubject }}
        </span>
      </p>
      <!-- Material Info -->
      <p v-if="studyStore.currentMaterial" class="mt-2 text-sm text-gray-500">
        📚 {{ studyStore.currentMaterial.title }}
      </p>
    </GlassPanel>

    <!-- Memo Input -->
    <GlassPanel>
      <label class="block text-sm font-medium text-gray-700 mb-2">
        📝 勉強メモ
      </label>
      <textarea
        v-model="studyStore.studyMemo"
        class="w-full h-24 p-3 border border-gray-200 rounded-lg resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
        placeholder="今日の勉強内容を記録しよう..."
      />
    </GlassPanel>

    <!-- Control Buttons -->
    <div class="grid grid-cols-2 gap-4">
      <button
        @click="handleFinish"
        class="bg-gradient-to-r from-green-500 to-emerald-600 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all active:scale-95"
      >
        ✓ 記録して終了
      </button>
      <button
        @click="handlePause"
        class="bg-gradient-to-r from-amber-500 to-orange-500 text-white py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all active:scale-95"
      >
        ⏸️ 一時中断
      </button>
    </div>

    <!-- Secondary Actions -->
    <div class="flex justify-center gap-4">
      <button
        @click="handleCancel"
        class="text-red-500 underline text-sm"
      >
        記録を取り消す
      </button>
      <button
        @click="emit('back')"
        class="text-gray-500 underline text-sm"
      >
        戻る
      </button>
    </div>
  </div>
</template>

<script setup>
import { useStudyStore } from '@/stores/study'
import GlassPanel from '@/components/common/GlassPanel.vue'

const studyStore = useStudyStore()

const emit = defineEmits(['back'])

const handleFinish = () => {
  studyStore.openMemoConfirm()
}

const handlePause = async () => {
  const success = await studyStore.pauseStudy()
  if (success) {
    emit('back')
  }
}

const handleCancel = async () => {
  await studyStore.cancelStudy()
  emit('back')
}
</script>
