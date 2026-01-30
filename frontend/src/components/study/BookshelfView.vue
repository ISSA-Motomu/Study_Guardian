<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-500 to-indigo-600 p-4 flex justify-between items-center">
        <h2 class="text-white font-bold text-lg">📚 マイ本棚</h2>
        <button @click="emit('close')" class="text-white/80 hover:text-white text-xl">✕</button>
      </div>
      
      <!-- Subject Tabs -->
      <div class="flex overflow-x-auto bg-gray-50 border-b scrollbar-hide">
        <button 
          v-for="subj in subjects" 
          :key="subj.name"
          @click="activeSubject = subj.name"
          :class="[
            'flex-shrink-0 px-4 py-3 font-medium transition-colors text-sm whitespace-nowrap',
            activeSubject === subj.name 
              ? 'text-blue-600 border-b-2 border-blue-500 bg-white' 
              : 'text-gray-500 hover:bg-gray-100'
          ]"
        >
          <span :style="{ color: subj.color }">●</span> {{ subj.name }}
          <span class="ml-1 text-xs text-gray-400">({{ getBookCount(subj.name) }})</span>
        </button>
      </div>
      
      <!-- Content -->
      <div class="p-4 overflow-y-auto" style="max-height: calc(90vh - 180px);">
        <!-- Loading -->
        <div v-if="loading" class="text-center py-8">
          <span class="text-gray-400 animate-pulse">読み込み中...</span>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="filteredBooks.length === 0" class="text-center py-8">
          <div class="text-6xl mb-4">📕</div>
          <p class="text-gray-500">{{ activeSubject }}の本がまだありません</p>
          <button 
            @click="showAddModal = true"
            class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
          >
            + 本を追加する
          </button>
        </div>
        
        <!-- Book Grid -->
        <div v-else class="grid grid-cols-3 gap-3">
          <div 
            v-for="book in filteredBooks" 
            :key="book.book_id"
            class="relative group"
          >
            <!-- Book Cover -->
            <div 
              @click="openBookDetail(book)"
              class="aspect-[3/4] rounded-lg overflow-hidden shadow-md cursor-pointer transition-transform hover:scale-105 bg-gradient-to-br"
              :style="{ background: getBookGradient(book.subject) }"
            >
              <img 
                v-if="book.cover_url"
                :src="book.cover_url" 
                :alt="book.title"
                class="w-full h-full object-cover"
              >
              <div v-else class="w-full h-full flex flex-col items-center justify-center p-2 text-white">
                <span class="text-3xl mb-1">📖</span>
                <span class="text-[10px] text-center font-medium line-clamp-2">{{ book.title }}</span>
              </div>
            </div>
            
            <!-- Book Title -->
            <p class="text-xs text-gray-700 mt-1 truncate font-medium">{{ book.title }}</p>
            <p class="text-[10px] text-gray-400 truncate">{{ book.author || '著者不明' }}</p>
            
            <!-- Progress Bar (if has progress) -->
            <div v-if="book.progress !== undefined" class="mt-1">
              <div class="h-1 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  class="h-full bg-green-500 transition-all"
                  :style="{ width: book.progress + '%' }"
                />
              </div>
              <p class="text-[9px] text-gray-400 text-right">{{ book.progress }}%</p>
            </div>
          </div>
          
          <!-- Add Book Button -->
          <div 
            @click="showAddModal = true"
            class="aspect-[3/4] rounded-lg border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
          >
            <span class="text-2xl text-gray-400">+</span>
            <span class="text-xs text-gray-400">追加</span>
          </div>
        </div>
      </div>
      
      <!-- Add Book Modal -->
      <div v-if="showAddModal" class="absolute inset-0 bg-black/50 flex items-center justify-center p-4">
        <div class="bg-white rounded-xl w-full max-w-sm p-4 shadow-xl">
          <h3 class="font-bold text-lg mb-4">📚 本を追加</h3>
          
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">タイトル *</label>
              <input 
                v-model="newBook.title"
                type="text"
                placeholder="例: 計算ドリル3年生"
                class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none text-sm"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">著者</label>
              <input 
                v-model="newBook.author"
                type="text"
                placeholder="例: 山田太郎"
                class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none text-sm"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">科目</label>
              <select 
                v-model="newBook.subject"
                class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none text-sm"
              >
                <option v-for="subj in subjects" :key="subj.name" :value="subj.name">
                  {{ subj.name }}
                </option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">表紙画像URL (任意)</label>
              <input 
                v-model="newBook.cover_url"
                type="url"
                placeholder="https://..."
                class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none text-sm"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">総ページ数</label>
              <input 
                v-model.number="newBook.total_pages"
                type="number"
                placeholder="100"
                class="w-full p-2.5 border-2 border-gray-200 rounded-lg focus:border-blue-400 focus:outline-none text-sm"
              >
            </div>
          </div>
          
          <div class="flex gap-2 mt-4">
            <button 
              @click="showAddModal = false"
              class="flex-1 py-2.5 rounded-lg border-2 border-gray-200 font-medium text-gray-600"
            >
              キャンセル
            </button>
            <button 
              @click="addBook"
              :disabled="!newBook.title || submitting"
              class="flex-1 py-2.5 rounded-lg bg-blue-500 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? '追加中...' : '追加する' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Book Detail Modal -->
      <div v-if="selectedBook" class="absolute inset-0 bg-black/50 flex items-center justify-center p-4">
        <div class="bg-white rounded-xl w-full max-w-sm p-4 shadow-xl">
          <div class="flex gap-4">
            <!-- Cover -->
            <div 
              class="w-24 h-32 flex-shrink-0 rounded-lg overflow-hidden shadow-md"
              :style="{ background: getBookGradient(selectedBook.subject) }"
            >
              <img 
                v-if="selectedBook.cover_url"
                :src="selectedBook.cover_url" 
                :alt="selectedBook.title"
                class="w-full h-full object-cover"
              >
              <div v-else class="w-full h-full flex items-center justify-center text-white">
                <span class="text-4xl">📖</span>
              </div>
            </div>
            <!-- Info -->
            <div class="flex-1 min-w-0">
              <h3 class="font-bold text-lg text-gray-800 line-clamp-2">{{ selectedBook.title }}</h3>
              <p class="text-sm text-gray-500">{{ selectedBook.author || '著者不明' }}</p>
              <p class="text-xs text-gray-400 mt-1">📚 {{ selectedBook.subject }}</p>
              <p v-if="selectedBook.total_pages" class="text-xs text-gray-400">📄 {{ selectedBook.total_pages }}ページ</p>
            </div>
          </div>
          
          <!-- Progress Update -->
          <div v-if="selectedBook.total_pages" class="mt-4 p-3 bg-gray-50 rounded-lg">
            <label class="block text-sm font-medium text-gray-700 mb-2">進捗を更新</label>
            <div class="flex items-center gap-2">
              <input 
                v-model.number="progressPage"
                type="number"
                :max="selectedBook.total_pages"
                min="0"
                placeholder="現在のページ"
                class="flex-1 p-2 border-2 border-gray-200 rounded-lg text-sm"
              >
              <span class="text-gray-500">/ {{ selectedBook.total_pages }}</span>
            </div>
            <button 
              @click="updateProgress"
              :disabled="!progressPage"
              class="w-full mt-2 py-2 rounded-lg bg-green-500 text-white font-medium disabled:opacity-50"
            >
              進捗を保存
            </button>
          </div>
          
          <div class="flex gap-2 mt-4">
            <button 
              @click="deleteBook(selectedBook.book_id)"
              class="flex-1 py-2.5 rounded-lg border-2 border-red-200 font-medium text-red-600 hover:bg-red-50"
            >
              🗑️ 削除
            </button>
            <button 
              @click="selectedBook = null"
              class="flex-1 py-2.5 rounded-lg bg-gray-100 font-medium text-gray-600"
            >
              閉じる
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useSound } from '@/composables/useSound'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useToastStore } from '@/stores/toast'

