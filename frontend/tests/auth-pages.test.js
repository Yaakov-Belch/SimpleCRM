import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import RegisterView from '../src/views/RegisterView.vue'
import LoginView from '../src/views/LoginView.vue'

// Mock the useAuth composable
vi.mock('../src/composables/useAuth', () => ({
  useAuth: vi.fn(() => ({
    register: vi.fn(),
    login: vi.fn(),
    isAuthenticated: { value: false },
    currentUser: { value: null },
  })),
}))

describe('Registration Page', () => {
  let wrapper
  let router

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/register', component: RegisterView },
        { path: '/login', component: {} },
        { path: '/dashboard', component: {} },
      ],
    })
  })

  it('should render registration form with all fields', async () => {
    wrapper = mount(RegisterView, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.findAll('input[type="email"]').length).toBeGreaterThan(0)
    expect(wrapper.findAll('input[type="password"]').length).toBeGreaterThan(0)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('should show validation error when full name is empty', async () => {
    wrapper = mount(RegisterView, {
      global: {
        plugins: [router],
      },
    })

    const fullNameInput = wrapper.find('input[type="text"]')
    await fullNameInput.setValue('')
    await fullNameInput.trigger('blur')

    // Wait for validation to run
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Full name is required')
  })

  it('should show validation error for password less than 8 characters', async () => {
    wrapper = mount(RegisterView, {
      global: {
        plugins: [router],
      },
    })

    const passwordInput = wrapper.find('input[type="password"]')
    await passwordInput.setValue('short')
    await passwordInput.trigger('blur')

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('Password must be at least 8 characters')
  })

  it('should call register function when form is submitted with valid data', async () => {
    const mockRegister = vi.fn().mockResolvedValue({ success: true, user: {} })
    const { useAuth } = await import('../src/composables/useAuth')
    useAuth.mockReturnValue({
      register: mockRegister,
      isAuthenticated: { value: false },
      currentUser: { value: null },
    })

    wrapper = mount(RegisterView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.find('input[type="text"]').setValue('John Doe')
    await wrapper.find('input[type="email"]').setValue('john@example.com')
    await wrapper.find('input[type="password"]').setValue('password123')

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(mockRegister).toHaveBeenCalledWith('John Doe', 'john@example.com', 'password123')
  })
})

describe('Login Page', () => {
  let wrapper
  let router

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: LoginView },
        { path: '/register', component: {} },
        { path: '/dashboard', component: {} },
      ],
    })
  })

  it('should render login form with email and password fields', async () => {
    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.findAll('input[type="email"]').length).toBeGreaterThan(0)
    expect(wrapper.findAll('input[type="password"]').length).toBeGreaterThan(0)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('should show validation error for invalid email format', async () => {
    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    const emailInput = wrapper.find('input[type="email"]')
    await emailInput.setValue('invalidemail')
    await emailInput.trigger('blur')

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('valid email')
  })

  it('should call login function when form is submitted with valid data', async () => {
    const mockLogin = vi.fn().mockResolvedValue({ success: true, user: {} })
    const { useAuth } = await import('../src/composables/useAuth')
    useAuth.mockReturnValue({
      login: mockLogin,
      isAuthenticated: { value: false },
      currentUser: { value: null },
    })

    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('password123')

    await wrapper.find('form').trigger('submit')
    await wrapper.vm.$nextTick()

    expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('should display error message when login fails', async () => {
    const mockLogin = vi.fn().mockResolvedValue({ success: false, error: 'Invalid credentials' })
    const { useAuth } = await import('../src/composables/useAuth')
    useAuth.mockReturnValue({
      login: mockLogin,
      isAuthenticated: { value: false },
      currentUser: { value: null },
    })

    wrapper = mount(LoginView, {
      global: {
        plugins: [router],
      },
    })

    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('input[type="password"]').setValue('wrongpassword')
    await wrapper.find('form').trigger('submit')

    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick() // Extra tick for state update

    expect(wrapper.text()).toContain('Invalid credentials')
  })
})
