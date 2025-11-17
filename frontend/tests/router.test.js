import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'

// Mock components
const LoginView = { template: '<div>Login</div>' }
const RegisterView = { template: '<div>Register</div>' }
const DashboardView = { template: '<div>Dashboard</div>' }
const ProfileView = { template: '<div>Profile</div>' }

describe('Router Guards', () => {
  let router
  let mockUseAuth

  beforeEach(() => {
    vi.resetModules()

    // Default mock - unauthenticated
    mockUseAuth = {
      isAuthenticated: { value: false },
      currentUser: { value: null },
    }

    vi.mock('../src/composables/useAuth', () => ({
      useAuth: () => mockUseAuth,
    }))

    // Create router with same structure as actual router
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

    // Apply the same guard logic as actual router
    router.beforeEach((to, from, next) => {
      const { isAuthenticated } = mockUseAuth

      if (to.meta.requiresAuth && !isAuthenticated.value) {
        next('/login')
      } else if (to.meta.public && isAuthenticated.value) {
        next('/dashboard')
      } else {
        next()
      }
    })
  })

  it('should redirect unauthenticated users from protected route to login', async () => {
    mockUseAuth.isAuthenticated.value = false

    await router.push('/dashboard')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should allow authenticated users to access protected routes', async () => {
    mockUseAuth.isAuthenticated.value = true
    mockUseAuth.currentUser.value = { id: 1, email: 'test@example.com' }

    await router.push('/dashboard')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('should redirect authenticated users from login page to dashboard', async () => {
    mockUseAuth.isAuthenticated.value = true
    mockUseAuth.currentUser.value = { id: 1, email: 'test@example.com' }

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('should redirect authenticated users from register page to dashboard', async () => {
    mockUseAuth.isAuthenticated.value = true
    mockUseAuth.currentUser.value = { id: 1, email: 'test@example.com' }

    await router.push('/register')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('should allow unauthenticated users to access public routes', async () => {
    mockUseAuth.isAuthenticated.value = false

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should redirect unauthenticated users from profile to login', async () => {
    mockUseAuth.isAuthenticated.value = false

    await router.push('/profile')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should allow authenticated users to access profile', async () => {
    mockUseAuth.isAuthenticated.value = true
    mockUseAuth.currentUser.value = { id: 1, email: 'test@example.com' }

    await router.push('/profile')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/profile')
  })
})