const userStore = useUserStore()
const { playSound } = useSound()
const { showConfirm } = useConfirmDialog()
const toast = useToastStore()

const emit = defineEmits(['close'])

// Subject definitions (same as study subjects)
const subjects = [
  { name: '国語', color: '#E57373' },
  { name: '算数', color: '#4FC3F7' },
  { name: '理科', color: '#81C784' },
  { name: '社会', color: '#FFD54F' },
  { name: '英語', color: '#7986CB' },
  { name: 'その他', color: '#90A4AE' }
]

// State
const loading = ref(true)
const books = ref([])
const activeSubject = ref('国語')
const showAddModal = ref(false)
const submitting = ref(false)
const selectedBook = ref(null)
const progressPage = ref(null)

const newBook = ref({
  title: '',
  author: '',
  subject: '国語',
  cover_url: '',
  total_pages: null
})

// Computed
const filteredBooks = computed(() => {
  return books.value.filter(b => b.subject === activeSubject.value)
})

// Functions
const getBookCount = (subject) => {
  return books.value.filter(b => b.subject === subject).length
}

const getBookGradient = (subject) => {
  const subj = subjects.find(s => s.name === subject)
  const color = subj?.color || '#90A4AE'
  return `linear-gradient(135deg, ${color} 0%, ${color}AA 100%)`
}

