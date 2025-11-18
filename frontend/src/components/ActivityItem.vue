<template>
  <div class="activity-item bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
    <!-- Header -->
    <div class="flex justify-between items-start mb-3">
      <div class="flex items-center gap-3">
        <!-- Type Badge -->
        <span
          :class="[
            'px-3 py-1 rounded-full text-xs font-semibold',
            typeBadgeClass
          ]"
        >
          {{ activity.type }}
        </span>

        <!-- Subject -->
        <h3 class="text-lg font-bold text-gray-900">{{ activity.subject }}</h3>
      </div>

      <!-- Action Buttons (visible on hover) -->
      <div class="action-buttons opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
        <button
          @click="$emit('edit', activity)"
          class="p-1 text-gray-600 hover:text-blue-600 focus:outline-none"
          title="Edit activity"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
        <button
          @click="$emit('delete', activity.id)"
          class="p-1 text-gray-600 hover:text-red-600 focus:outline-none"
          title="Delete activity"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Activity Date -->
    <p class="text-sm text-gray-600 mb-3">
      {{ formatDate(activity.activity_date) }}
    </p>

    <!-- Markdown Content -->
    <div
      v-if="activity.notes"
      class="mb-3 prose prose-sm max-w-none"
      :class="{ 'line-clamp-3': !isExpanded }"
      v-html="sanitizedNotes"
    ></div>

    <!-- Expand/Collapse Button (if notes are long) -->
    <button
      v-if="hasLongContent"
      @click="isExpanded = !isExpanded"
      class="text-sm text-blue-600 hover:text-blue-800 font-medium mb-3"
    >
      {{ isExpanded ? 'Show less' : 'Show more' }}
    </button>

    <!-- Attachments -->
    <div v-if="activity.attachments && activity.attachments.length > 0" class="mt-4 border-t border-gray-200 pt-3">
      <h4 class="text-sm font-medium text-gray-700 mb-2">Attachments</h4>
      <ul class="space-y-2">
        <li
          v-for="attachment in activity.attachments"
          :key="attachment.id"
          class="flex items-center gap-2"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
          <a
            @click.prevent="downloadFile(attachment)"
            class="text-sm text-blue-600 hover:text-blue-800 cursor-pointer"
          >
            {{ attachment.original_filename }}
          </a>
          <span class="text-xs text-gray-500">({{ formatFileSize(attachment.file_size) }})</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { downloadAttachment } from '../services/api'

const props = defineProps({
  activity: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete'])

const isExpanded = ref(false)

// Configure marked with GFM support
marked.setOptions({
  gfm: true,
  breaks: true
})

// Type badge styling
const typeBadgeClass = computed(() => {
  const typeColors = {
    'Call': 'bg-blue-100 text-blue-800',
    'Meeting': 'bg-green-100 text-green-800',
    'Email': 'bg-purple-100 text-purple-800',
    'Note': 'bg-gray-100 text-gray-800'
  }

  return typeColors[props.activity.type] || 'bg-gray-100 text-gray-800'
})

// Sanitize markdown notes
const sanitizedNotes = computed(() => {
  if (!props.activity.notes) return ''

  try {
    const rawHtml = marked(props.activity.notes)
    return DOMPurify.sanitize(rawHtml)
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return '<p class="text-red-500">Error parsing markdown</p>'
  }
})

// Check if content is long enough to need expand/collapse
const hasLongContent = computed(() => {
  if (!props.activity.notes) return false
  return props.activity.notes.length > 200 || props.activity.notes.split('\n').length > 5
})

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

async function downloadFile(attachment) {
  try {
    const blob = await downloadAttachment(props.activity.id, attachment.id)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = attachment.original_filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Download failed:', error)
    alert('Failed to download file. Please try again.')
  }
}
</script>

<style scoped>
.activity-item:hover .action-buttons {
  opacity: 1;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Prose styles for markdown rendering */
.prose :deep(h1) {
  font-size: 1.25rem;
  font-weight: bold;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(h2) {
  font-size: 1.125rem;
  font-weight: bold;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(h3) {
  font-size: 1rem;
  font-weight: bold;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(ul), .prose :deep(ol) {
  margin-left: 1.5rem;
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}

.prose :deep(code) {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.875rem;
}

.prose :deep(pre) {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 0.75rem;
  border-radius: 0.375rem;
  overflow-x: auto;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

.prose :deep(blockquote) {
  border-left: 4px solid #d1d5db;
  padding-left: 1rem;
  font-style: italic;
  color: #6b7280;
  margin: 0.5rem 0;
}

.prose :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.5rem 0;
  font-size: 0.875rem;
}

.prose :deep(th), .prose :deep(td) {
  border: 1px solid #d1d5db;
  padding: 0.375rem;
  text-align: left;
}

.prose :deep(th) {
  background-color: #f3f4f6;
  font-weight: bold;
}

.prose :deep(a) {
  color: #2563eb;
  text-decoration: underline;
}

.prose :deep(a:hover) {
  color: #1d4ed8;
}

.prose :deep(p) {
  margin: 0.25rem 0;
}
</style>
