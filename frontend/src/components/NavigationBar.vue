<template>
  <nav class="bg-blue-600 text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center">
          <h1 class="text-xl font-bold">SimpleCRM</h1>
        </div>
        <div v-if="isAuthenticated" class="flex items-center gap-4">
          <router-link to="/dashboard" class="hover:text-blue-200 transition">
            Dashboard
          </router-link>
          <router-link to="/profile" class="hover:text-blue-200 transition">
            Profile
          </router-link>
          <span class="text-blue-100">{{ currentUser?.full_name || 'User' }}</span>
          <button
            @click="handleLogout"
            class="px-3 py-1 bg-blue-700 hover:bg-blue-800 rounded-md transition"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { currentUser, isAuthenticated, logout } = useAuth()

async function handleLogout() {
  await logout()
  router.push('/login')
}
</script>