const fetchBooks = async () => {
  if (!userStore.currentUserId) return
  loading.value = true
  try {
    const res = await fetch(`/api/bookshelf/${userStore.currentUserId}`)
    const data = await res.json()
    if (data.status === 'ok') {
      books.value = data.books || []
    }
  } catch (e) {
    console.error('Failed to fetch books:', e)
  } finally {
    loading.value = false
  }
}

const addBook = async () => {
  if (!newBook.value.title || submitting.value) return
  
  submitting.value = true
  try {
    const res = await fetch('/api/bookshelf/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.currentUserId,
        ...newBook.value
      })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      playSound('success')
      showAddModal.value = false
      newBook.value = { title: '', author: '', subject: activeSubject.value, cover_url: '', total_pages: null }
      await fetchBooks()
    } else {
      toast.error('追加に失敗しました: ' + (data.message || ''))
    }
  } catch (e) {
    console.error('Add book error:', e)
    toast.error('追加に失敗しました')
  } finally {
    submitting.value = false
  }
}

const openBookDetail = (book) => {
  playSound('click')
  selectedBook.value = book
  progressPage.value = book.current_page || 0
}

const updateProgress = async () => {
  if (!selectedBook.value || !progressPage.value) return
  
  try {
    const res = await fetch(`/api/bookshelf/${selectedBook.value.book_id}/progress`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.currentUserId,
        current_page: progressPage.value
      })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      playSound('success')
      selectedBook.value = null
      await fetchBooks()
    } else {
      toast.error('更新に失敗しました')
    }
  } catch (e) {
    console.error('Update progress error:', e)
    toast.error('更新に失敗しました')
  }
}

const deleteBook = async (bookId) => {
  const confirmed = await showConfirm({
    type: 'danger',
    title: '本の削除',
    message: 'この本を本棚から削除しますか？\n読書記録も一緒に削除されます。',
    confirmText: '削除する',
    cancelText: 'キャンセル',
    icon: '📕'
  })
  if (!confirmed) return
  
  try {
    const res = await fetch(`/api/bookshelf/${bookId}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userStore.currentUserId })
    })
    const data = await res.json()
    if (data.status === 'ok') {
      playSound('click')
      selectedBook.value = null
      await fetchBooks()
    } else {
      toast.error('削除に失敗しました')
    }
  } catch (e) {
    console.error('Delete book error:', e)
    toast.error('削除に失敗しました')
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
