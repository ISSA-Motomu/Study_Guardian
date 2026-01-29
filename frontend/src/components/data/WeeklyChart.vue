<template>
  <div class="h-40 flex items-end gap-2">
    <div
      v-for="(item, idx) in data"
      :key="idx"
      class="flex-1 flex flex-col items-center"
    >
      <!-- Bar -->
      <div 
        class="w-full bg-gradient-to-t from-indigo-500 to-purple-400 rounded-t-lg transition-all duration-500"
        :style="{ height: getBarHeight(item.minutes) + '%' }"
      />
      <!-- Label -->
      <p class="text-xs text-gray-500 mt-2">{{ item.day }}</p>
      <p class="text-xs font-bold text-indigo-600">{{ item.minutes }}分</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const maxMinutes = computed(() => {
  return Math.max(...props.data.map(d => d.minutes), 1)
})

const getBarHeight = (minutes) => {
  return Math.max(5, (minutes / maxMinutes.value) * 100)
}
</script>
