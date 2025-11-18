<template>
  <div class="bg-white shadow rounded-lg p-6">
    <h2 class="text-2xl font-bold text-gray-900 mb-6">
      {{ contactId ? 'Edit Contact' : 'New Contact' }}
    </h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <FormInput
        label="Name"
        type="text"
        v-model="formData.name"
        :error="errors.name"
        @blur="validateName"
        required
      />

      <FormInput
        label="Email"
        type="email"
        v-model="formData.email"
        :error="errors.email"
        @blur="validateEmail"
        required
      />

      <FormInput
        label="Phone"
        type="tel"
        v-model="formData.phone"
        :error="errors.phone"
      />

      <FormInput
        label="Company"
        type="text"
        v-model="formData.company"
        :error="errors.company"
      />

      <FormInput
        label="Job Title"
        type="text"
        v-model="formData.job_title"
        :error="errors.job_title"
      />

      <FormInput
        label="Website"
        type="url"
        v-model="formData.website"
        :error="errors.website"
      />

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          v-model="formData.notes"
          rows="4"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          :class="{ 'border-red-500': errors.notes }"
        ></textarea>
        <p v-if="errors.notes" class="mt-1 text-sm text-red-600">{{ errors.notes }}</p>
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          Pipeline Stage
          <span class="text-red-500">*</span>
        </label>
        <select
          v-model="formData.pipeline_stage"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="Lead">Lead</option>
          <option value="Qualified">Qualified</option>
          <option value="Proposal">Proposal</option>
          <option value="Client">Client</option>
        </select>
      </div>

      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          :disabled="isSubmitting"
          class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSubmitting ? 'Saving...' : (contactId ? 'Update Contact' : 'Create Contact') }}
        </button>
        <router-link
          to="/contacts"
          class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 text-center"
        >
          Cancel
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createContact, updateContact, getContactById, ApiError } from '../services/api'
import FormInput from './FormInput.vue'

const props = defineProps({
  contactId: {
    type: [String, Number],
    default: null
  },
  initialData: {
    type: Object,
    default: null
  }
})

const router = useRouter()

const formData = ref({
  name: '',
  email: '',
  phone: '',
  company: '',
  job_title: '',
  website: '',
  notes: '',
  pipeline_stage: 'Lead'
})

const errors = ref({})
const isSubmitting = ref(false)
const isLoading = ref(false)

function validateName() {
  if (!formData.value.name) {
    errors.value.name = 'Name is required'
    return false
  }
  if (formData.value.name.length > 255) {
    errors.value.name = 'Name must be 255 characters or less'
    return false
  }
  errors.value.name = ''
  return true
}

function validateEmail() {
  if (!formData.value.email) {
    errors.value.email = 'Email is required'
    return false
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    errors.value.email = 'Please enter a valid email address'
    return false
  }
  if (formData.value.email.length > 255) {
    errors.value.email = 'Email must be 255 characters or less'
    return false
  }
  errors.value.email = ''
  return true
}

function validateForm() {
  const isNameValid = validateName()
  const isEmailValid = validateEmail()
  return isNameValid && isEmailValid
}

async function handleSubmit() {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const contactData = {
      name: formData.value.name,
      email: formData.value.email,
      phone: formData.value.phone || undefined,
      company: formData.value.company || undefined,
      job_title: formData.value.job_title || undefined,
      website: formData.value.website || undefined,
      notes: formData.value.notes || undefined,
      pipeline_stage: formData.value.pipeline_stage
    }

    let response
    if (props.contactId) {
      response = await updateContact(props.contactId, contactData)
    } else {
      response = await createContact(contactData)
    }

    // Navigate to contacts list with the created/updated contact selected
    router.push({
      path: '/contacts',
      query: { selected: response.id }
    })
  } catch (err) {
    if (err instanceof ApiError) {
      if (err.data?.error?.field) {
        errors.value[err.data.error.field] = err.message
      } else {
        alert(err.message)
      }
    } else {
      alert('An unexpected error occurred. Please try again.')
    }
  } finally {
    isSubmitting.value = false
  }
}

async function loadContact() {
  if (!props.contactId) return

  isLoading.value = true

  try {
    const contact = await getContactById(props.contactId)
    formData.value = {
      name: contact.name || '',
      email: contact.email || '',
      phone: contact.phone || '',
      company: contact.company || '',
      job_title: contact.job_title || '',
      website: contact.website || '',
      notes: contact.notes || '',
      pipeline_stage: contact.pipeline_stage || 'Lead'
    }
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      alert('Contact not found')
      router.push('/contacts')
    } else {
      alert('Failed to load contact. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (props.initialData) {
    formData.value = { ...formData.value, ...props.initialData }
  } else if (props.contactId) {
    loadContact()
  }
})

watch(() => props.initialData, (newData) => {
  if (newData) {
    formData.value = { ...formData.value, ...newData }
  }
})
</script>
