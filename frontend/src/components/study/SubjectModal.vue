<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center px-6">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden animate-fadeInUp">
        <!-- Header -->
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 p-4">
          <h3 class="text-white font-bold text-lg text-center">📚 科目を選択</h3>
        </div>

        <!-- Subject List -->
        <div class="p-4 max-h-80 overflow-y-auto">
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="(color, subject) in studyStore.subjects"
              :key="subject"
              @click="selectSubject(subject)"
              :disabled="studyStore.studying"
              class="p-4 rounded-xl border-2 font-medium text-center transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
              :style="{ 
                borderColor: color, 
                backgroundColor: color + '20',
                color: color
              }"
            >
              {{ subject }}
            </button>
          </div>

          <!-- Loading state -->
          <div v-if="Object.keys(studyStore.subjects).length === 0" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-4 border-indigo-300 border-t-indigo-600 mx-auto" />
            <p class="mt-2 text-gray-500">科目を読み込み中...</p>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t">
          <button
            @click="emit('close')"
            class="w-full py-3 text-gray-600 font-medium"
          >
            キャンセル
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useStudyStore } from '@/stores/study'

const studyStore = useStudyStore()

const emit = defineEmits(['close', 'start'])

const selectSubject = (subject) => {
  emit('start', subject)
}
</script>
