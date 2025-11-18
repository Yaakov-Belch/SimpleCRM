import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ActivityItem from '../ActivityItem.vue'

describe('ActivityItem', () => {
  const mockActivity = {
    id: 1,
    type: 'Call',
    subject: 'Follow-up call',
    notes: '# Meeting Notes\n\nDiscussed project timeline.',
    activity_date: '2024-01-15T10:30:00',
    attachments: [
      {
        id: 1,
        original_filename: 'document.pdf',
        file_size: 1024000
      }
    ]
  }

  it('renders activity with correct type badge', () => {
    const wrapper = mount(ActivityItem, {
      props: {
        activity: mockActivity
      }
    })

    const badge = wrapper.find('.px-3.py-1.rounded-full')
    expect(badge.text()).toBe('Call')
    expect(badge.classes()).toContain('bg-blue-100')
  })

  it('displays activity subject and date', () => {
    const wrapper = mount(ActivityItem, {
      props: {
        activity: mockActivity
      }
    })

    expect(wrapper.text()).toContain('Follow-up call')
    expect(wrapper.text()).toContain('January')
  })

  it('renders markdown notes as HTML', () => {
    const wrapper = mount(ActivityItem, {
      props: {
        activity: mockActivity
      }
    })

    const prose = wrapper.find('.prose')
    expect(prose.html()).toContain('<h1')
    expect(prose.html()).toContain('Meeting Notes')
  })

  it('emits edit event when edit button is clicked', async () => {
    const wrapper = mount(ActivityItem, {
      props: {
        activity: mockActivity
      }
    })

    const editButton = wrapper.findAll('button')[0]
    await editButton.trigger('click')

    expect(wrapper.emitted('edit')).toBeTruthy()
    expect(wrapper.emitted('edit')[0]).toEqual([mockActivity])
  })

  it('emits delete event when delete button is clicked', async () => {
    const wrapper = mount(ActivityItem, {
      props: {
        activity: mockActivity
      }
    })

    const deleteButton = wrapper.findAll('button')[1]
    await deleteButton.trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')[0]).toEqual([mockActivity.id])
  })

  it('displays attachments with file size', () => {
    const wrapper = mount(ActivityItem, {
      props: {
        activity: mockActivity
      }
    })

    expect(wrapper.text()).toContain('Attachments')
    expect(wrapper.text()).toContain('document.pdf')
    expect(wrapper.text()).toContain('1000 KB')
  })

  it('shows expand/collapse button for long content', async () => {
    const longActivity = {
      ...mockActivity,
      notes: 'a'.repeat(250)
    }

    const wrapper = mount(ActivityItem, {
      props: {
        activity: longActivity
      }
    })

    const expandButton = wrapper.find('button.text-blue-600')
    expect(expandButton.exists()).toBe(true)
    expect(expandButton.text()).toContain('Show more')

    await expandButton.trigger('click')
    expect(expandButton.text()).toContain('Show less')
  })

  it('applies correct type badge colors', () => {
    const types = [
      { type: 'Call', colorClass: 'bg-blue-100' },
      { type: 'Meeting', colorClass: 'bg-green-100' },
      { type: 'Email', colorClass: 'bg-purple-100' },
      { type: 'Note', colorClass: 'bg-gray-100' }
    ]

    types.forEach(({ type, colorClass }) => {
      const wrapper = mount(ActivityItem, {
        props: {
          activity: { ...mockActivity, type }
        }
      })

      const badge = wrapper.find('.rounded-full')
      expect(badge.classes()).toContain(colorClass)
    })
  })
})
