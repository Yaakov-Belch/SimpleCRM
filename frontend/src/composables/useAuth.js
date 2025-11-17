import { ref, computed } from 'vue'
import { apiGet, apiPost, ApiError } from '../services/api'

// Shared state across all component instances
const currentUser = ref(null)
const sessionToken = ref(null)

// Initialize from localStorage on module load
if (typeof window !== 'undefined' && window.localStorage) {
  sessionToken.value = localStorage.getItem('sessionToken')
}

export function useAuth() {
  const isAuthenticated = computed(() => !!sessionToken.value)

  async function login(email, password) {
    try {
      const response = await apiPost('/auth/login', { email, password })

      sessionToken.value = response.session_token
      currentUser.value = response.user

      localStorage.setItem('sessionToken', response.session_token)

      return { success: true, user: response.user }
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        return { success: false, error: 'Invalid email or password' }
      }
      return { success: false, error: error.message || 'Login failed' }
    }
  }

  async function register(fullName, email, password) {
    try {
      const response = await apiPost('/auth/register', {
        full_name: fullName,
        email,
        password,
      })

      sessionToken.value = response.session_token
      currentUser.value = response.user

      localStorage.setItem('sessionToken', response.session_token)

      return { success: true, user: response.user }
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        return { success: false, error: 'Email already registered' }
      }
      return { success: false, error: error.message || 'Registration failed' }
    }
  }

  async function logout() {
    try {
      await apiPost('/auth/logout', {})
    } catch (error) {
      // Ignore errors during logout, still clear local state
      console.error('Logout error:', error)
    } finally {
      sessionToken.value = null
      currentUser.value = null
      localStorage.removeItem('sessionToken')
    }
  }

  async function fetchCurrentUser() {
    if (!sessionToken.value) {
      return { success: false, error: 'Not authenticated' }
    }

    try {
      const user = await apiGet('/users/me')
      currentUser.value = user
      return { success: true, user }
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        // Session expired, clear auth state
        sessionToken.value = null
        currentUser.value = null
        localStorage.removeItem('sessionToken')
        return { success: false, error: 'Session expired' }
      }
      return { success: false, error: error.message || 'Failed to fetch user' }
    }
  }

  async function updateProfile(data) {
    try {
      const response = await apiPost('/users/me', data)
      currentUser.value = response
      return { success: true, user: response }
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        return { success: false, error: 'Email already in use' }
      }
      return { success: false, error: error.message || 'Update failed' }
    }
  }

  return {
    currentUser,
    sessionToken,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
  }
}

// Exported helper for testing - reset module state
export function resetAuthModule() {
  currentUser.value = null
  sessionToken.value = null
  if (typeof window !== 'undefined' && window.localStorage) {
    const token = localStorage.getItem('sessionToken')
    if (token) {
      sessionToken.value = token
    }
  }
}
