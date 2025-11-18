import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContactPreview from '../ContactPreview.vue'
import ActivityTimeline from '../ActivityTimeline.vue'
import StageSelector from '../StageSelector.vue'
import * as api from '../../services/api'

vi.mock('../../services/api', () => ({
  getActivitiesForContact: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  }
}))

describe('ContactPreview', () => {
  const mockContact = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    company: 'Test Company',
    job_title: 'Manager',
    website: 'https://example.com',
    notes: 'Test notes',
    pipeline_stage: 'Lead',
    created_at: '2024-01-01T00:00:00',
    updated_at: '2024-01-02T00:00:00'
  }

  beforeEach(() => {
    vi.clearAllMocks()
    api.getActivitiesForContact.mockResolvedValue({ activities: [] })
  })

  it('renders with contact data', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    expect(wrapper.text()).toContain('John Doe')
  })

  it('displays Timeline tab as default', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.activeTab).toBe('timeline')
    expect(wrapper.findComponent(ActivityTimeline).exists()).toBe(true)
  })

  it('shows both Timeline and Contact Info tabs', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    const tabs = wrapper.findAll('nav button')
    expect(tabs.length).toBe(2)
    expect(tabs[0].text()).toBe('Timeline')
    expect(tabs[1].text()).toBe('Contact Info')
  })

  it('switches between tabs when clicked', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    await wrapper.vm.$nextTick()

    // Initially on Timeline tab
    expect(wrapper.vm.activeTab).toBe('timeline')

    // Click Contact Info tab
    const tabs = wrapper.findAll('nav button')
    await tabs[1].trigger('click')

    expect(wrapper.vm.activeTab).toBe('contact-info')

    // Contact info should be visible
    expect(wrapper.text()).toContain('john@example.com')
    expect(wrapper.text()).toContain('123-456-7890')

    // Click back to Timeline tab
    await tabs[0].trigger('click')

    expect(wrapper.vm.activeTab).toBe('timeline')
  })

  it('displays contact info fields in Contact Info tab', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    // Switch to Contact Info tab
    const tabs = wrapper.findAll('nav button')
    await tabs[1].trigger('click')

    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('john@example.com')
    expect(wrapper.text()).toContain('123-456-7890')
    expect(wrapper.text()).toContain('Test Company')
    expect(wrapper.text()).toContain('Manager')
    expect(wrapper.text()).toContain('https://example.com')
    expect(wrapper.text()).toContain('Test notes')
  })

  it('renders ActivityTimeline component with contact ID', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    await wrapper.vm.$nextTick()

    const activityTimeline = wrapper.findComponent(ActivityTimeline)
    expect(activityTimeline.exists()).toBe(true)
    expect(activityTimeline.props('contactId')).toBe(1)
  })

  it('resets to Timeline tab when contact changes', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    // Switch to Contact Info tab
    const tabs = wrapper.findAll('nav button')
    await tabs[1].trigger('click')
    expect(wrapper.vm.activeTab).toBe('contact-info')

    // Change contact
    const newContact = { ...mockContact, id: 2, name: 'Jane Doe' }
    await wrapper.setProps({ contact: newContact })

    // Should reset to Timeline tab
    expect(wrapper.vm.activeTab).toBe('timeline')
  })

  it('emits edit and delete events', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    const buttons = wrapper.findAll('button').filter(btn =>
      btn.text() === 'Edit' || btn.text() === 'Delete'
    )

    const editButton = buttons.find(btn => btn.text() === 'Edit')
    const deleteButton = buttons.find(btn => btn.text() === 'Delete')

    await editButton.trigger('click')
    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0]).toEqual([mockContact])

    await deleteButton.trigger('click')
    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0]).toEqual([mockContact])
  })

  it('displays empty state when no contact is provided', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: null
      }
    })

    expect(wrapper.text()).toContain('Select a contact to view details')
  })
})
