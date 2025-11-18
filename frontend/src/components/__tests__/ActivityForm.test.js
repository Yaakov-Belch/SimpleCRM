import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ActivityForm from '../ActivityForm.vue'
import MarkdownEditor from '../MarkdownEditor.vue'
import * as api from '../../services/api'

vi.mock('../../services/api', () => ({
  createActivity: vi.fn(),
  updateActivity: vi.fn(),
  deleteActivity: vi.fn(),
  uploadAttachment: vi.fn(),
  deleteAttachment: vi.fn(),
  ApiError: class ApiError extends Error {
    constructor(message, status, data) {
      super(message)
      this.status = status
      this.data = data
    }
  }
}))

describe('ActivityForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders form with all required fields', () => {
    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    expect(wrapper.find('select').exists()).toBe(true) // Activity type
    expect(wrapper.findAll('input[type="text"]').length).toBeGreaterThan(0) // Subject
    expect(wrapper.find('input[type="datetime-local"]').exists()).toBe(true) // Date
    expect(wrapper.findComponent(MarkdownEditor).exists()).toBe(true) // Notes
  })

  it('shows validation errors for required fields', async () => {
    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    // Clear required fields
    await wrapper.findAll('select')[0].setValue('')  // Clear type
    await wrapper.find('input[type="datetime-local"]').setValue('')  // Clear date

    // Submit form without filling required fields
    await wrapper.find('form').trigger('submit.prevent')

    expect(wrapper.text()).toContain('Activity type is required')
    expect(wrapper.text()).toContain('Activity date is required')
  })

  it('validates subject max length', async () => {
    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    const subjectInput = wrapper.find('input[type="text"]')
    await subjectInput.setValue('a'.repeat(300))
    await subjectInput.trigger('blur')

    expect(wrapper.text()).toContain('must be 255 characters or less')
  })

  it('creates new activity when form is submitted', async () => {
    const mockActivity = {
      id: 1,
      type: 'Call',
      subject: 'Test call',
      activity_date: '2024-01-15T10:30:00',
      notes: 'Test notes'
    }

    api.createActivity.mockResolvedValue(mockActivity)

    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    // Fill form
    await wrapper.findAll('select')[0].setValue('Call')
    await wrapper.find('input[type="text"]').setValue('Test call')
    await wrapper.find('input[type="datetime-local"]').setValue('2024-01-15T10:30')

    // Submit
    await wrapper.find('form').trigger('submit.prevent')

    expect(api.createActivity).toHaveBeenCalledWith(1, expect.objectContaining({
      type: 'Call',
      subject: 'Test call'
    }))

    await flushPromises()
    expect(wrapper.emitted('saved')).toBeTruthy()
    expect(wrapper.emitted('saved')[0]).toEqual([mockActivity])
  })

  it('updates existing activity when editing', async () => {
    const existingActivity = {
      id: 1,
      type: 'Meeting',
      subject: 'Original subject',
      activity_date: '2024-01-15T10:30:00',
      notes: 'Original notes',
      attachments: []
    }

    const updatedActivity = {
      ...existingActivity,
      subject: 'Updated subject'
    }

    api.updateActivity.mockResolvedValue(updatedActivity)

    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1,
        activity: existingActivity
      }
    })

    await wrapper.vm.$nextTick()

    // Verify form is pre-filled
    expect(wrapper.vm.formData.type).toBe('Meeting')
    expect(wrapper.vm.formData.subject).toBe('Original subject')

    // Update subject
    await wrapper.find('input[type="text"]').setValue('Updated subject')

    // Submit
    await wrapper.find('form').trigger('submit.prevent')

    expect(api.updateActivity).toHaveBeenCalledWith(1, expect.objectContaining({
      subject: 'Updated subject'
    }))

    await flushPromises()
    expect(wrapper.emitted('saved')).toBeTruthy()
  })

  it('emits cancelled when cancel button is clicked', async () => {
    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    const cancelButton = wrapper.findAll('button').find(btn => btn.text() === 'Cancel')
    await cancelButton.trigger('click')

    expect(wrapper.emitted('cancelled')).toBeTruthy()
  })

  it('shows delete button only in edit mode', () => {
    const wrapperNew = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    expect(wrapperNew.text()).not.toContain('Delete')

    const wrapperEdit = mount(ActivityForm, {
      props: {
        contactId: 1,
        activity: {
          id: 1,
          type: 'Call',
          subject: 'Test',
          activity_date: '2024-01-15T10:30:00',
          notes: ''
        }
      }
    })

    expect(wrapperEdit.text()).toContain('Delete')
  })

  it('deletes activity when delete button is clicked', async () => {
    global.confirm = vi.fn(() => true)

    const activity = {
      id: 1,
      type: 'Call',
      subject: 'Test',
      activity_date: '2024-01-15T10:30:00',
      notes: ''
    }

    api.deleteActivity.mockResolvedValue(null)

    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1,
        activity
      }
    })

    const deleteButton = wrapper.findAll('button').find(btn => btn.text() === 'Delete')
    await deleteButton.trigger('click')

    expect(api.deleteActivity).toHaveBeenCalledWith(1)

    await flushPromises()
    expect(wrapper.emitted('deleted')).toBeTruthy()
    expect(wrapper.emitted('deleted')[0]).toEqual([1])
  })

  it('displays existing attachments in edit mode', () => {
    const activity = {
      id: 1,
      type: 'Call',
      subject: 'Test',
      activity_date: '2024-01-15T10:30:00',
      notes: '',
      attachments: [
        {
          id: 1,
          original_filename: 'document.pdf',
          file_size: 1024000
        }
      ]
    }

    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1,
        activity
      }
    })

    expect(wrapper.text()).toContain('Attachments')
    expect(wrapper.text()).toContain('document.pdf')
    expect(wrapper.text()).toContain('1000 KB')
  })

  // Task Group 4 Tests

  it('pre-populates form with type="Note" and current date for new activities', async () => {
    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    await wrapper.vm.$nextTick()

    // Should default to Note type
    expect(wrapper.vm.formData.type).toBe('Note')

    // Should have activity_date set to current date/time
    expect(wrapper.vm.formData.activity_date).toBeTruthy()

    // Verify it's a datetime-local format (YYYY-MM-DDTHH:MM)
    expect(wrapper.vm.formData.activity_date).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/)
  })

  it('displays submit button as "Update Activity" for both new and existing activities', async () => {
    // New activity
    const wrapperNew = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    expect(wrapperNew.text()).toContain('Update Activity')

    // Existing activity
    const wrapperEdit = mount(ActivityForm, {
      props: {
        contactId: 1,
        activity: {
          id: 1,
          type: 'Call',
          subject: 'Test',
          activity_date: '2024-01-15T10:30:00',
          notes: '',
          attachments: []
        }
      }
    })

    expect(wrapperEdit.text()).toContain('Update Activity')
  })

  it('includes pipeline_stage dropdown with active and passive stages', async () => {
    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1
      }
    })

    await wrapper.vm.$nextTick()

    // Find all select elements
    const selects = wrapper.findAll('select')

    // Should have at least 2 selects: activity type and pipeline stage
    expect(selects.length).toBeGreaterThanOrEqual(2)

    // Check that pipeline stage select exists
    const pipelineSelect = selects.find(select => {
      const options = select.findAll('option')
      return options.some(opt => opt.text().includes('Lead'))
    })

    expect(pipelineSelect).toBeTruthy()

    // Verify all stages are present
    const pipelineOptions = pipelineSelect.findAll('option')
    const stageTexts = pipelineOptions.map(opt => opt.text())

    // Active stages
    expect(stageTexts).toContain('Lead')
    expect(stageTexts).toContain('Qualified')
    expect(stageTexts).toContain('Proposal')
    expect(stageTexts).toContain('Client')

    // Passive stages
    expect(stageTexts).toContain('Qualified Out')
    expect(stageTexts).toContain('Lost Proposal')
    expect(stageTexts).toContain('Work Completed')
    expect(stageTexts).toContain('Archived')
  })

  it('allows file uploads on newly created activities', async () => {
    const mockActivity = {
      id: 1,
      type: 'Note',
      subject: 'Test',
      activity_date: '2024-01-15T10:30:00',
      notes: '',
      attachments: []
    }

    const wrapper = mount(ActivityForm, {
      props: {
        contactId: 1,
        activity: mockActivity
      }
    })

    await wrapper.vm.$nextTick()

    // File input should be available
    const fileInput = wrapper.find('input[type="file"]')
    expect(fileInput.exists()).toBe(true)

    // Upload button should be enabled
    const uploadButton = wrapper.findAll('button').find(btn => btn.text().includes('Add Attachment'))
    expect(uploadButton.exists()).toBe(true)
    expect(uploadButton.attributes('disabled')).toBeUndefined()
  })
})
