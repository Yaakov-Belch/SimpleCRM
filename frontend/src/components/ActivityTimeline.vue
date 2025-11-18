<template>
  <div class="activity-timeline">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-xl font-bold text-gray-900">Activity Timeline</h2>
      <button
        @click="handleNewActivity"
        :disabled="creatingActivity"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {{ creatingActivity ? 'Creating...' : 'New Activity' }}
      </button>
    </div>

    <!-- Filter and Search Controls -->
    <div class="mb-6 space-y-3">
      <div class="flex flex-col md:flex-row gap-3">
        <!-- Type Filter -->
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Type</label>
          <select
            v-model="filterType"
            @change="applyFilters"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="All">All Types{{ totalCount > 0 ? ` (${totalCount})` : '' }}</option>
            <option value="Call">Call{{ typeCounts.Call > 0 ? ` (${typeCounts.Call})` : '' }}</option>
            <option value="Meeting">Meeting{{ typeCounts.Meeting > 0 ? ` (${typeCounts.Meeting})` : '' }}</option>
            <option value="Email">Email{{ typeCounts.Email > 0 ? ` (${typeCounts.Email})` : '' }}</option>
            <option value="Note">Note{{ typeCounts.Note > 0 ? ` (${typeCounts.Note})` : '' }}</option>
          </select>
        </div>

        <!-- Search -->
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            type="text"
            v-model="searchTerm"
            @input="applyFilters"
            placeholder="Search in subject and notes..."
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p class="mt-2 text-gray-600">Loading activities...</p>
    </div>

    <!-- Activity List -->
    <div v-else-if="filteredActivities.length > 0" class="space-y-4">
      <ActivityItem
        v-for="(activity, index) in filteredActivities"
        :key="activity.id"
        :activity="activity"
        :previous-activity="index < filteredActivities.length - 1 ? filteredActivities[index + 1] : null"
        @edit="handleEdit"
        @delete="handleDelete"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-12 bg-gray-50 rounded-lg">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-gray-500">
        {{ searchTerm || filterType !== 'All' ? 'No activities match your filters.' : 'No activities yet. Start tracking interactions with this contact.' }}
      </p>
    </div>

    <!-- Activity Form Modal -->
    <ActivityForm
      v-if="showActivityForm"
      :contact-id="contactId"
      :activity="selectedActivity"
      @saved="handleActivitySaved"
      @cancelled="closeActivityForm"
      @deleted="handleActivityDeleted"
      @stage-updated="handleStageUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import ActivityItem from './ActivityItem.vue'
import ActivityForm from './ActivityForm.vue'
import { getActivitiesForContact, createActivity, ApiError } from '../services/api'

const props = defineProps({
  contactId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['stage-updated'])

const activities = ref([])
const loading = ref(false)
const creatingActivity = ref(false)
const filterType = ref('All')
const searchTerm = ref('')
const showActivityForm = ref(false)
const selectedActivity = ref(null)

// Computed type counts
const typeCounts = computed(() => {
  const counts = {
    Call: 0,
    Meeting: 0,
    Email: 0,
    Note: 0
  }

  activities.value.forEach(activity => {
    if (counts.hasOwnProperty(activity.type)) {
      counts[activity.type]++
    }
  })

  return counts
})

const totalCount = computed(() => {
  return activities.value.length
})

// Computed filtered activities
const filteredActivities = computed(() => {
  let filtered = activities.value

  // Filter by type
  if (filterType.value !== 'All') {
    filtered = filtered.filter(activity => activity.type === filterType.value)
  }

  // Filter by search term
  if (searchTerm.value) {
    const search = searchTerm.value.toLowerCase()
    filtered = filtered.filter(activity => {
      const subjectMatch = activity.subject?.toLowerCase().includes(search)
      const notesMatch = activity.notes?.toLowerCase().includes(search)
      return subjectMatch || notesMatch
    })
  }

  // Sort by activity_date descending (most recent first)
  return filtered.sort((a, b) => {
    return new Date(b.activity_date) - new Date(a.activity_date)
  })
})

async function fetchActivities() {
  loading.value = true
  activities.value = []  // Clear stale data

  try {
    const response = await getActivitiesForContact(props.contactId)
    activities.value = response.activities || response || []
  } catch (err) {
    if (err instanceof ApiError) {
      console.error('Failed to fetch activities:', err.message)
      alert('Failed to load activities. Please try again.')
    } else {
      console.error('Unexpected error:', err)
    }
    activities.value = []
  } finally {
    loading.value = false
  }
}

async function handleNewActivity() {
  creatingActivity.value = true

  try {
    // Create activity immediately with defaults
    const newActivity = await createActivity(props.contactId, {
      type: 'Note',
      subject: '',
      activity_date: new Date().toISOString()
    })

    // Add to timeline
    activities.value.unshift(newActivity)

    // Open form to edit
    selectedActivity.value = newActivity
    showActivityForm.value = true
  } catch (err) {
    if (err instanceof ApiError) {
      alert(err.message || 'Failed to create activity')
    } else {
      alert('An unexpected error occurred. Please try again.')
    }
  } finally {
    creatingActivity.value = false
  }
}

function applyFilters() {
  // Filters are applied automatically via computed property
}

function handleEdit(activity) {
  selectedActivity.value = activity
  showActivityForm.value = true
}

async function handleDelete(activityId) {
  if (!confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
    return
  }

  try {
    const { deleteActivity } = await import('../services/api')
    await deleteActivity(activityId)
    handleActivityDeleted(activityId)
  } catch (err) {
    alert(err.message || 'Failed to delete activity')
  }
}

function handleActivitySaved(activity) {
  if (selectedActivity.value) {
    // Update existing activity
    const index = activities.value.findIndex(a => a.id === activity.id)
    if (index !== -1) {
      activities.value[index] = activity
    }
  } else {
    // Add new activity (shouldn't happen with new workflow, but keep for safety)
    activities.value.unshift(activity)
  }

  closeActivityForm()
}

function handleActivityDeleted(activityId) {
  const index = activities.value.findIndex(a => a.id === activityId)
  if (index !== -1) {
    activities.value.splice(index, 1)
  }

  closeActivityForm()
}

function closeActivityForm() {
  showActivityForm.value = false
  selectedActivity.value = null
}

function handleStageUpdated(data) {
  // Forward the stage-updated event to parent (ContactPreview)
  emit('stage-updated', data)
}

// Watch contactId prop and re-fetch activities when it changes
watch(() => props.contactId, (newContactId) => {
  if (newContactId) {
    fetchActivities()
  }
}, { immediate: true })  // immediate: true runs on initial mount
</script>
