<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="text-center text-3xl font-extrabold text-gray-900">Sign in to your account</h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Don't have an account?
          <router-link to="/register" class="font-medium text-blue-600 hover:text-blue-500">
            Sign up
          </router-link>
        </p>
      </div>

      <div class="mt-8 bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <ErrorMessage :message="generalError" />

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <FormInput
            label="Email"
            type="email"
            v-model="email"
            :error="errors.email"
            @blur="validateEmail"
            required
          />

          <FormInput
            label="Password"
            type="password"
            v-model="password"
            :error="errors.password"
            @blur="validatePassword"
            required
          />

          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isSubmitting ? 'Signing in...' : 'Login' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import FormInput from '../components/FormInput.vue'
import ErrorMessage from '../components/ErrorMessage.vue'

const router = useRouter()
const { login } = useAuth()

const email = ref('')
const password = ref('')
const errors = ref({
  email: '',
  password: '',
})
const generalError = ref('')
const isSubmitting = ref(false)

function validateEmail() {
  if (!email.value) {
    errors.value.email = 'Email is required'
    return false
  }
  if (!email.value.includes('@')) {
    errors.value.email = 'Please enter a valid email address'
    return false
  }
  errors.value.email = ''
  return true
}

function validatePassword() {
  if (!password.value) {
    errors.value.password = 'Password is required'
    return false
  }
  errors.value.password = ''
  return true
}

function validateForm() {
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  return isEmailValid && isPasswordValid
}

async function handleSubmit() {
  generalError.value = ''

  if (!validateForm()) {
    return
  }

  isSubmitting.value = true

  try {
    const result = await login(email.value, password.value)

    if (result.success) {
      router.push('/contacts')
    } else {
      generalError.value = result.error
    }
  } catch (error) {
    generalError.value = 'An unexpected error occurred. Please try again.'
  } finally {
    isSubmitting.value = false
  }
}
</script>
