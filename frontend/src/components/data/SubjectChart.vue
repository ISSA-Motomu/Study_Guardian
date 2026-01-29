<template>
  <div class="space-y-3">
    <div
      v-for="(item, idx) in data"
      :key="idx"
      class="flex items-center gap-3"
    >
      <!-- Subject Label -->
      <div class="w-16 text-sm font-medium text-gray-700 truncate">
        {{ item.subject }}
      </div>
      
      <!-- Progress Bar -->
      <div class="flex-1 h-6 bg-gray-100 rounded-full overflow-hidden">
        <div 
          class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
          :style="{ 
            width: getBarWidth(item.minutes) + '%',
            backgroundColor: item.color 
          }"
        >
          <span 
            v-if="getBarWidth(item.minutes) > 30"
            class="text-white text-xs font-bold"
          >
            {{ item.minutes }}分
          </span>
        </div>
      </div>
      
      <!-- Minutes (outside bar for small values) -->
      <span 
        v-if="getBarWidth(item.minutes) <= 30"
        class="text-sm font-medium text-gray-600 w-12 text-right"
      >
        {{ item.minutes }}分
      </span>
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

const getBarWidth = (minutes) => {
  return Math.max(5, (minutes / maxMinutes.value) * 100)
}
</script>
