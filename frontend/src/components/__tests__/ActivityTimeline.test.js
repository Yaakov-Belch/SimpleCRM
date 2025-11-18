import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ActivityTimeline from '../ActivityTimeline.vue'
import ActivityItem from '../ActivityItem.vue'
import ActivityForm from '../ActivityForm.vue'
import * as api from '../../services/api'

vi.mock('../../services/api', () => ({
  getActivitiesForContact: vi.fn(),
  deleteActivity: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  }
}))

describe('ActivityTimeline', () => {
  const mockActivities = [
    {
      id: 1,
      type: 'Call',
      subject: 'Follow-up call',
      notes: 'Discussed project',
      activity_date: '2024-01-15T10:30:00',
      attachments: []
    },
    {
      id: 2,
      type: 'Meeting',
      subject: 'Initial meeting',
      notes: 'Met with client',
      activity_date: '2024-01-14T09:00:00',
      attachments: []
    },
    {
      id: 3,
      type: 'Email',
      subject: 'Proposal sent',
      notes: 'Sent proposal document',
      activity_date: '2024-01-13T15:00:00',
      attachments: []
    }
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches and displays activities on mount', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    expect(api.getActivitiesForContact).toHaveBeenCalledWith(1)
    expect(wrapper.findAllComponents(ActivityItem).length).toBe(3)
  })

  it('shows loading=true state initially', () => {
    api.getActivitiesForContact.mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    // Check loading state immediately (before promise resolves)
    expect(wrapper.vm.loading).toBe(true)
  })

  it('displays empty state when no activities', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: []
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    expect(wrapper.text()).toContain('No activities yet')
  })

  it('filters activities by type', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // All activities shown initially
    expect(wrapper.findAllComponents(ActivityItem).length).toBe(3)

    // Filter by Call
    const typeSelect = wrapper.find('select')
    await typeSelect.setValue('Call')

    expect(wrapper.findAllComponents(ActivityItem).length).toBe(1)
    expect(wrapper.text()).toContain('Follow-up call')
  })

  it('searches activities by content', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // Search for "proposal"
    const searchInput = wrapper.find('input[type="text"]')
    await searchInput.setValue('proposal')
    await searchInput.trigger('input')

    expect(wrapper.findAllComponents(ActivityItem).length).toBe(1)
    expect(wrapper.text()).toContain('Proposal sent')
  })

  it('sorts activities by date descending', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    const items = wrapper.findAllComponents(ActivityItem)
    const subjects = items.map(item => item.props('activity').subject)

    // Most recent first
    expect(subjects[0]).toBe('Follow-up call')
    expect(subjects[1]).toBe('Initial meeting')
    expect(subjects[2]).toBe('Proposal sent')
  })

  it('opens activity form when Add Activity button is clicked', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: []
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    const addButton = wrapper.find('button')
    await addButton.trigger('click')

    expect(wrapper.findComponent(ActivityForm).exists()).toBe(true)
  })

  it('handles activity edit event', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: mockActivities
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    const firstItem = wrapper.findComponent(ActivityItem)
    await firstItem.vm.$emit('edit', mockActivities[0])

    expect(wrapper.findComponent(ActivityForm).exists()).toBe(true)
    expect(wrapper.findComponent(ActivityForm).props('activity')).toEqual(mockActivities[0])
  })

  it('handles activity delete event', async () => {
    global.confirm = vi.fn(() => true)
    api.getActivitiesForContact.mockResolvedValue({
      activities: [...mockActivities] // Use a copy
    })
    api.deleteActivity.mockResolvedValue(null)

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // Initially 3 activities
    expect(wrapper.vm.activities.length).toBe(3)

    const activityIdToDelete = wrapper.vm.activities[0].id

    // Trigger delete through the handleDelete method
    await wrapper.vm.handleDelete(activityIdToDelete)

    await flushPromises()

    expect(api.deleteActivity).toHaveBeenCalledWith(activityIdToDelete)

    // Check activity was removed
    expect(wrapper.vm.activities.length).toBe(2)
  })

  it('adds new activity to timeline when saved', async () => {
    api.getActivitiesForContact.mockResolvedValue({
      activities: []
    })

    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // Open form
    const addButton = wrapper.find('button')
    await addButton.trigger('click')

    // Simulate activity saved
    const newActivity = {
      id: 4,
      type: 'Note',
      subject: 'New note',
      notes: 'Content',
      activity_date: '2024-01-16T12:00:00',
      attachments: []
    }

    const form = wrapper.findComponent(ActivityForm)
    await form.vm.$emit('saved', newActivity)

    await wrapper.vm.$nextTick()

    expect(wrapper.vm.activities.length).toBe(1)
    expect(wrapper.vm.activities[0]).toEqual(newActivity)
  })

  // CRITICAL TEST: Prop reactivity (prevents regression of the bug)
  it('re-fetches activities when contactId prop changes', async () => {
    const contact1Activities = [
      {
        id: 1,
        type: 'Call',
        subject: 'Contact 1 activity',
        notes: 'For contact 1',
        activity_date: '2024-01-15T10:30:00',
        attachments: []
      }
    ]

    const contact2Activities = [
      {
        id: 2,
        type: 'Meeting',
        subject: 'Contact 2 activity',
        notes: 'For contact 2',
        activity_date: '2024-01-16T10:30:00',
        attachments: []
      }
    ]

    // Mock API to return different data based on contactId
    api.getActivitiesForContact.mockImplementation((contactId) => {
      if (contactId === 1) {
        return Promise.resolve({ activities: contact1Activities })
      } else if (contactId === 2) {
        return Promise.resolve({ activities: contact2Activities })
      }
      return Promise.resolve({ activities: [] })
    })

    // Mount with contactId: 1
    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // Verify first fetch
    expect(api.getActivitiesForContact).toHaveBeenCalledWith(1)
    expect(wrapper.vm.activities.length).toBe(1)
    expect(wrapper.vm.activities[0].subject).toBe('Contact 1 activity')

    // Change contactId prop to 2
    await wrapper.setProps({ contactId: 2 })
    await flushPromises()

    // Verify second fetch
    expect(api.getActivitiesForContact).toHaveBeenCalledWith(2)
    expect(api.getActivitiesForContact).toHaveBeenCalledTimes(2)
    expect(wrapper.vm.activities.length).toBe(1)
    expect(wrapper.vm.activities[0].subject).toBe('Contact 2 activity')
  })

  // TEST: Stale data doesn't persist after contact change
  it('shows correct activities after changing contact (no stale data)', async () => {
    const contact1Activities = [
      {
        id: 1,
        type: 'Call',
        subject: 'Contact 1 activity',
        notes: 'For contact 1',
        activity_date: '2024-01-15T10:30:00',
        attachments: []
      }
    ]

    const contact2Activities = [
      {
        id: 2,
        type: 'Email',
        subject: 'Contact 2 activity',
        notes: 'For contact 2',
        activity_date: '2024-01-16T10:30:00',
        attachments: []
      }
    ]

    // First call returns contact1Activities
    api.getActivitiesForContact.mockResolvedValueOnce({
      activities: contact1Activities
    })

    // Mount with contactId: 1
    const wrapper = mount(ActivityTimeline, {
      props: {
        contactId: 1
      }
    })

    await flushPromises()

    // Verify activities for contact 1
    expect(wrapper.vm.activities.length).toBe(1)
    expect(wrapper.vm.activities[0].subject).toBe('Contact 1 activity')

    // Second call returns contact2Activities
    api.getActivitiesForContact.mockResolvedValueOnce({
      activities: contact2Activities
    })

    // Change contact to 2
    await wrapper.setProps({ contactId: 2 })
    await flushPromises()

    // After fetch completes, should show only contact 2 activities (no stale data from contact 1)
    expect(wrapper.vm.activities.length).toBe(1)
    expect(wrapper.vm.activities[0].subject).toBe('Contact 2 activity')
    expect(wrapper.text()).toContain('Contact 2 activity')
    expect(wrapper.text()).not.toContain('Contact 1 activity')
  })
})
