<template>
  <div class="min-h-screen pb-20 max-w-md mx-auto relative overflow-hidden bg-slate-50">
    <!-- Global Toast Container -->
    <ToastContainer />
    
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
        <AdminView v-else-if="view === 'admin'" @exit="view = 'other'" @viewAsUser="handleViewAsUser" />
        <DataView v-else-if="view === 'data'" @admin="view = 'admin'" />
        <OtherView v-else-if="view === 'other'" @admin="view = 'admin'" />
        <StudyView 
          v-else 
          ref="studyViewRef"
          @timer="view = 'timer'" 
          @openGoalModal="openGoalModalNew"
          @openMaterials="showMaterialsModal = true"
          @openBookshelf="showBookshelfModal = true"
          @editGoal="openGoalModalEdit"
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
      :editGoal="editingGoal"
      @close="closeGoalModal"
      @created="onGoalCreated"
      @updated="onGoalUpdated"
    />

    <MaterialsView
      v-if="showMaterialsModal"
      @close="showMaterialsModal = false"
    />

    <BookshelfView
      v-if="showBookshelfModal"
      @close="showBookshelfModal = false"
    />

    <!-- Bottom Navigation -->
    <BottomNav v-model="view" :in-session="studyStore.inSession" />
    
    <!-- Floating Action Button -->
    <FloatingButton 
      v-if="view === 'study'" 
      :in-session="studyStore.inSession"
      @click="handleFabClick"
    />

    <!-- Global Confirm Dialog -->
    <ConfirmDialog
      v-model="confirmState.show"
      :type="confirmState.type"
      :title="confirmState.title"
      :message="confirmState.message"
      :confirmText="confirmState.confirmText"
      :cancelText="confirmState.cancelText"
      :icon="confirmState.icon"
      :confirmIcon="confirmState.confirmIcon"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useStudyStore } from '@/stores/study'
import { useGameStore } from '@/stores/game'
import { useShopStore } from '@/stores/shop'
import { useEvolutionStore } from '@/stores/evolution'
import { useToastStore } from '@/stores/toast'
import { useLiff } from '@/composables/useLiff'
import { useSound } from '@/composables/useSound'
import { useConfirmDialog } from '@/composables/useConfirmDialog'

// Components
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import BottomNav from '@/components/common/BottomNav.vue'
import FloatingButton from '@/components/common/FloatingButton.vue'
import NotificationBell from '@/components/common/NotificationBell.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'
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
import MaterialsView from '@/components/materials/MaterialsView.vue'
import BookshelfView from '@/components/study/BookshelfView.vue'
import OtherView from '@/components/other/OtherView.vue'

// Stores
const userStore = useUserStore()
const studyStore = useStudyStore()
const gameStore = useGameStore()
const shopStore = useShopStore()
const evolutionStore = useEvolutionStore()
const toastStore = useToastStore()

// Composables
const { initLiff } = useLiff()
const { playSound } = useSound()
const { state: confirmState, handleConfirm, handleCancel } = useConfirmDialog()

// State
const view = ref('study')
const showGoalModal = ref(false)
const showMaterialsModal = ref(false)
const showBookshelfModal = ref(false)
const studyViewRef = ref(null)
const editingGoal = ref(null)

// ゲストモード検知時に通知表示
watch(() => userStore.isGuestMode, (isGuest) => {
  if (isGuest) {
    toastStore.warning('カカ！そいはログインに失敗しとっど 👷', 5000)
  }
})

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

const handleStartStudy = async (data) => {
  // data can be string (subject) for backward compatibility or object { subject, material }
  const subject = typeof data === 'string' ? data : data.subject
  const material = typeof data === 'object' ? data.material : null
  
  await studyStore.startStudy(subject, material)
  view.value = 'timer'
}

const handleFinishStudy = async (reflectionData) => {
  const minutes = await studyStore.finishStudy(reflectionData)
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
  editingGoal.value = null
  // StudyViewの目標リストを更新
  if (studyViewRef.value?.fetchMyGoals) {
    studyViewRef.value.fetchMyGoals()
  }
}

const onGoalUpdated = () => {
  showGoalModal.value = false
  editingGoal.value = null
  // StudyViewの目標リストを更新
  if (studyViewRef.value?.fetchMyGoals) {
    studyViewRef.value.fetchMyGoals()
  }
}

const openGoalModalNew = () => {
  editingGoal.value = null
  showGoalModal.value = true
}

const openGoalModalEdit = (goal) => {
  editingGoal.value = goal
  showGoalModal.value = true
}

const closeGoalModal = () => {
  showGoalModal.value = false
  editingGoal.value = null
}
</script>
