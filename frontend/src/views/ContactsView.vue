<template>
  <div class="min-h-screen bg-gray-50">
    <NavigationBar />

    <main class="max-w-full mx-auto py-6 px-8">
      <div class="px-4 sm:px-0">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Contact List (Left - 1 column) -->
          <div class="col-span-1">
            <div class="bg-white shadow rounded-lg">
              <!-- Header -->
              <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h1 class="text-2xl font-bold text-gray-900">Contacts</h1>
                <router-link
                  to="/contacts/new"
                  class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  New Contact
                </router-link>
              </div>

              <!-- Active/Passive Tabs -->
              <div class="px-6 pt-4 border-b border-gray-200">
                <nav class="-mb-px flex space-x-8">
                  <button
                    @click="switchActivePassiveTab('Active')"
                    :class="[
                      'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm',
                      activePassiveTab === 'Active'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    ]"
                  >
                    Active
                    <span v-if="activeCount > 0" class="ml-2 px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                      {{ activeCount }}
                    </span>
                  </button>
                  <button
                    @click="switchActivePassiveTab('Passive')"
                    :class="[
                      'whitespace-nowrap pb-4 px-1 border-b-2 font-medium text-sm',
                      activePassiveTab === 'Passive'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    ]"
                  >
                    Passive
                    <span v-if="passiveCount > 0" class="ml-2 px-2 py-1 bg-gray-100 text-gray-800 rounded-full text-xs">
                      {{ passiveCount }}
                    </span>
                  </button>
                </nav>
              </div>

              <!-- Search and Filter -->
              <div class="px-6 py-4 border-b border-gray-200 space-y-4">
                <div class="flex gap-4">
                  <div class="flex-1">
                    <input
                      type="text"
                      v-model="searchQuery"
                      @input="onSearchInput"
                      placeholder="Search by name, email, or company..."
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div class="w-48">
                    <select
                      v-model="stageFilter"
                      @change="onFilterChange"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="All">All Stages{{ allStagesCount > 0 ? ` (${allStagesCount})` : '' }}</option>
                      <option v-for="stage in currentStages" :key="stage" :value="stage">
                        {{ stage }}{{ stageCounts[stage] > 0 ? ` (${stageCounts[stage]})` : '' }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- Contact List Table -->
              <div class="overflow-x-auto">
                <table v-if="!isLoading && contacts.length > 0" class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Company
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Stage
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr
                      v-for="contact in contacts"
                      :key="contact.id"
                      @click="selectContact(contact)"
                      :class="[
                        'cursor-pointer hover:bg-gray-50',
                        selectedContact?.id === contact.id ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                      ]"
                    >
                      <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {{ contact.name }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ contact.email }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {{ contact.company || '-' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm">
                        <span :class="getStageClass(contact.current_pipeline_stage || contact.pipeline_stage)">
                          {{ contact.current_pipeline_stage || contact.pipeline_stage }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>

                <!-- Loading State -->
                <div v-if="isLoading" class="px-6 py-12 text-center">
                  <div class="text-gray-500">Loading contacts...</div>
                </div>

                <!-- Empty State -->
                <div v-if="!isLoading && contacts.length === 0" class="px-6 py-12 text-center">
                  <p class="text-gray-500">No contacts found.</p>
                </div>
              </div>

              <!-- Pagination -->
              <div v-if="!isLoading && contacts.length > 0" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <div class="text-sm text-gray-700">
                  Showing {{ (pagination.page - 1) * pagination.limit + 1 }} - {{ Math.min(pagination.page * pagination.limit, pagination.total) }} of {{ pagination.total }} contacts
                </div>
                <div class="flex gap-2">
                  <button
                    @click="previousPage"
                    :disabled="pagination.page === 1"
                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    @click="nextPage"
                    :disabled="!pagination.hasMore"
                    class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Preview Panel (Right - 1 column) -->
          <div class="col-span-1">
            <div class="sticky top-6">
              <ContactPreview
                :contact="selectedContact"
                @edit="onEdit"
                @delete="onDeleteRequest"
                @stage-updated="onStageUpdated"
              />
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      :is-open="showDeleteConfirm"
      title="Delete Contact"
      :message="`Are you sure you want to delete ${contactToDelete?.name}?`"
      confirm-text="Delete"
      cancel-text="Cancel"
      @confirm="onDeleteConfirm"
      @cancel="onDeleteCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useContacts } from '../composables/useContacts'
import { deleteContact, apiGet, ApiError } from '../services/api'
import NavigationBar from '../components/NavigationBar.vue'
import ContactPreview from '../components/ContactPreview.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const router = useRouter()
const route = useRoute()

const { contacts, selectedContact, isLoading, error, pagination, fetchContacts, selectContact, clearSelection } = useContacts()

const searchQuery = ref(route.query.search || '')
const stageFilter = ref(route.query.stage || 'All')
const activePassiveTab = ref('Active')
const showDeleteConfirm = ref(false)
const contactToDelete = ref(null)
const stageCounts = ref({})
const activeCount = ref(0)
const passiveCount = ref(0)

let searchTimeout = null

// Pipeline stage categories
const activeStages = ['Lead', 'Qualified', 'Proposal', 'Client']
const passiveStages = ['Qualified Out', 'Lost Proposal', 'Work Completed', 'Archived']

// Computed current stages based on Active/Passive tab
const currentStages = computed(() => {
  return activePassiveTab.value === 'Active' ? activeStages : passiveStages
})

// Computed all stages count for current tab
const allStagesCount = computed(() => {
  return activePassiveTab.value === 'Active' ? activeCount.value : passiveCount.value
})

function debounceSearch(callback, delay = 300) {
  return (...args) => {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => callback(...args), delay)
  }
}

const debouncedFetch = debounceSearch(async () => {
  await loadContacts()
}, 300)

function onSearchInput() {
  updateQueryParams()
  debouncedFetch()
  fetchFilterCounts()
}

function onFilterChange() {
  updateQueryParams()
  loadContacts()
  fetchFilterCounts()
}

function switchActivePassiveTab(tab) {
  activePassiveTab.value = tab
  stageFilter.value = 'All'
  updateQueryParams()
  loadContacts()
  fetchFilterCounts()
}

function updateQueryParams() {
  const query = {}
  if (searchQuery.value) query.search = searchQuery.value
  if (stageFilter.value && stageFilter.value !== 'All') query.stage = stageFilter.value
  if (pagination.value.page > 1) query.page = pagination.value.page

  router.replace({ query })
}

async function loadContacts() {
  try {
    // Build stage filter based on Active/Passive tab
    let stageParam = undefined
    if (stageFilter.value !== 'All') {
      stageParam = stageFilter.value
    } else {
      // When "All" is selected, filter by all stages in current tab (Active or Passive)
      stageParam = currentStages.value.join(',')
    }

    await fetchContacts({
      page: pagination.value.page,
      search: searchQuery.value || undefined,
      stage: stageParam
    })
  } catch (err) {
    console.error('Failed to load contacts:', err)
  }
}

async function fetchFilterCounts() {
  try {
    const params = new URLSearchParams()
    if (searchQuery.value) {
      params.append('search', searchQuery.value)
    }

    const response = await apiGet(`/contacts/filter-counts${params.toString() ? '?' + params.toString() : ''}`)

    if (response && response.stage_counts) {
      stageCounts.value = response.stage_counts

      // Calculate active and passive totals
      activeCount.value = activeStages.reduce((sum, stage) => sum + (response.stage_counts[stage] || 0), 0)
      passiveCount.value = passiveStages.reduce((sum, stage) => sum + (response.stage_counts[stage] || 0), 0)
    }
  } catch (err) {
    console.error('Failed to fetch filter counts:', err)
  }
}

function previousPage() {
  if (pagination.value.page > 1) {
    pagination.value.page--
    updateQueryParams()
    loadContacts()
  }
}

function nextPage() {
  if (pagination.value.hasMore) {
    pagination.value.page++
    updateQueryParams()
    loadContacts()
  }
}

function onEdit(contact) {
  router.push(`/contacts/${contact.id}/edit`)
}

function onDeleteRequest(contact) {
  contactToDelete.value = contact
  showDeleteConfirm.value = true
}

async function onDeleteConfirm() {
  if (!contactToDelete.value) return

  try {
    await deleteContact(contactToDelete.value.id)

    // Remove from list
    const index = contacts.value.findIndex(c => c.id === contactToDelete.value.id)
    if (index !== -1) {
      contacts.value.splice(index, 1)
    }

    // Clear selection if deleted contact was selected
    if (selectedContact.value?.id === contactToDelete.value.id) {
      clearSelection()
    }

    // Update pagination total
    pagination.value.total--

    showDeleteConfirm.value = false
    contactToDelete.value = null

    // Refresh counts
    fetchFilterCounts()
  } catch (err) {
    console.error('Failed to delete contact:', err)
    alert(err instanceof ApiError ? err.message : 'Failed to delete contact. Please try again.')
  }
}

function onDeleteCancel() {
  showDeleteConfirm.value = false
  contactToDelete.value = null
}

function onStageUpdated({ contactId, stage }) {
  // Update the contact in the local list
  const contactIndex = contacts.value.findIndex(c => c.id === contactId)
  if (contactIndex !== -1) {
    // Create a new object to ensure Vue's reactivity detects the change
    contacts.value[contactIndex] = {
      ...contacts.value[contactIndex],
      current_pipeline_stage: stage,
      pipeline_stage: stage
    }
  }

  // Update selected contact if it's the one that changed
  if (selectedContact.value?.id === contactId) {
    selectedContact.value = {
      ...selectedContact.value,
      current_pipeline_stage: stage,
      pipeline_stage: stage
    }
  }

  // Refresh counts
  fetchFilterCounts()
}

function getStageClass(stage) {
  const baseClass = 'px-2 py-1 text-xs font-semibold rounded-full'
  const stages = {
    // Active stages
    'Lead': 'bg-yellow-100 text-yellow-800',
    'Qualified': 'bg-blue-100 text-blue-800',
    'Proposal': 'bg-purple-100 text-purple-800',
    'Client': 'bg-green-100 text-green-800',
    // Passive stages
    'Qualified Out': 'bg-gray-100 text-gray-800',
    'Lost Proposal': 'bg-red-100 text-red-800',
    'Work Completed': 'bg-teal-100 text-teal-800',
    'Archived': 'bg-slate-100 text-slate-800'
  }
  return `${baseClass} ${stages[stage] || 'bg-gray-100 text-gray-800'}`
}

onMounted(async () => {
  // Load initial data from URL query params
  if (route.query.page) {
    pagination.value.page = parseInt(route.query.page) || 1
  }

  await loadContacts()
  await fetchFilterCounts()
})
</script>
