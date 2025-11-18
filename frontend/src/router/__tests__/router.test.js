import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { useAuth } from '../../composables/useAuth'
import LoginView from '../../views/LoginView.vue'
import RegisterView from '../../views/RegisterView.vue'
import DashboardView from '../../views/DashboardView.vue'
import ProfileView from '../../views/ProfileView.vue'
import ContactsView from '../../views/ContactsView.vue'
import ContactCreateView from '../../views/ContactCreateView.vue'
import ContactEditView from '../../views/ContactEditView.vue'

vi.mock('../../composables/useAuth', () => ({
  useAuth: vi.fn()
}))

describe('Router Configuration', () => {
  let router

  const createTestRouter = () => {
    const routes = [
      {
        path: '/',
        redirect: '/contacts',
      },
      {
        path: '/login',
        name: 'Login',
        component: LoginView,
        meta: { public: true },
      },
      {
        path: '/register',
        name: 'Register',
        component: RegisterView,
        meta: { public: true },
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: DashboardView,
        meta: { requiresAuth: true },
      },
      {
        path: '/profile',
        name: 'Profile',
        component: ProfileView,
        meta: { requiresAuth: true },
      },
      {
        path: '/contacts',
        name: 'Contacts',
        component: ContactsView,
        meta: { requiresAuth: true },
      },
      {
        path: '/contacts/new',
        name: 'ContactCreate',
        component: ContactCreateView,
        meta: { requiresAuth: true },
      },
      {
        path: '/contacts/:id/edit',
        name: 'ContactEdit',
        component: ContactEditView,
        meta: { requiresAuth: true },
      },
    ]

    const testRouter = createRouter({
      history: createMemoryHistory(),
      routes,
    })

    // Add route guard
    testRouter.beforeEach((to, from, next) => {
      const { isAuthenticated } = useAuth()

      // Check if route requires authentication
      if (to.meta.requiresAuth && !isAuthenticated.value) {
        // Redirect to login if not authenticated
        next('/login')
      } else if (to.meta.public && isAuthenticated.value) {
        // Redirect to contacts if already authenticated and trying to access public routes
        next('/contacts')
      } else {
        // Allow navigation
        next()
      }
    })

    return testRouter
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('redirects root path "/" to "/contacts"', async () => {
    useAuth.mockReturnValue({
      isAuthenticated: { value: true }
    })

    router = createTestRouter()

    await router.push('/')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/contacts')
  })

  it('redirects authenticated user on public route to "/contacts"', async () => {
    useAuth.mockReturnValue({
      isAuthenticated: { value: true }
    })

    router = createTestRouter()

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/contacts')
  })

  it('redirects authenticated user from register page to "/contacts"', async () => {
    useAuth.mockReturnValue({
      isAuthenticated: { value: true }
    })

    router = createTestRouter()

    await router.push('/register')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/contacts')
  })

  it('allows unauthenticated user to access login page', async () => {
    useAuth.mockReturnValue({
      isAuthenticated: { value: false }
    })

    router = createTestRouter()

    await router.push('/login')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redirects unauthenticated user from protected route to "/login"', async () => {
    useAuth.mockReturnValue({
      isAuthenticated: { value: false }
    })

    router = createTestRouter()

    await router.push('/contacts')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('allows authenticated user to access contacts page', async () => {
    useAuth.mockReturnValue({
      isAuthenticated: { value: true }
    })

    router = createTestRouter()

    await router.push('/contacts')
    await router.isReady()

    expect(router.currentRoute.value.path).toBe('/contacts')
  })
})
