import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import RegisterView from '../src/views/RegisterView.vue'
import LoginView from '../src/views/LoginView.vue'
import DashboardView from '../src/views/DashboardView.vue'
import ProfileView from '../src/views/ProfileView.vue'

// Mock the API service
vi.mock('../src/services/api', () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  apiPut: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  },
}))

describe('Frontend Integration Tests', () => {
  let router

  beforeEach(async () => {
    localStorage.clear()
    vi.clearAllMocks()
    vi.resetModules()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('should complete user journey from registration to logout', async () => {
    // Import fresh modules
    const { apiPost, apiGet } = await import('../src/services/api')
    const { resetAuthModule } = await import('../src/composables/useAuth')
    resetAuthModule()

    // Create router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', redirect: '/dashboard' },
        { path: '/login', component: LoginView, meta: { public: true } },
        { path: '/register', component: RegisterView, meta: { public: true } },
        { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } },
        { path: '/profile', component: ProfileView, meta: { requiresAuth: true } },
      ],
    })

    // Step 1: Register a new user
    apiPost.mockResolvedValueOnce({
      session_token: 'test-session-token',
      user: {
        id: 1,
        email: 'newuser@example.com',
        full_name: 'New User',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
    })

    const registerWrapper = mount(RegisterView, {
      global: {
        plugins: [router],
      },
    })

    await registerWrapper.find('input[type="text"]').setValue('New User')
    await registerWrapper.find('input[type="email"]').setValue('newuser@example.com')
    await registerWrapper.find('input[type="password"]').setValue('password123')
    await registerWrapper.find('form').trigger('submit')
    await flushPromises()

    // Verify registration called API (without /api prefix - that's added by api service)
    expect(apiPost).toHaveBeenCalledWith('/auth/register', {
      full_name: 'New User',
      email: 'newuser@example.com',
      password: 'password123',
    })

    // Verify session token stored
    expect(localStorage.getItem('sessionToken')).toBe('test-session-token')

    // Step 2: Navigate to dashboard (simulating auto-redirect after registration)
    apiGet.mockResolvedValueOnce({
      id: 1,
      email: 'newuser@example.com',
      full_name: 'New User',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })

    await router.push('/dashboard')
    await router.isReady()

    const dashboardWrapper = mount(DashboardView, {
      global: {
        plugins: [router],
      },
    })

    await flushPromises()

    // Verify dashboard displays user info
    expect(dashboardWrapper.text()).toContain('New User')

    // Step 3: Logout
    apiPost.mockResolvedValueOnce({ message: 'Logged out successfully' })

    const { useAuth } = await import('../src/composables/useAuth')
    const { logout } = useAuth()
    await logout()

    // Verify session token cleared
    expect(localStorage.getItem('sessionToken')).toBeNull()
  })

  it('should persist authentication state across page reloads', async () => {
    // Step 1: Simulate existing session in localStorage
    localStorage.setItem('sessionToken', 'persisted-token')

    // Step 2: Import fresh modules and reset state
    const { apiGet } = await import('../src/services/api')
    const { useAuth, resetAuthModule } = await import('../src/composables/useAuth')
    resetAuthModule()

    const { fetchCurrentUser, currentUser, isAuthenticated } = useAuth()

    // Step 3: Mock API call to fetch current user
    apiGet.mockResolvedValueOnce({
      id: 2,
      email: 'persisted@example.com',
      full_name: 'Persisted User',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })

    // Step 4: Fetch current user to restore session
    await fetchCurrentUser()

    // Verify authentication state restored
    expect(isAuthenticated.value).toBe(true)
    expect(currentUser.value).toEqual({
      id: 2,
      email: 'persisted@example.com',
      full_name: 'Persisted User',
      created_at: expect.any(String),
      updated_at: expect.any(String)
    })

    // Verify API was called (without /api prefix - that's added by api service)
    expect(apiGet).toHaveBeenCalledWith('/users/me')
  })

  it('should recover from network failures with clear error messages', async () => {
    // Import fresh modules
    const { apiPost, ApiError } = await import('../src/services/api')
    const { resetAuthModule } = await import('../src/composables/useAuth')
    resetAuthModule()

    // Create router
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', redirect: '/dashboard' },
        { path: '/login', component: LoginView, meta: { public: true } },
      ],
    })

    // Step 1: Simulate network failure on login
    apiPost.mockRejectedValueOnce(new ApiError('Network error', 0, null))

    const loginWrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    await loginWrapper.find('input[type="email"]').setValue('test@example.com')
    await loginWrapper.find('input[type="password"]').setValue('password123')
    await loginWrapper.find('form').trigger('submit')
    await flushPromises()

    // Verify error message displayed
    expect(loginWrapper.text()).toContain('error')

    // Step 2: Simulate successful retry
    apiPost.mockResolvedValueOnce({
      session_token: 'retry-token',
      user: {
        id: 3,
        email: 'test@example.com',
        full_name: 'Test User'
      },
    })

    await loginWrapper.find('form').trigger('submit')
    await flushPromises()

    // Verify successful login after retry
    expect(localStorage.getItem('sessionToken')).toBe('retry-token')
  })

  it('should handle session expiration and redirect to login', async () => {
    // Step 1: Set up expired session
    localStorage.setItem('sessionToken', 'expired-token')

    // Step 2: Import fresh modules and reset state
    const { apiGet, ApiError } = await import('../src/services/api')
    const { useAuth, resetAuthModule } = await import('../src/composables/useAuth')
    resetAuthModule()

    const { fetchCurrentUser, isAuthenticated, currentUser } = useAuth()

    // Step 3: Mock 401 response (session expired)
    apiGet.mockRejectedValueOnce(new ApiError('Session expired', 401, { error: 'Unauthorized' }))

    // Step 4: Attempt to fetch current user - should fail with 401
    const result = await fetchCurrentUser()

    // Verify authentication state cleared
    expect(result.success).toBe(false)
    expect(isAuthenticated.value).toBe(false)
    expect(currentUser.value).toBeNull()
    expect(localStorage.getItem('sessionToken')).toBeNull()
  })
})
