<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center px-4">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fadeInUp max-h-[85vh] flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 flex-shrink-0">
          <h3 class="text-white font-bold text-lg text-center">📚 勉強を始める</h3>
        </div>

        <!-- Tab Selector -->
        <div class="flex border-b bg-gray-50 flex-shrink-0">
          <button
            @click="activeTab = 'subject'"
            :class="[
              'flex-1 py-3 font-medium text-sm transition-colors',
              activeTab === 'subject'
                ? 'text-indigo-600 border-b-2 border-indigo-500 bg-white'
                : 'text-gray-500 hover:bg-gray-100'
            ]"
          >
            📝 科目から選ぶ
          </button>
          <button
            @click="activeTab = 'bookshelf'; loadBooks()"
            :class="[
              'flex-1 py-3 font-medium text-sm transition-colors',
              activeTab === 'bookshelf'
                ? 'text-indigo-600 border-b-2 border-indigo-500 bg-white'
                : 'text-gray-500 hover:bg-gray-100'
            ]"
          >
            📚 本棚から選ぶ
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-4">
          <!-- Subject Selection Tab -->
          <div v-if="activeTab === 'subject'">
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

          <!-- Bookshelf Tab -->
          <div v-if="activeTab === 'bookshelf'">
            <!-- Subject Filter Tabs -->
            <div class="flex overflow-x-auto -mx-4 px-4 pb-3 mb-3 border-b scrollbar-hide">
              <button 
                @click="selectedSubjectFilter = ''"
                :class="[
                  'flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium mr-2 transition-colors',
                  selectedSubjectFilter === ''
                    ? 'bg-indigo-500 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                ]"
              >
                すべて
              </button>
              <button 
                v-for="subj in subjectList" 
                :key="subj.name"
                @click="selectedSubjectFilter = subj.name"
                :class="[
                  'flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium mr-2 transition-colors',
                  selectedSubjectFilter === subj.name
                    ? 'text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                ]"
                :style="selectedSubjectFilter === subj.name ? { backgroundColor: subj.color } : {}"
              >
                {{ subj.name }} ({{ getBookCount(subj.name) }})
              </button>
            </div>

            <!-- Loading -->
            <div v-if="loadingBooks" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-4 border-indigo-300 border-t-indigo-600 mx-auto" />
              <p class="mt-2 text-gray-500">本棚を読み込み中...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="filteredBooks.length === 0" class="text-center py-8">
              <div class="text-5xl mb-3">📕</div>
              <p class="text-gray-500 text-sm">
                {{ selectedSubjectFilter ? `${selectedSubjectFilter}の教材がありません` : '本棚に教材がありません' }}
              </p>
              <p class="text-gray-400 text-xs mt-1">本棚から教材を追加してね</p>
            </div>

            <!-- Book Grid -->
            <div v-else class="grid grid-cols-2 gap-3">
              <div 
                v-for="book in filteredBooks" 
                :key="book.book_id"
                @click="selectBook(book)"
                class="bg-gray-50 rounded-xl p-3 cursor-pointer transition-all hover:bg-indigo-50 hover:scale-[1.02] active:scale-95 border-2 border-transparent hover:border-indigo-300"
              >
                <div class="flex gap-3">
                  <!-- Mini Cover -->
                  <div 
                    class="w-12 h-16 flex-shrink-0 rounded-lg overflow-hidden shadow-sm"
                    :style="{ background: getBookGradient(book.subject) }"
                  >
                    <img 
                      v-if="book.cover_url"
                      :src="book.cover_url" 
                      :alt="book.title"
                      class="w-full h-full object-cover"
                    >
                    <div v-else class="w-full h-full flex items-center justify-center text-white text-lg">
                      📖
                    </div>
                  </div>
                  <!-- Info -->
                  <div class="flex-1 min-w-0">
                    <p class="font-medium text-sm text-gray-800 line-clamp-2">{{ book.title }}</p>
                    <p class="text-xs text-gray-400 mt-0.5">{{ book.author || '著者不明' }}</p>
                    <span 
                      class="inline-block px-2 py-0.5 rounded-full text-[10px] mt-1 text-white"
                      :style="{ backgroundColor: getSubjectColor(book.subject) }"
                    >
                      {{ book.subject }}
                    </span>
                  </div>
                </div>
                <!-- Progress -->
                <div v-if="book.progress !== undefined && book.progress > 0" class="mt-2">
                  <div class="flex justify-between text-[10px] text-gray-400 mb-0.5">
                    <span>進捗</span>
                    <span>{{ book.progress }}%</span>
                  </div>
                  <div class="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      class="h-full bg-green-500 transition-all"
                      :style="{ width: book.progress + '%' }"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="p-4 border-t flex-shrink-0">
          <button
            @click="emit('close')"
            class="w-full py-3 text-gray-600 font-medium hover:bg-gray-100 rounded-xl transition-colors"
          >
            キャンセル
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStudyStore } from '@/stores/study'
import { useUserStore } from '@/stores/user'

const studyStore = useStudyStore()
const userStore = useUserStore()

const emit = defineEmits(['close', 'start'])

// State
const activeTab = ref('subject')
const books = ref([])
const loadingBooks = ref(false)
const selectedSubjectFilter = ref('')

// Subject list with colors
const subjectList = [
  { name: '国語', color: '#EF5350' },
  { name: '数学', color: '#42A5F5' },
  { name: '理科', color: '#66BB6A' },
  { name: '社会', color: '#AB47BC' },
  { name: '英語', color: '#7986CB' },
  { name: 'その他', color: '#90A4AE' }
]

// Computed
const filteredBooks = computed(() => {
  if (!selectedSubjectFilter.value) {
    return books.value
  }
  return books.value.filter(b => b.subject === selectedSubjectFilter.value)
})

// Methods
const getBookCount = (subject) => {
  return books.value.filter(b => b.subject === subject).length
}

const getSubjectColor = (subject) => {
  const subj = subjectList.find(s => s.name === subject)
  return subj?.color || '#90A4AE'
}

const getBookGradient = (subject) => {
  const color = getSubjectColor(subject)
  return `linear-gradient(135deg, ${color} 0%, ${color}AA 100%)`
}

const loadBooks = async () => {
  if (books.value.length > 0) return // Already loaded
  if (!userStore.currentUserId) return
  
  loadingBooks.value = true
  try {
    const res = await fetch(`/api/bookshelf/${userStore.currentUserId}`)
    const json = await res.json()
    if (json.status === 'ok') {
      books.value = json.books || []
    }
  } catch (e) {
    console.error('Failed to load books:', e)
  } finally {
    loadingBooks.value = false
  }
}

const selectSubject = (subject) => {
  emit('start', { subject, material: null })
}

const selectBook = (book) => {
  emit('start', { subject: book.subject, material: book })
}

// Initialize
onMounted(() => {
  // Pre-load books in background
  loadBooks()
})
</script>
