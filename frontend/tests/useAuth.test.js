import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'

// Mock the API service
vi.mock('../src/services/api', () => ({
  apiGet: vi.fn(),
  apiPost: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  },
}))

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    // Reset modules to get fresh state
    vi.resetModules()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('should initialize with no user when no token in localStorage', async () => {
    const { useAuth } = await import('../src/composables/useAuth')
    const { currentUser, isAuthenticated } = useAuth()
    expect(currentUser.value).toBeNull()
    expect(isAuthenticated.value).toBe(false)
  })

  it('should set authenticated state after successful login', async () => {
    const { apiPost } = await import('../src/services/api')
    apiPost.mockResolvedValue({
      session_token: 'test-token',
      user: { id: 1, email: 'test@example.com', full_name: 'Test User' },
    })

    const { useAuth } = await import('../src/composables/useAuth')
    const { login, currentUser, isAuthenticated } = useAuth()
    const result = await login('test@example.com', 'password')

    expect(result.success).toBe(true)
    expect(currentUser.value).toEqual({ id: 1, email: 'test@example.com', full_name: 'Test User' })
    expect(isAuthenticated.value).toBe(true)
    expect(localStorage.getItem('sessionToken')).toBe('test-token')
  })

  it('should handle login failure with 401 error', async () => {
    const { apiPost, ApiError } = await import('../src/services/api')
    apiPost.mockRejectedValue(new ApiError('Invalid credentials', 401, {}))

    const { useAuth } = await import('../src/composables/useAuth')
    const { login, isAuthenticated } = useAuth()
    const result = await login('test@example.com', 'wrongpassword')

    expect(result.success).toBe(false)
    expect(result.error).toBe('Invalid email or password')
    expect(isAuthenticated.value).toBe(false)
  })

  it('should clear auth state on logout', async () => {
    const { apiPost } = await import('../src/services/api')
    apiPost.mockResolvedValue({})

    localStorage.setItem('sessionToken', 'test-token')
    const { useAuth } = await import('../src/composables/useAuth')
    const { logout, currentUser, isAuthenticated } = useAuth()

    // Manually set state for test
    currentUser.value = { id: 1, email: 'test@example.com' }

    await logout()

    expect(currentUser.value).toBeNull()
    expect(isAuthenticated.value).toBe(false)
    expect(localStorage.getItem('sessionToken')).toBeNull()
  })

  it('should register new user and set auth state', async () => {
    const { apiPost } = await import('../src/services/api')
    apiPost.mockResolvedValue({
      session_token: 'new-token',
      user: { id: 2, email: 'new@example.com', full_name: 'New User' },
    })

    const { useAuth } = await import('../src/composables/useAuth')
    const { register, currentUser, isAuthenticated } = useAuth()
    const result = await register('New User', 'new@example.com', 'password123')

    expect(result.success).toBe(true)
    expect(currentUser.value.email).toBe('new@example.com')
    expect(isAuthenticated.value).toBe(true)
    expect(localStorage.getItem('sessionToken')).toBe('new-token')
  })

  it('should handle registration failure for duplicate email', async () => {
    const { apiPost, ApiError } = await import('../src/services/api')
    apiPost.mockRejectedValue(new ApiError('Email exists', 409, {}))

    const { useAuth } = await import('../src/composables/useAuth')
    const { register } = useAuth()
    const result = await register('Test', 'existing@example.com', 'password')

    expect(result.success).toBe(false)
    expect(result.error).toBe('Email already registered')
  })

  it('should fetch current user when authenticated', async () => {
    const { apiGet } = await import('../src/services/api')
    apiGet.mockResolvedValue({ id: 1, email: 'test@example.com', full_name: 'Test User' })

    localStorage.setItem('sessionToken', 'test-token')
    const { useAuth } = await import('../src/composables/useAuth')
    const { fetchCurrentUser, currentUser } = useAuth()
    const result = await fetchCurrentUser()

    expect(result.success).toBe(true)
    expect(currentUser.value.email).toBe('test@example.com')
  })

  it('should clear auth state when fetching user fails with 401', async () => {
    const { apiGet, ApiError } = await import('../src/services/api')
    apiGet.mockRejectedValue(new ApiError('Unauthorized', 401, {}))

    localStorage.setItem('sessionToken', 'expired-token')
    const { useAuth } = await import('../src/composables/useAuth')
    const { fetchCurrentUser, isAuthenticated } = useAuth()
    const result = await fetchCurrentUser()

    expect(result.success).toBe(false)
    expect(result.error).toBe('Session expired')
    expect(isAuthenticated.value).toBe(false)
    expect(localStorage.getItem('sessionToken')).toBeNull()
  })
})
