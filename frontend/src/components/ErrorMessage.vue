<template>
  <div v-if="message" class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
    <p class="text-sm text-red-600">{{ message }}</p>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: '',
  },
})
</script>
