<template>
  <div class="stage-selector">
    <label v-if="showLabel" :for="selectId" class="block text-sm font-medium text-gray-700 mb-1">
      Pipeline Stage
    </label>
    <select
      :id="selectId"
      v-model="selectedStage"
      @change="handleStageChange"
      class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      :disabled="disabled || loading"
    >
      <option v-for="stage in stages" :key="stage" :value="stage">
        {{ stage }}
      </option>
    </select>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { updateContactStage } from '../services/api'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  contactId: {
    type: Number,
    required: true
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'stage-updated', 'error'])

const stages = ['Lead', 'Qualified', 'Proposal', 'Client']
const selectedStage = ref(props.modelValue)
const loading = ref(false)
const error = ref('')
const selectId = `stage-selector-${props.contactId}`

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  selectedStage.value = newValue
})

async function handleStageChange() {
  const newStage = selectedStage.value
  error.value = ''
  loading.value = true

  try {
    await updateContactStage(props.contactId, newStage)
    emit('update:modelValue', newStage)
    emit('stage-updated', { contactId: props.contactId, stage: newStage })
  } catch (err) {
    error.value = err.message || 'Failed to update stage'
    emit('error', err)
    // Revert to previous value on error
    selectedStage.value = props.modelValue
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.stage-selector select:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}
</style>
