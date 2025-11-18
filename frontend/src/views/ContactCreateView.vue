<template>
  <div class="min-h-screen bg-gray-50">
    <NavigationBar />

    <main class="max-w-2xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 sm:px-0">
        <ContactForm />
      </div>
    </main>
  </div>
</template>

<script setup>
import NavigationBar from '../components/NavigationBar.vue'
import ContactForm from '../components/ContactForm.vue'
</script>
