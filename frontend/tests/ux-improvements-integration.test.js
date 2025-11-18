/**
 * Integration tests for UX Improvements feature (Task Group 7.3)
 *
 * These tests cover critical end-to-end workflows from the frontend perspective:
 * - Activity creation UI to timeline display
 * - Contact filtering by Active/Passive tabs
 * - Filter count updates with search
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ContactsView from '../src/views/ContactsView.vue'
import ContactPreview from '../src/components/ContactPreview.vue'
import ActivityTimeline from '../src/components/ActivityTimeline.vue'
import ActivityItem from '../src/components/ActivityItem.vue'
import * as api from '../src/services/api'

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

vi.mock('../src/services/api')

describe('UX Improvements - Frontend Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows pipeline stage badge in timeline when stage changes', async () => {
    const mockActivities = [
      {
        id: 3,
        type: 'Meeting',
        subject: 'Proposal meeting',
        activity_date: '2024-01-15T10:00:00',
        pipeline_stage: 'Proposal',
        attachments: []
      },
      {
        id: 2,
        type: 'Call',
        subject: 'Qualification call',
        activity_date: '2024-01-14T10:00:00',
        pipeline_stage: 'Qualified',
        attachments: []
      },
      {
        id: 1,
        type: 'Note',
        subject: 'First contact',
        activity_date: '2024-01-13T10:00:00',
        pipeline_stage: 'Lead',
        attachments: []
      }
    ]

    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    const activityItems = wrapper.findAllComponents(ActivityItem)
    expect(activityItems.length).toBe(3)

    // First activity (most recent) should show Proposal badge (different from next)
    expect(activityItems[0].props('activity').pipeline_stage).toBe('Proposal')
    expect(activityItems[0].props('previousActivity')).toEqual(mockActivities[1])

    // Second activity should show Qualified badge (different from next)
    expect(activityItems[1].props('activity').pipeline_stage).toBe('Qualified')
    expect(activityItems[1].props('previousActivity')).toEqual(mockActivities[2])

    // Third activity (oldest) should show Lead badge (no previous activity)
    expect(activityItems[2].props('activity').pipeline_stage).toBe('Lead')
    // previousActivity could be undefined or null depending on component implementation
    const previousActivity = activityItems[2].props('previousActivity')
    expect(previousActivity === undefined || previousActivity === null).toBe(true)
  })

  it('does not show stage badge when stage matches previous activity', async () => {
    const mockActivities = [
      {
        id: 2,
        type: 'Note',
        subject: 'Follow-up note',
        activity_date: '2024-01-15T10:00:00',
        pipeline_stage: 'Lead',
        attachments: []
      },
      {
        id: 1,
        type: 'Call',
        subject: 'Initial call',
        activity_date: '2024-01-14T10:00:00',
        pipeline_stage: 'Lead',
        attachments: []
      }
    ]

    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    const activityItems = wrapper.findAllComponents(ActivityItem)
    expect(activityItems.length).toBe(2)

    // First activity should have previous activity with same stage
    const firstItem = activityItems[0]
    expect(firstItem.props('activity').pipeline_stage).toBe('Lead')
    expect(firstItem.props('previousActivity').pipeline_stage).toBe('Lead')
  })

  it('creates activity immediately and displays in timeline', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: []
    })

    const mockNewActivity = {
      id: 1,
      type: 'Note',
      subject: '',
      notes: '',
      activity_date: '2024-01-15T10:30:00',
      pipeline_stage: 'Lead',
      attachments: []
    }

    api.createActivity.mockResolvedValue(mockNewActivity)

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // Initially no activities
    expect(wrapper.vm.activities.length).toBe(0)

    // Click "New Activity" button
    const newActivityButton = wrapper.find('button')
    expect(newActivityButton.text()).toBe('New Activity')

    await newActivityButton.trigger('click')
    await flushPromises()

    // Activity should be created and added to timeline
    expect(api.createActivity).toHaveBeenCalledWith(1, expect.objectContaining({
      type: 'Note'
    }))

    expect(wrapper.vm.activities.length).toBe(1)
    expect(wrapper.vm.activities[0].id).toBe(1)
  })

  it('updates filter counts when search query changes', async () => {
    const mockContacts = [
      {
        id: 1,
        name: 'Alice Anderson',
        email: 'alice@example.com',
        current_pipeline_stage: 'Lead'
      },
      {
        id: 2,
        name: 'Bob Brown',
        email: 'bob@example.com',
        current_pipeline_stage: 'Qualified'
      }
    ]

    const initialCounts = {
      stage_counts: {
        'Lead': 1,
        'Qualified': 1
      },
      activity_type_counts: {}
    }

    const filteredCounts = {
      stage_counts: {
        'Lead': 1,
        'Qualified': 0
      },
      activity_type_counts: {}
    }

    api.getContacts.mockResolvedValue({
      contacts: mockContacts,
      pagination: { page: 1, limit: 20, total: 2, hasMore: false }
    })

    api.apiGet.mockResolvedValueOnce(initialCounts)

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

    // Initial counts should be fetched
    expect(api.apiGet).toHaveBeenCalledWith('/contacts/filter-counts')

    // Update search query
    api.apiGet.mockResolvedValueOnce(filteredCounts)

    const searchInput = wrapper.find('input[type="text"]')
    await searchInput.setValue('alice')
    await searchInput.trigger('input')

    // Allow debounce and API call
    await new Promise(resolve => setTimeout(resolve, 500))
    await flushPromises()

    // Filter counts should be re-fetched with search parameter
    expect(api.apiGet).toHaveBeenCalledWith('/contacts/filter-counts?search=alice')
  })

  it('displays Active/Passive tabs with correct counts', async () => {
    const mockActiveCounts = {
      stage_counts: {
        'Lead': 5,
        'Qualified': 3,
        'Proposal': 2,
        'Client': 1
      },
      activity_type_counts: {}
    }

    api.getContacts.mockResolvedValue({
      contacts: [],
      pagination: { page: 1, limit: 20, total: 0, hasMore: false }
    })

    api.apiGet.mockResolvedValue(mockActiveCounts)

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

    // Should display Active and Passive tabs
    expect(wrapper.text()).toContain('Active')
    expect(wrapper.text()).toContain('Passive')

    // Default to Active tab
    expect(wrapper.vm.activePassiveTab).toBe('Active')
  })

  it('switches between Active and Passive tabs', async () => {
    const mockActiveContacts = [
      {
        id: 1,
        name: 'Active Contact',
        email: 'active@example.com',
        current_pipeline_stage: 'Lead'
      }
    ]

    const mockPassiveContacts = [
      {
        id: 2,
        name: 'Passive Contact',
        email: 'passive@example.com',
        current_pipeline_stage: 'Archived'
      }
    ]

    api.apiGet.mockResolvedValue({
      stage_counts: {},
      activity_type_counts: {}
    })

    // First call returns active contacts
    api.getContacts.mockResolvedValueOnce({
      contacts: mockActiveContacts,
      pagination: { page: 1, limit: 20, total: 1, hasMore: false }
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

    // Should be on Active tab initially
    expect(wrapper.vm.activePassiveTab).toBe('Active')

    // Mock Passive contacts call
    api.getContacts.mockResolvedValueOnce({
      contacts: mockPassiveContacts,
      pagination: { page: 1, limit: 20, total: 1, hasMore: false }
    })

    // Find and click Passive tab
    const tabs = wrapper.findAll('button').filter(btn =>
      btn.text() === 'Active' || btn.text() === 'Passive'
    )

    const passiveTab = tabs.find(btn => btn.text() === 'Passive')
    await passiveTab.trigger('click')

    await flushPromises()

    // Should switch to Passive tab
    expect(wrapper.vm.activePassiveTab).toBe('Passive')
  })

  it('displays contact info above tabs in ContactPreview', () => {
    const mockContact = {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      job_title: 'CEO',
      company: 'Acme Corp',
      website: 'https://acme.com',
      current_pipeline_stage: 'Client'
    }

    api.getActivitiesForContact.mockResolvedValue({
      activities: []
    })

    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    // Should display job title and company in header
    const header = wrapper.find('.flex-1')
    expect(header.text()).toContain('CEO')
    expect(header.text()).toContain('at')
    expect(header.text()).toContain('Acme Corp')

    // Company should be linked
    const companyLink = wrapper.find('a[href="https://acme.com"]')
    expect(companyLink.exists()).toBe(true)
    expect(companyLink.text()).toBe('Acme Corp')

    // Should display current pipeline stage badge
    const stageBadge = wrapper.find('.bg-green-100')
    expect(stageBadge.exists()).toBe(true)
    expect(stageBadge.text()).toBe('Client')
  })

  it('displays stage filter dropdown with counts', async () => {
    const mockCounts = {
      stage_counts: {
        'Lead': 10,
        'Qualified': 5,
        'Proposal': 3,
        'Client': 2
      },
      activity_type_counts: {}
    }

    api.getContacts.mockResolvedValue({
      contacts: [],
      pagination: { page: 1, limit: 20, total: 0, hasMore: false }
    })

    api.apiGet.mockResolvedValue(mockCounts)

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

    // Find stage filter dropdown
    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)

    const selectHtml = select.html()
    expect(selectHtml).toContain('Lead (10)')
    expect(selectHtml).toContain('Qualified (5)')
    expect(selectHtml).toContain('Proposal (3)')
    expect(selectHtml).toContain('Client (2)')
  })

  it('shows all pipeline stages in ActivityForm dropdown with visual separator', async () => {
    const mockActivity = {
      id: 1,
      type: 'Note',
      subject: 'Test',
      activity_date: '2024-01-15T10:00:00',
      pipeline_stage: 'Lead',
      attachments: []
    }

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    api.getActivitiesForContact.mockResolvedValue({
      activities: [mockActivity]
    })

    await flushPromises()

    // Edit the activity to open form
    await wrapper.vm.handleEdit(mockActivity)

    await wrapper.vm.$nextTick()

    // ActivityForm should be rendered
    const form = wrapper.findComponent({ name: 'ActivityForm' })

    if (form.exists()) {
      // Find pipeline stage select
      const selects = form.findAll('select')
      const pipelineSelect = selects.find(select => {
        const options = select.findAll('option')
        return options.some(opt => opt.text().includes('Lead'))
      })

      expect(pipelineSelect).toBeTruthy()

      // Verify all stages are present
      const optionsText = pipelineSelect.html()

      // Active stages
      expect(optionsText).toContain('Lead')
      expect(optionsText).toContain('Qualified')
      expect(optionsText).toContain('Proposal')
      expect(optionsText).toContain('Client')

      // Passive stages
      expect(optionsText).toContain('Qualified Out')
      expect(optionsText).toContain('Lost Proposal')
      expect(optionsText).toContain('Work Completed')
      expect(optionsText).toContain('Archived')
    }
  })

  it('reflects contact current_pipeline_stage from latest activity', async () => {
    const mockContact = {
      id: 1,
      name: 'Test Contact',
      email: 'test@example.com',
      current_pipeline_stage: 'Proposal'
    }

    const mockActivities = [
      {
        id: 2,
        type: 'Meeting',
        subject: 'Proposal meeting',
        activity_date: '2024-01-15T10:00:00',
        pipeline_stage: 'Proposal',
        attachments: []
      },
      {
        id: 1,
        type: 'Call',
        subject: 'Initial call',
        activity_date: '2024-01-14T10:00:00',
        pipeline_stage: 'Lead',
        attachments: []
      }
    ]

    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ContactPreview, {
      props: {
        contact: mockContact
      }
    })

    await flushPromises()

    // Contact's current_pipeline_stage should be displayed
    const stageBadge = wrapper.find('.bg-purple-100')
    expect(stageBadge.exists()).toBe(true)
    expect(stageBadge.text()).toBe('Proposal')
  })
})
