<template>
  <div class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-500 to-emerald-600 p-4 flex justify-between items-center">
        <h2 class="text-white font-bold text-lg">📖 マイ教材</h2>
        <button @click="emit('close')" class="text-white/80 hover:text-white text-xl">✕</button>
      </div>
      
      <!-- Tabs -->
      <div class="flex border-b">
        <button 
          @click="activeTab = 'list'"
          :class="['flex-1 py-3 font-medium transition-colors', activeTab === 'list' ? 'text-green-600 border-b-2 border-green-500' : 'text-gray-500']"
        >
          📚 教材一覧
        </button>
        <button 
          @click="activeTab = 'add'"
          :class="['flex-1 py-3 font-medium transition-colors', activeTab === 'add' ? 'text-green-600 border-b-2 border-green-500' : 'text-gray-500']"
        >
          ➕ 新規登録
        </button>
      </div>
      
      <!-- Content -->
      <div class="p-4 overflow-y-auto" style="max-height: calc(90vh - 140px);">
        <!-- Material List -->
        <div v-if="activeTab === 'list'">
          <div v-if="loading" class="text-center py-8">
            <span class="text-gray-400 animate-pulse">読み込み中...</span>
          </div>
          
          <div v-else-if="materials.length === 0" class="text-center py-8">
            <span class="text-6xl">📖</span>
            <p class="text-gray-500 mt-4">教材がまだ登録されていません</p>
            <button 
              @click="activeTab = 'add'"
              class="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg font-medium"
            >
              教材を登録する
            </button>
          </div>
          
          <div v-else class="space-y-3">
            <div 
              v-for="mat in materials" 
              :key="mat.material_id"
              class="flex gap-3 p-3 bg-gray-50 rounded-xl border border-gray-100"
            >
              <!-- Image -->
              <div class="w-16 h-20 flex-shrink-0 rounded-lg overflow-hidden bg-gray-200">
                <img 
                  v-if="mat.image_url"
                  :src="mat.image_url" 
                  :alt="mat.name"
                  class="w-full h-full object-cover"
                >
                <div v-else class="w-full h-full flex items-center justify-center text-2xl">
                  📕
                </div>
              </div>
              <!-- Info -->
              <div class="flex-1 min-w-0">
                <h4 class="font-bold text-gray-800 truncate">{{ mat.name }}</h4>
                <p class="text-xs text-gray-500">{{ mat.subject }}</p>
                <p v-if="mat.description" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ mat.description }}</p>
                <p class="text-[10px] text-gray-400 mt-1">登録日: {{ formatDate(mat.created_at) }}</p>
              </div>
              <!-- Delete -->
              <button 
                @click="deleteMaterial(mat.material_id)"
                class="text-red-400 hover:text-red-600 self-start"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
        
        <!-- Add Material Form -->
        <div v-if="activeTab === 'add'" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">教材名 *</label>
            <input 
              v-model="newMaterial.name"
              type="text"
              placeholder="例: 計算ドリル3年生"
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-green-400 focus:outline-none"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">科目</label>
            <select 
              v-model="newMaterial.subject"
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-green-400 focus:outline-none"
            >
              <option value="">選択してください</option>
              <option value="国語">国語</option>
              <option value="数学">数学</option>
              <option value="英語">英語</option>
              <option value="理科">理科</option>
              <option value="社会">社会</option>
              <option value="その他">その他</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">説明（任意）</label>
            <textarea 
              v-model="newMaterial.description"
              placeholder="教材の内容や目標など"
              rows="2"
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-green-400 focus:outline-none resize-none"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">画像URL（任意）</label>
            <input 
              v-model="newMaterial.image_url"
              type="url"
              placeholder="https://..."
              class="w-full p-3 border-2 border-gray-200 rounded-xl focus:border-green-400 focus:outline-none"
            >
            <p class="text-xs text-gray-400 mt-1">※ 画像アップロード機能は今後追加予定</p>
          </div>
          
          <!-- Image Preview -->
          <div v-if="newMaterial.image_url" class="text-center">
            <img 
              :src="newMaterial.image_url" 
              alt="Preview"
              class="w-24 h-32 object-cover rounded-lg mx-auto border"
              @error="newMaterial.image_url = ''"
            >
          </div>
          
          <button 
            @click="addMaterial"
            :disabled="!newMaterial.name || submitting"
            class="w-full py-3 bg-green-500 text-white font-bold rounded-xl disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-green-600 transition-colors"
          >
            {{ submitting ? '登録中...' : '📖 教材を登録' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useCache, CACHE_KEYS } from '@/composables/useCache'

const emit = defineEmits(['close'])
const userStore = useUserStore()
const { getCache, setCache, clearCache } = useCache()

const activeTab = ref('list')
const loading = ref(true)
const submitting = ref(false)
const materials = ref([])

const newMaterial = ref({
  name: '',
  subject: '',
  description: '',
  image_url: ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    return dateStr.split(' ')[0]
  } catch {
    return dateStr
  }
}

const fetchMaterials = async () => {
  // Check cache first
  const cacheKey = CACHE_KEYS.MATERIALS(userStore.currentUserId)
  const cached = getCache(cacheKey)
  if (cached) {
    materials.value = cached
    loading.value = false
    return
  }

  loading.value = true
  try {
    const res = await fetch(`/api/materials/user/${userStore.currentUserId}`)
    const data = await res.json()
    if (data.status === 'ok') {
      materials.value = data.materials || []
      // Cache for 5 minutes
      setCache(cacheKey, materials.value, 5 * 60 * 1000)
    }
  } catch (e) {
    console.error('Failed to fetch materials:', e)
  } finally {
    loading.value = false
  }
}

const addMaterial = async () => {
  if (!newMaterial.value.name || submitting.value) return
  submitting.value = true
  
  try {
    const res = await fetch('/api/materials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.currentUserId,
        name: newMaterial.value.name,
        subject: newMaterial.value.subject,
        description: newMaterial.value.description,
        image_url: newMaterial.value.image_url
      })
    })
    const data = await res.json()
    
    if (data.status === 'ok') {
      alert('教材を登録しました！')
      newMaterial.value = { name: '', subject: '', description: '', image_url: '' }
      activeTab.value = 'list'
      // Clear cache and refetch
      clearCache(CACHE_KEYS.MATERIALS(userStore.currentUserId))
      await fetchMaterials()
    } else {
      alert(data.message || '登録に失敗しました')
    }
  } catch (e) {
    console.error('Failed to add material:', e)
    alert('エラーが発生しました')
  } finally {
    submitting.value = false
  }
}

const deleteMaterial = async (materialId) => {
  if (!confirm('この教材を削除しますか？')) return
  
  try {
    const res = await fetch(`/api/materials/${materialId}?user_id=${userStore.currentUserId}`, {
      method: 'DELETE'
    })
    const data = await res.json()
    
    if (data.status === 'ok') {
      materials.value = materials.value.filter(m => m.material_id !== materialId)
      // Clear cache
      clearCache(CACHE_KEYS.MATERIALS(userStore.currentUserId))
    } else {
      alert(data.message || '削除に失敗しました')
    }
  } catch (e) {
    console.error('Failed to delete material:', e)
  }
}

onMounted(() => {
  fetchMaterials()
})
</script>
