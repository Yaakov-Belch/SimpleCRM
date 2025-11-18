<template>
  <div class="min-h-screen bg-gray-50">
    <NavigationBar />

    <main class="max-w-2xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 sm:px-0">
        <div v-if="isLoading" class="text-center py-12">
          <p class="text-gray-500">Loading contact...</p>
        </div>
        <ContactForm v-else :contact-id="contactId" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import NavigationBar from '../components/NavigationBar.vue'
import ContactForm from '../components/ContactForm.vue'

const route = useRoute()
const contactId = ref(route.params.id)
const isLoading = ref(false)
</script>
