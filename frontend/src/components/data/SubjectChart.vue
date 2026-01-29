<template>
  <div class="flex items-center gap-6">
    <!-- Pie Chart -->
    <div class="relative w-32 h-32 flex-shrink-0">
      <div 
        class="w-full h-full rounded-full"
        :style="{ background: gradientStyle }"
      />
      <!-- Inner White Circle (Donut) -->
      <div class="absolute inset-4 bg-white rounded-full flex items-center justify-center shadow-inner">
        <span class="text-xs font-bold text-gray-500">TOTAL<br>{{ totalMinutes }}分</span>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex-1 space-y-2">
      <div
        v-for="(item, idx) in sortedData"
        :key="idx"
        class="flex items-center justify-between text-sm"
      >
        <div class="flex items-center gap-2">
          <div 
            class="w-3 h-3 rounded-full"
            :style="{ backgroundColor: item.color }"
          />
          <span class="text-gray-700 font-medium">{{ item.subject }}</span>
        </div>
        <div class="text-right">
          <span class="font-bold text-gray-800">{{ item.minutes }}分</span>
          <span class="text-xs text-gray-400 ml-1">({{ Math.round(item.percent) }}%)</span>
        </div>
      </div>
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

const sortedData = computed(() => {
  return [...props.data].sort((a, b) => b.minutes - a.minutes)
})

const totalMinutes = computed(() => {
  return props.data.reduce((acc, cur) => acc + cur.minutes, 0)
})

const gradientStyle = computed(() => {
  if (props.data.length === 0) return '#e5e7eb'
  
  let currentPos = 0
  const parts = sortedData.value.map(item => {
    const start = currentPos
    const end = currentPos + item.percent
    currentPos = end
    return `${item.color} ${start}% ${end}%`
  })
  
  return `conic-gradient(${parts.join(', ')})`
})
</script>
