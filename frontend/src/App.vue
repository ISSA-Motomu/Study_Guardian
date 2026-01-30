<template>
  <div class="min-h-screen pb-20 max-w-md mx-auto relative overflow-hidden bg-slate-50">
    <!-- Header Background -->
    <div class="absolute top-0 left-0 w-full h-48 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-b-[40px] z-0" />

    <!-- 他ユーザー視点表示中のバナー -->
    <div 
      v-if="userStore.isViewingAsOther"
      class="fixed top-0 left-0 right-0 bg-orange-500 text-white py-2 px-4 z-50 flex items-center justify-between shadow-lg"
    >
      <span class="text-sm font-bold">👁️ {{ userStore.user.name }} の視点で表示中</span>
      <button 
        @click="exitViewMode"
        class="bg-white text-orange-500 px-3 py-1 rounded-full text-xs font-bold hover:bg-orange-100"
      >
        ✕ 戻る
      </button>
    </div>

    <!-- Notification Bell (Top Right) -->
    <div class="absolute top-4 right-4 z-30" :class="{ 'mt-10': userStore.isViewingAsOther }">
      <NotificationBell @navigate="handleNotificationNavigate" />
    </div>

    <!-- Main Content -->
    <div class="relative z-10 px-6 pt-8" :class="{ 'mt-10': userStore.isViewingAsOther }">
      <LoadingSpinner v-if="userStore.loading" />
      
      <template v-else>
        <TimerView v-if="view === 'timer'" @back="view = 'study'" />
        <GameView v-else-if="view === 'game'" />
        <AdminView v-else-if="view === 'admin'" @exit="view = 'study'" @viewAsUser="handleViewAsUser" />
        <DataView v-else-if="view === 'data'" @admin="view = 'admin'" />
        <StudyView 
          v-else 
          ref="studyViewRef"
          @timer="view = 'timer'" 
          @openGoalModal="showGoalModal = true"
        />
      </template>
    </div>

    <!-- Global Modals -->
    <SubjectModal 
      v-if="studyStore.showSubjectModal" 
      @close="studyStore.showSubjectModal = false"
      @start="handleStartStudy"
    />
    
    <MemoConfirmDialog
      v-if="studyStore.showMemoConfirm"
      :memo="studyStore.memoToSend"
      @confirm="handleFinishStudy"
      @cancel="studyStore.showMemoConfirm = false"
    />

    <BuyModal
      v-if="shopStore.showBuyModal"
      :item="shopStore.selectedItem"
      @confirm="handleBuy"
      @cancel="shopStore.showBuyModal = false"
    />

    <ShopListModal
      v-if="shopStore.showShopList"
      @close="shopStore.showShopList = false"
    />

    <GoalModal
      v-if="showGoalModal"
      @close="showGoalModal = false"
      @created="onGoalCreated"
    />

    <!-- Bottom Navigation -->
    <BottomNav v-model="view" :in-session="studyStore.inSession" />
    
    <!-- Floating Action Button -->
    <FloatingButton 
      v-if="view === 'study'" 
      :in-session="studyStore.inSession"
      @click="handleFabClick"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'
import { useGameStore } from '@/stores/game'
import { useShopStore } from '@/stores/shop'
import { useEvolutionStore } from '@/stores/evolution'
import { useLiff } from '@/composables/useLiff'
import { useSound } from '@/composables/useSound'

// Components
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import BottomNav from '@/components/common/BottomNav.vue'
import FloatingButton from '@/components/common/FloatingButton.vue'
import NotificationBell from '@/components/common/NotificationBell.vue'
import StudyView from '@/components/study/StudyView.vue'
import TimerView from '@/components/study/TimerView.vue'
import SubjectModal from '@/components/study/SubjectModal.vue'
import MemoConfirmDialog from '@/components/study/MemoConfirmDialog.vue'
import GameView from '@/components/game/GameView.vue'
import DataView from '@/components/data/DataView.vue'
import AdminView from '@/components/admin/AdminView.vue'
import BuyModal from '@/components/shop/BuyModal.vue'
import ShopListModal from '@/components/shop/ShopListModal.vue'
import GoalModal from '@/components/study/GoalModal.vue'

// Stores
const userStore = useUserStore()
const studyStore = useStudyStore()
const gameStore = useGameStore()
const shopStore = useShopStore()
const evolutionStore = useEvolutionStore()

// Composables
const { initLiff } = useLiff()
const { playSound } = useSound()

// State
const view = ref('study')
const showGoalModal = ref(false)
const studyViewRef = ref(null)

// Lifecycle
onMounted(async () => {
  playSound('poweron')
  await initLiff()
  gameStore.startBattleLoop()
  evolutionStore.initialize()
})

// Handlers
const handleFabClick = () => {
  if (studyStore.inSession) {
    view.value = 'timer'
  } else {
    studyStore.openSubjectModal()
  }
}

const handleStartStudy = async (subject) => {
  await studyStore.startStudy(subject)
  view.value = 'timer'
}

const handleFinishStudy = async () => {
  const minutes = await studyStore.finishStudy()
  if (minutes > 0) {
    gameStore.applyStudyDamage(minutes)
    // 進化ゲームにポイント付与
    const earnedPoints = evolutionStore.earnFromStudy(minutes)
    if (earnedPoints > 0) {
      // サーバーに同期
      await evolutionStore.syncToServer()
    }
  }
  view.value = 'study'
}

const handleBuy = async (comment) => {
  await shopStore.confirmBuy(comment)
}

const handleNotificationNavigate = (target) => {
  if (target === 'admin') {
    view.value = 'admin'
  }
}

// 他ユーザー視点で見る
const handleViewAsUser = () => {
  view.value = 'study'  // 勉強画面に移動
}

// 元の管理者に戻る
const exitViewMode = async () => {
  await userStore.exitViewAsUser()
  view.value = 'study'
}

const onGoalCreated = () => {
  showGoalModal.value = false
  // StudyViewの目標リストを更新
  if (studyViewRef.value?.fetchMyGoals) {
    studyViewRef.value.fetchMyGoals()
  }
}
</script>
