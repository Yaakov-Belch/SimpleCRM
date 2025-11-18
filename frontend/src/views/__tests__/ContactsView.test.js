import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContactsView from '../ContactsView.vue'
import * as api from '../../services/api'

// Mock router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
}

const mockRoute = {
  query: {}
}

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => mockRoute
}))

vi.mock('../../services/api', () => ({
  getContacts: vi.fn(),
  deleteContact: vi.fn(),
  apiGet: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  }
}))

vi.mock('../../composables/useContacts', () => ({
  useContacts: () => ({
    contacts: { value: [] },
    selectedContact: { value: null },
    isLoading: { value: false },
    error: { value: null },
    pagination: {
      value: {
        page: 1,
        limit: 20,
        total: 0,
        hasMore: false
      }
    },
    fetchContacts: vi.fn(),
    selectContact: vi.fn(),
    clearSelection: vi.fn()
  })
}))

describe('ContactsView - Task Group 5', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    api.getContacts.mockResolvedValue({
      contacts: [],
      pagination: { page: 1, limit: 20, total: 0, hasMore: false }
    })
    api.apiGet.mockResolvedValue({
      stage_counts: {}
    })
  })

  it('renders with equal columns layout (md:grid-cols-2)', () => {
    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    const grid = wrapper.find('.grid')
    expect(grid.classes()).toContain('md:grid-cols-2')
  })

  it('renders with full width container (max-w-full)', () => {
    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    const container = wrapper.find('main')
    expect(container.classes()).toContain('max-w-full')
  })

  it('displays Active/Passive tab buttons', () => {
    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    expect(wrapper.text()).toContain('Active')
    expect(wrapper.text()).toContain('Passive')
  })

  it('defaults to Active tab on page load', () => {
    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    expect(wrapper.vm.activePassiveTab).toBe('Active')
  })

  it('displays stage filter dropdown with All Stages option', () => {
    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect(select.html()).toContain('All Stages')
  })

  it('fetches filter counts on mount', async () => {
    api.apiGet.mockResolvedValue({
      stage_counts: {
        'Lead': 10,
        'Qualified': 5,
        'Proposal': 3,
        'Client': 2
      }
    })

    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    await flushPromises()

    expect(api.apiGet).toHaveBeenCalledWith('/contacts/filter-counts')
  })

  it('displays stage counts in dropdown options', async () => {
    api.apiGet.mockResolvedValue({
      stage_counts: {
        'Lead': 10,
        'Qualified': 5,
        'Proposal': 3,
        'Client': 2
      }
    })

    const wrapper = mount(ContactsView, {
      global: {
        stubs: {
          NavigationBar: true,
          ContactPreview: true,
          ConfirmDialog: true,
          'router-link': true
        }
      }
    })

    await flushPromises()

    const select = wrapper.find('select')
    expect(select.html()).toContain('Lead (10)')
    expect(select.html()).toContain('Qualified (5)')
  })
})
