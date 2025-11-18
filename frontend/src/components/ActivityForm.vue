<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click.self="$emit('cancelled')">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-2xl font-bold text-gray-900">
          {{ activity ? 'Edit Activity' : 'New Activity' }}
        </h3>
        <button
          @click="$emit('cancelled')"
          class="text-gray-400 hover:text-gray-600"
        >
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <!-- Activity Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Activity Type
            <span class="text-red-500">*</span>
          </label>
          <select
            v-model="formData.type"
            @blur="validateType"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.type }"
          >
            <option value="">Select type...</option>
            <option value="Call">Call</option>
            <option value="Meeting">Meeting</option>
            <option value="Email">Email</option>
            <option value="Note">Note</option>
          </select>
          <p v-if="errors.type" class="mt-1 text-sm text-red-600">{{ errors.type }}</p>
        </div>

        <!-- Subject -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Subject
            <span class="text-red-500">*</span>
          </label>
          <input
            type="text"
            v-model="formData.subject"
            @blur="validateSubject"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.subject }"
            placeholder="Brief description of the activity"
          />
          <p v-if="errors.subject" class="mt-1 text-sm text-red-600">{{ errors.subject }}</p>
        </div>

        <!-- Activity Date -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Activity Date
            <span class="text-red-500">*</span>
          </label>
          <input
            type="datetime-local"
            v-model="formData.activity_date"
            @blur="validateActivityDate"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            :class="{ 'border-red-500': errors.activity_date }"
          />
          <p v-if="errors.activity_date" class="mt-1 text-sm text-red-600">{{ errors.activity_date }}</p>
        </div>

        <!-- Notes (Markdown Editor) -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Notes
          </label>
          <MarkdownEditor
            v-model="formData.notes"
            placeholder="Write your notes using markdown..."
          />
        </div>

        <!-- File Attachments -->
        <div v-if="activity">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Attachments
          </label>

          <!-- Existing Attachments -->
          <div v-if="activity.attachments && activity.attachments.length > 0" class="mb-3">
            <ul class="space-y-2">
              <li
                v-for="attachment in activity.attachments"
                :key="attachment.id"
                class="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200"
              >
                <div class="flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  <span class="text-sm">{{ attachment.original_filename }}</span>
                  <span class="text-xs text-gray-500">({{ formatFileSize(attachment.file_size) }})</span>
                </div>
                <button
                  type="button"
                  @click="handleDeleteAttachment(attachment.id)"
                  class="text-red-600 hover:text-red-800"
                  :disabled="isDeleting"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </li>
            </ul>
          </div>

          <!-- Upload New File -->
          <div class="flex items-center gap-2">
            <input
              type="file"
              ref="fileInput"
              @change="handleFileSelect"
              class="hidden"
            />
            <button
              type="button"
              @click="$refs.fileInput.click()"
              :disabled="isUploading"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ isUploading ? 'Uploading...' : 'Add Attachment' }}
            </button>
            <span v-if="uploadError" class="text-sm text-red-600">{{ uploadError }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-3 pt-4 border-t border-gray-200">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmitting ? 'Saving...' : (activity ? 'Update Activity' : 'Create Activity') }}
          </button>
          <button
            type="button"
            @click="$emit('cancelled')"
            class="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            v-if="activity"
            type="button"
            @click="handleDelete"
            :disabled="isSubmitting"
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import MarkdownEditor from './MarkdownEditor.vue'
import {
  createActivity,
  updateActivity,
  deleteActivity,
  uploadAttachment,
  deleteAttachment,
  ApiError
} from '../services/api'

const props = defineProps({
  contactId: {
    type: Number,
    required: true
  },
  activity: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['saved', 'cancelled', 'deleted'])

const formData = reactive({
  type: '',
  subject: '',
  activity_date: '',
  notes: ''
})

const errors = ref({})
const isSubmitting = ref(false)
const isUploading = ref(false)
const isDeleting = ref(false)
const uploadError = ref('')
const fileInput = ref(null)

function validateType() {
  if (!formData.type) {
    errors.value.type = 'Activity type is required'
    return false
  }
  errors.value.type = ''
  return true
}

function validateSubject() {
  if (!formData.subject) {
    errors.value.subject = 'Subject is required'
    return false
  }
  if (formData.subject.length > 255) {
    errors.value.subject = 'Subject must be 255 characters or less'
    return false
  }
  errors.value.subject = ''
  return true
}

function validateActivityDate() {
  if (!formData.activity_date) {
    errors.value.activity_date = 'Activity date is required'
    return false
  }
  errors.value.activity_date = ''
  return true
}

function validateForm() {
  const isTypeValid = validateType()
  const isSubjectValid = validateSubject()
  const isDateValid = validateActivityDate()
  return isTypeValid && isSubjectValid && isDateValid
}

async function handleSubmit() {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const activityData = {
      type: formData.type,
      subject: formData.subject,
      activity_date: formData.activity_date,
      notes: formData.notes || undefined
    }

    let savedActivity
    if (props.activity) {
      savedActivity = await updateActivity(props.activity.id, activityData)
    } else {
      savedActivity = await createActivity(props.contactId, activityData)
    }

    emit('saved', savedActivity)
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

async function handleFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return

  if (!props.activity) {
    alert('Please save the activity first before adding attachments.')
    return
  }

  isUploading.value = true
  uploadError.value = ''

  try {
    const attachment = await uploadAttachment(props.activity.id, file)

    // Add attachment to activity's attachments array
    if (!props.activity.attachments) {
      props.activity.attachments = []
    }
    props.activity.attachments.push(attachment)

    // Clear file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (err) {
    uploadError.value = err.message || 'Failed to upload file'
  } finally {
    isUploading.value = false
  }
}

async function handleDeleteAttachment(attachmentId) {
  if (!confirm('Are you sure you want to delete this attachment?')) {
    return
  }

  isDeleting.value = true

  try {
    await deleteAttachment(props.activity.id, attachmentId)

    // Remove attachment from activity's attachments array
    const index = props.activity.attachments.findIndex(a => a.id === attachmentId)
    if (index !== -1) {
      props.activity.attachments.splice(index, 1)
    }
  } catch (err) {
    alert(err.message || 'Failed to delete attachment')
  } finally {
    isDeleting.value = false
  }
}

async function handleDelete() {
  if (!confirm('Are you sure you want to delete this activity? This action cannot be undone.')) {
    return
  }

  isSubmitting.value = true

  try {
    await deleteActivity(props.activity.id)
    emit('deleted', props.activity.id)
  } catch (err) {
    alert(err.message || 'Failed to delete activity')
  } finally {
    isSubmitting.value = false
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

function formatDateTimeLocal(dateString) {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

onMounted(() => {
  if (props.activity) {
    formData.type = props.activity.type
    formData.subject = props.activity.subject
    formData.activity_date = formatDateTimeLocal(props.activity.activity_date)
    formData.notes = props.activity.notes || ''
  } else {
    // Default to current date/time for new activities
    formData.activity_date = formatDateTimeLocal(new Date().toISOString())
  }
})
</script>
