import { ref } from 'vue'
import { getContacts, ApiError } from '../services/api'

export function useContacts() {
  const contacts = ref([])
  const selectedContact = ref(null)
  const isLoading = ref(false)
  const error = ref('')
  const pagination = ref({
    page: 1,
    limit: 50,
    total: 0,
    hasMore: false
  })

  async function fetchContacts(params = {}) {
    isLoading.value = true
    error.value = ''

    try {
      const data = await getContacts({
        page: params.page || pagination.value.page,
        limit: params.limit || pagination.value.limit,
        search: params.search,
        stage: params.stage
      })

      contacts.value = data.contacts
      pagination.value = {
        page: data.page,
        limit: data.limit,
        total: data.total,
        hasMore: data.has_more
      }

      return data
    } catch (err) {
      if (err instanceof ApiError) {
        error.value = err.message
      } else {
        error.value = 'Failed to load contacts. Please try again.'
      }
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function selectContact(contact) {
    selectedContact.value = contact
  }

  function clearSelection() {
    selectedContact.value = null
  }

  return {
    contacts,
    selectedContact,
    isLoading,
    error,
    pagination,
    fetchContacts,
    selectContact,
    clearSelection
  }
}
