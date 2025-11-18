<template>
  <div class="bg-white shadow rounded-lg p-6">
    <div v-if="contact">
      <!-- Header with Actions -->
      <div class="flex justify-between items-start mb-6">
        <h2 class="text-xl font-bold text-gray-900">{{ contact.name }}</h2>
        <div class="flex gap-2">
          <button
            @click="$emit('edit', contact)"
            class="px-3 py-1 text-sm border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Edit
          </button>
          <button
            @click="$emit('delete', contact)"
            class="px-3 py-1 text-sm bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Delete
          </button>
        </div>
      </div>

      <!-- Tabs -->
      <div class="mb-6 border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'timeline'"
            :class="[
              'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'timeline'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Timeline
          </button>
          <button
            @click="activeTab = 'contact-info'"
            :class="[
              'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm',
              activeTab === 'contact-info'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            Contact Info
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div v-show="activeTab === 'timeline'">
        <ActivityTimeline :contact-id="contact.id" />
      </div>

      <div v-show="activeTab === 'contact-info'" class="space-y-4">
        <!-- Contact Fields -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <p class="text-base text-gray-900">
            <a :href="`mailto:${contact.email}`" class="text-blue-600 hover:text-blue-800">
              {{ contact.email }}
            </a>
          </p>
        </div>

        <div v-if="contact.phone">
          <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
          <p class="text-base text-gray-900">{{ contact.phone }}</p>
        </div>

        <div v-if="contact.company">
          <label class="block text-sm font-medium text-gray-700 mb-1">Company</label>
          <p class="text-base text-gray-900">{{ contact.company }}</p>
        </div>

        <div v-if="contact.job_title">
          <label class="block text-sm font-medium text-gray-700 mb-1">Job Title</label>
          <p class="text-base text-gray-900">{{ contact.job_title }}</p>
        </div>

        <div v-if="contact.website">
          <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
          <p class="text-base text-gray-900">
            <a
              :href="contact.website"
              target="_blank"
              rel="noopener noreferrer"
              class="text-blue-600 hover:text-blue-800 inline-flex items-center gap-1"
            >
              {{ contact.website }}
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </p>
        </div>

        <div v-if="contact.notes">
          <label class="block text-sm font-medium text-gray-700 mb-1">Notes</label>
          <p class="text-base text-gray-900 whitespace-pre-wrap">{{ contact.notes }}</p>
        </div>

        <!-- Pipeline Stage Selector -->
        <div>
          <StageSelector
            v-model="currentStage"
            :contact-id="contact.id"
            @stage-updated="handleStageUpdated"
          />
        </div>

        <div class="pt-4 border-t border-gray-200">
          <label class="block text-sm font-medium text-gray-700 mb-1">Created At</label>
          <p class="text-sm text-gray-600">{{ formatDate(contact.created_at) }}</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Updated At</label>
          <p class="text-sm text-gray-600">{{ formatDate(contact.updated_at) }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
      <p class="text-gray-500">Select a contact to view details</p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import StageSelector from './StageSelector.vue'
import ActivityTimeline from './ActivityTimeline.vue'

const props = defineProps({
  contact: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['edit', 'delete', 'stage-updated'])

const activeTab = ref('timeline')
const currentStage = ref(props.contact?.pipeline_stage || 'Lead')

// Watch for contact changes
watch(() => props.contact, (newContact) => {
  if (newContact) {
    currentStage.value = newContact.pipeline_stage
    // Reset to timeline tab when contact changes
    activeTab.value = 'timeline'
  }
}, { immediate: true })

function handleStageUpdated(event) {
  emit('stage-updated', event)
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}
</script>
