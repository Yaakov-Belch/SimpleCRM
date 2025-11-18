<template>
  <div class="markdown-editor">
    <!-- Mobile toggle buttons -->
    <div class="md:hidden mb-2 flex gap-2">
      <button
        type="button"
        @click="mobileMode = 'write'"
        :class="[
          'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
          mobileMode === 'write'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        ]"
      >
        Write
      </button>
      <button
        type="button"
        @click="mobileMode = 'preview'"
        :class="[
          'flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors',
          mobileMode === 'preview'
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
        ]"
      >
        Preview
      </button>
    </div>

    <!-- Desktop split-pane / Mobile single pane -->
    <div class="grid md:grid-cols-2 gap-4">
      <!-- Write Pane -->
      <div v-show="mobileMode === 'write' || isDesktop" class="flex flex-col">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Markdown
        </label>
        <textarea
          :value="modelValue"
          @input="handleInput"
          :placeholder="placeholder"
          class="flex-1 min-h-[200px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-y"
          rows="10"
        ></textarea>
      </div>

      <!-- Preview Pane -->
      <div v-show="mobileMode === 'preview' || isDesktop" class="flex flex-col">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Preview
        </label>
        <div
          class="flex-1 min-h-[200px] px-3 py-2 border border-gray-200 rounded-md bg-gray-50 prose prose-sm max-w-none overflow-auto"
          v-html="sanitizedHtml"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Write markdown...'
  }
})

const emit = defineEmits(['update:modelValue'])

// Mobile/Desktop mode
const mobileMode = ref('write')
const isDesktop = ref(false)

// Configure marked with GFM support
marked.setOptions({
  gfm: true,
  breaks: true
})

// Debounced preview
let debounceTimer = null
const debouncedMarkdown = ref(props.modelValue)

// Compute sanitized HTML
const sanitizedHtml = computed(() => {
  if (!debouncedMarkdown.value) {
    return '<p class="text-gray-400 italic">Nothing to preview yet...</p>'
  }

  try {
    const rawHtml = marked(debouncedMarkdown.value)
    return DOMPurify.sanitize(rawHtml)
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return '<p class="text-red-500">Error parsing markdown</p>'
  }
})

function handleInput(event) {
  const value = event.target.value
  emit('update:modelValue', value)

  // Debounce preview update
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  debounceTimer = setTimeout(() => {
    debouncedMarkdown.value = value
  }, 300)
}

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
  debouncedMarkdown.value = newValue
})

// Handle window resize for responsive behavior
function updateIsDesktop() {
  isDesktop.value = window.innerWidth >= 768 // md breakpoint
}

onMounted(() => {
  updateIsDesktop()
  window.addEventListener('resize', updateIsDesktop)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateIsDesktop)
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
})
</script>

<style scoped>
/* Additional prose styles for better markdown rendering */
.prose :deep(h1) {
  font-size: 1.5rem;
  font-weight: bold;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.prose :deep(h2) {
  font-size: 1.25rem;
  font-weight: bold;
  margin-top: 0.875rem;
  margin-bottom: 0.5rem;
}

.prose :deep(h3) {
  font-size: 1.125rem;
  font-weight: bold;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}

.prose :deep(ul), .prose :deep(ol) {
  margin-left: 1.5rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.prose :deep(code) {
  background-color: #f3f4f6;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: monospace;
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
}

.prose :deep(th), .prose :deep(td) {
  border: 1px solid #d1d5db;
  padding: 0.5rem;
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

.prose :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.375rem;
  margin: 0.5rem 0;
}
</style>
