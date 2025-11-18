import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContactPreview from '../ContactPreview.vue'
import ActivityTimeline from '../ActivityTimeline.vue'
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
    current_pipeline_stage: 'Lead',
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
    expect(wrapper.text()).toContain('https://example.com')
    expect(wrapper.text()).toContain('Test notes')
  })

  it('displays job title and company in header above tabs', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    const header = wrapper.find('.flex-1')
    expect(header.text()).toContain('Manager')
    expect(header.text()).toContain('at')
    expect(header.text()).toContain('Test Company')
  })

  it('displays current pipeline stage badge in header', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    const badge = wrapper.find('.px-3.py-1.rounded-full')
    expect(badge.exists()).toBe(true)
    expect(badge.text()).toBe('Lead')
    expect(badge.classes()).toContain('bg-yellow-100')
    expect(badge.classes()).toContain('text-yellow-800')
  })

  it('does not display StageSelector component in Contact Info tab', async () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    // Switch to Contact Info tab
    const tabs = wrapper.findAll('nav button')
    await tabs[1].trigger('click')

    await wrapper.vm.$nextTick()

    // StageSelector component should not be imported or rendered
    const contactInfoDiv = wrapper.find('[class="space-y-4"]')
    expect(contactInfoDiv.exists()).toBe(true)

    // Check that there's no label for Pipeline Stage
    const labels = wrapper.findAll('label')
    const hasStageLabel = labels.some(label => label.text().includes('Pipeline Stage'))
    expect(hasStageLabel).toBe(false)
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

  it('formats job title and company correctly when both exist', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    const jobCompanyDiv = wrapper.find('.text-sm.text-gray-600')
    expect(jobCompanyDiv.text()).toContain('Manager at Test Company')
  })

  it('displays only company when job title is missing', () => {
    const contactWithoutTitle = { ...mockContact, job_title: null }
    const wrapper = mount(ContactPreview, {
      props: {
        contact: contactWithoutTitle
      }
    })

    const jobCompanyDiv = wrapper.find('.text-sm.text-gray-600')
    expect(jobCompanyDiv.text()).toContain('Test Company')
    expect(jobCompanyDiv.text()).not.toContain(' at ')
  })

  it('links company to website when website exists', () => {
    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    const companyLink = wrapper.find('a[href="https://example.com"]')
    expect(companyLink.exists()).toBe(true)
    expect(companyLink.text()).toBe('Test Company')
    expect(companyLink.attributes('target')).toBe('_blank')
  })

  it('displays company as plain text when no website', () => {
    const contactWithoutWebsite = { ...mockContact, website: null }
    const wrapper = mount(ContactPreview, {
      props: {
        contact: contactWithoutWebsite
      }
    })

    const jobCompanyDiv = wrapper.find('.text-sm.text-gray-600')
    expect(jobCompanyDiv.text()).toContain('Test Company')
    // Should not be a link
    const companyLinks = wrapper.findAll('a').filter(link => link.text() === 'Test Company')
    expect(companyLinks.length).toBe(0)
  })
})
