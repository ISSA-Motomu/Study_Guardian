<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center overflow-hidden">
    <!-- 背景グラデーション -->
    <div class="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500">
      <!-- 流れる装飾 -->
      <div class="absolute inset-0 opacity-30">
        <div class="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
        <div class="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>
      </div>
    </div>
    
    <!-- メインコンテンツ -->
    <div class="relative text-center px-8">
      <!-- ロゴ/アイコン -->
      <div class="mb-6">
        <div class="relative inline-block">
          <span class="text-7xl animate-bounce-slow">📖</span>
          <span class="absolute -top-1 -right-1 text-3xl animate-pulse">✨</span>
        </div>
      </div>
      
      <!-- タイトル -->
      <h1 class="text-2xl font-bold text-white mb-2 tracking-wider">
        Study Guardian
      </h1>
      <p class="text-white/80 text-sm mb-8">勉強の旅を始めよう</p>
      
      <!-- プログレスバー -->
      <div class="w-48 mx-auto mb-6">
        <div class="h-2 bg-white/20 rounded-full overflow-hidden">
          <div class="h-full bg-white rounded-full animate-loading-bar"></div>
        </div>
      </div>
      
      <!-- ヒント -->
      <p class="text-white/70 text-xs max-w-xs mx-auto animate-fade-in">
        {{ currentTip }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

defineProps({
  message: {
    type: String,
    default: '読み込み中...'
  }
})

const tips = [
  '💡 毎日の勉強でEXPを貯めよう！',
  '🏆 ランキング上位を目指せ！',
  '🎯 ミッションをクリアしてボーナスGET',
  '📊 データで成長を確認しよう',
  '⚔️ 勉強時間でバトルに勝利！',
  '🛒 貯めたEXPでごほうび交換',
  '🌟 連続勉強でストリークボーナス',
  '📚 教材を登録して効率アップ',
]

const currentTip = ref(tips[0])
let tipInterval = null

onMounted(() => {
  currentTip.value = tips[Math.floor(Math.random() * tips.length)]
  tipInterval = setInterval(() => {
    currentTip.value = tips[Math.floor(Math.random() * tips.length)]
  }, 3000)
})

onUnmounted(() => {
  if (tipInterval) clearInterval(tipInterval)
})
</script>

<style scoped>
@keyframes blob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
}

@keyframes loading-bar {
  0% { width: 0%; transform: translateX(0); }
  50% { width: 70%; }
  100% { width: 100%; }
}

@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes fade-in {
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animate-loading-bar {
  animation: loading-bar 2s ease-in-out infinite;
}

.animate-bounce-slow {
  animation: bounce-slow 2s ease-in-out infinite;
}

.animate-fade-in {
  animation: fade-in 0.5s ease-out;
}
</style>
