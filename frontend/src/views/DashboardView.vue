<template>
  <div class="min-h-screen bg-gray-50">
    <NavigationBar />

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Welcome Section -->
        <div class="bg-white shadow rounded-lg p-6 mb-6">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">
            Welcome, {{ currentUser?.full_name || 'User' }}!
          </h1>
          <div class="border-t border-gray-200 pt-4">
            <p class="text-gray-600">
              Manage your contacts and track your sales pipeline.
            </p>
          </div>
        </div>

        <!-- Pipeline Overview -->
        <PipelineOverview />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import NavigationBar from '../components/NavigationBar.vue'
import PipelineOverview from '../components/PipelineOverview.vue'

const router = useRouter()
const { currentUser, isAuthenticated, fetchCurrentUser } = useAuth()

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  if (!currentUser.value) {
    const result = await fetchCurrentUser()
    if (!result.success) {
      router.push('/login')
    }
  }
})
</script>
