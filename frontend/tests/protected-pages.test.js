import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import DashboardView from '../src/views/DashboardView.vue'
import ProfileView from '../src/views/ProfileView.vue'
import { ref } from 'vue'

// Mock the useAuth composable
const mockCurrentUser = ref({ id: 1, full_name: 'John Doe', email: 'john@example.com' })
const mockIsAuthenticated = ref(true)
const mockFetchCurrentUser = vi.fn().mockResolvedValue({ success: true })
const mockLogout = vi.fn()

vi.mock('../src/composables/useAuth', () => ({
  useAuth: () => ({
    currentUser: mockCurrentUser,
    isAuthenticated: mockIsAuthenticated,
    fetchCurrentUser: mockFetchCurrentUser,
    logout: mockLogout,
  }),
}))

// Mock the API service
vi.mock('../src/services/api', () => ({
  apiPut: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  },
}))

describe('Dashboard Page', () => {
  let wrapper
  let router

  beforeEach(() => {
    mockCurrentUser.value = { id: 1, full_name: 'John Doe', email: 'john@example.com' }
    mockIsAuthenticated.value = true
    vi.clearAllMocks()

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/dashboard', component: DashboardView },
        { path: '/profile', component: {} },
        { path: '/login', component: {} },
      ],
    })
  })

  it('should display welcome message with user name', async () => {
    wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Welcome')
    expect(wrapper.text()).toContain('John Doe')
  })

  it('should display pipeline overview content', async () => {
    wrapper = mount(DashboardView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Manage your contacts and track your sales pipeline')
  })
})

describe('Profile Page', () => {
  let wrapper
  let router

  beforeEach(() => {
    mockCurrentUser.value = { id: 1, full_name: 'Jane Smith', email: 'jane@example.com' }
    mockIsAuthenticated.value = true
    vi.clearAllMocks()

    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/profile', component: ProfileView },
        { path: '/dashboard', component: {} },
        { path: '/login', component: {} },
      ],
    })
  })

  it('should display current user information', async () => {
    wrapper = mount(ProfileView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick() // Extra tick for onMounted

    expect(wrapper.text()).toContain('Jane Smith')
    expect(wrapper.text()).toContain('jane@example.com')
  })

  it('should pre-fill form with current user data', async () => {
    wrapper = mount(ProfileView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    const inputs = wrapper.findAll('input')
    const nameInput = inputs.find(input => input.attributes('type') === 'text')
    const emailInput = inputs.find(input => input.attributes('type') === 'email')

    expect(nameInput.element.value).toBe('Jane Smith')
    expect(emailInput.element.value).toBe('jane@example.com')
  })

  it('should show success message after profile update', async () => {
    const { apiPut } = await import('../src/services/api')
    apiPut.mockResolvedValue({
      id: 1,
      full_name: 'Jane Updated',
      email: 'jane@example.com',
      created_at: '2024-01-01',
      updated_at: '2024-01-02',
    })

    wrapper = mount(ProfileView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    const nameInput = wrapper.findAll('input').find(input => input.attributes('type') === 'text')
    await nameInput.setValue('Jane Updated')

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Profile updated successfully')
  })
})
