<template>
  <div class="min-h-screen bg-gray-50">
    <NavigationBar />

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <div class="bg-white shadow rounded-lg p-6">
          <h1 class="text-3xl font-bold text-gray-900 mb-6">Your Profile</h1>

          <!-- Current Profile Information -->
          <div class="mb-8 pb-6 border-b border-gray-200">
            <h2 class="text-lg font-semibold text-gray-700 mb-4">Current Information</h2>
            <div class="space-y-2">
              <p class="text-gray-600">
                <span class="font-medium">Name:</span> {{ currentUser?.full_name || 'N/A' }}
              </p>
              <p class="text-gray-600">
                <span class="font-medium">Email:</span> {{ currentUser?.email || 'N/A' }}
              </p>
            </div>
          </div>

          <!-- Edit Profile Form -->
          <div>
            <h2 class="text-lg font-semibold text-gray-700 mb-4">Update Profile</h2>

            <ErrorMessage :message="generalError" />

            <div v-if="successMessage" class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
              <p class="text-sm text-green-600">{{ successMessage }}</p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-6">
              <FormInput
                label="Full Name"
                type="text"
                v-model="fullName"
                :error="errors.fullName"
                @blur="validateFullName"
              />

              <FormInput
                label="Email"
                type="email"
                v-model="email"
                :error="errors.email"
                @blur="validateEmail"
              />

              <FormInput
                label="Password"
                type="password"
                v-model="password"
                :error="errors.password"
                @blur="validatePassword"
              />
              <p class="text-xs text-gray-500 -mt-3">Leave blank to keep current password</p>

              <button
                type="submit"
                :disabled="isSubmitting"
                class="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
              </button>
            </form>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import NavigationBar from '../components/NavigationBar.vue'
import FormInput from '../components/FormInput.vue'
import ErrorMessage from '../components/ErrorMessage.vue'
import { apiPut } from '../services/api'

const router = useRouter()
const { currentUser, isAuthenticated, fetchCurrentUser } = useAuth()

const fullName = ref('')
const email = ref('')
const password = ref('')
const errors = ref({
  fullName: '',
  email: '',
  password: '',
})
const generalError = ref('')
const successMessage = ref('')
const isSubmitting = ref(false)

onMounted(async () => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }

  if (!currentUser.value) {
    const result = await fetchCurrentUser()
    if (!result.success) {
      router.push('/login')
      return
    }
  }

  // Pre-fill form with current values
  if (currentUser.value) {
    fullName.value = currentUser.value.full_name
    email.value = currentUser.value.email
  }
})

function validateFullName() {
  if (fullName.value && !fullName.value.trim()) {
    errors.value.fullName = 'Full name cannot be empty'
    return false
  }
  errors.value.fullName = ''
  return true
}

function validateEmail() {
  if (email.value && !email.value.includes('@')) {
    errors.value.email = 'Please enter a valid email address'
    return false
  }
  errors.value.email = ''
  return true
}

function validatePassword() {
  if (password.value && password.value.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
    return false
  }
  errors.value.password = ''
  return true
}

function validateForm() {
  const isFullNameValid = validateFullName()
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  return isFullNameValid && isEmailValid && isPasswordValid
}

async function handleSubmit() {
  generalError.value = ''
  successMessage.value = ''

  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    // Build update payload with only changed fields
    const updateData = {}
    if (fullName.value !== currentUser.value.full_name) {
      updateData.full_name = fullName.value
    }
    if (email.value !== currentUser.value.email) {
      updateData.email = email.value
    }
    if (password.value) {
      updateData.password = password.value
    }

    if (Object.keys(updateData).length === 0) {
      generalError.value = 'No changes to save'
      return
    }

    const updatedUser = await apiPut('/users/me', updateData)
    currentUser.value = updatedUser
    fullName.value = updatedUser.full_name
    email.value = updatedUser.email
    password.value = ''

    successMessage.value = 'Profile updated successfully!'
  } catch (error) {
    if (error.status === 409) {
      generalError.value = 'Email already in use by another account'
    } else {
      generalError.value = error.message || 'Failed to update profile'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>
