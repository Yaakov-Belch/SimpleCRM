<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-xl font-semibold text-gray-900 mb-4">Pipeline Overview</h2>

    <div v-if="loading" class="text-gray-500">Loading pipeline statistics...</div>

    <div v-else-if="error" class="text-red-600">
      Failed to load pipeline statistics: {{ error }}
    </div>

    <div v-else class="space-y-4">
      <!-- Stage items -->
      <div
        v-for="stage in stageData"
        :key="stage.name"
        class="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
      >
        <div class="flex items-center space-x-3">
          <div :class="['w-3 h-3 rounded-full', stage.color]"></div>
          <span class="font-medium text-gray-900">{{ stage.name }}</span>
        </div>
        <div class="flex items-center space-x-4">
          <span class="text-2xl font-bold text-gray-900">{{ stage.count }}</span>
          <div class="w-32 bg-gray-200 rounded-full h-2">
            <div
              :class="['h-2 rounded-full', stage.barColor]"
              :style="{ width: `${stage.percentage}%` }"
            ></div>
          </div>
          <span class="text-sm text-gray-500 w-12 text-right">{{ stage.percentage }}%</span>
        </div>
      </div>

      <!-- Total -->
      <div class="pt-4 border-t border-gray-200 flex justify-between items-center">
        <span class="font-semibold text-gray-900">Total Contacts</span>
        <span class="text-2xl font-bold text-gray-900">{{ stats?.total_count || 0 }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { getPipelineStats } from '../services/api'

const props = defineProps({
  refreshTrigger: {
    type: Number,
    default: 0
  }
})

const stats = ref(null)
const loading = ref(true)
const error = ref('')

const stageData = computed(() => {
  if (!stats.value) {
    return []
  }

  const total = stats.value.total_count || 1 // Prevent division by zero

  return [
    {
      name: 'Lead',
      count: stats.value.lead_count || 0,
      percentage: total > 0 ? Math.round((stats.value.lead_count / total) * 100) : 0,
      color: 'bg-blue-500',
      barColor: 'bg-blue-500'
    },
    {
      name: 'Qualified',
      count: stats.value.qualified_count || 0,
      percentage: total > 0 ? Math.round((stats.value.qualified_count / total) * 100) : 0,
      color: 'bg-yellow-500',
      barColor: 'bg-yellow-500'
    },
    {
      name: 'Proposal',
      count: stats.value.proposal_count || 0,
      percentage: total > 0 ? Math.round((stats.value.proposal_count / total) * 100) : 0,
      color: 'bg-orange-500',
      barColor: 'bg-orange-500'
    },
    {
      name: 'Client',
      count: stats.value.client_count || 0,
      percentage: total > 0 ? Math.round((stats.value.client_count / total) * 100) : 0,
      color: 'bg-green-500',
      barColor: 'bg-green-500'
    }
  ]
})

async function fetchStats() {
  loading.value = true
  error.value = ''

  try {
    stats.value = await getPipelineStats()
  } catch (err) {
    error.value = err.message || 'Failed to load statistics'
    console.error('Error fetching pipeline stats:', err)
  } finally {
    loading.value = false
  }
}

// Watch for refresh trigger changes
watch(() => props.refreshTrigger, () => {
  fetchStats()
})

onMounted(() => {
  fetchStats()
})
</script>
