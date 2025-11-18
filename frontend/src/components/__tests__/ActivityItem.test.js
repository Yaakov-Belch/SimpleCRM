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

  // Task Group 4 Tests

  it('displays pipeline stage badge when stage differs from previous activity', () => {
    const activityWithStageChange = {
      ...mockActivity,
      pipeline_stage: 'Qualified'
    }

    const previousActivity = {
      id: 0,
      pipeline_stage: 'Lead'
    }

    const wrapper = mount(ActivityItem, {
      props: {
        activity: activityWithStageChange,
        previousActivity: previousActivity
      }
    })

    // Should show stage badge
    expect(wrapper.text()).toContain('Qualified')

    // Should have both type and stage badge
    const badges = wrapper.findAll('.rounded-full')
    expect(badges.length).toBeGreaterThanOrEqual(2)
  })

  it('does not display pipeline stage badge when stage matches previous activity', () => {
    const activityWithSameStage = {
      ...mockActivity,
      pipeline_stage: 'Lead'
    }

    const previousActivity = {
      id: 0,
      pipeline_stage: 'Lead'
    }

    const wrapper = mount(ActivityItem, {
      props: {
        activity: activityWithSameStage,
        previousActivity: previousActivity
      }
    })

    // Should not show duplicate stage badge text
    const text = wrapper.text()
    // Count occurrences of "Lead" - should only appear once if at all (not as a stage badge)
    const leadCount = (text.match(/Lead/g) || []).length
    expect(leadCount).toBe(0) // No "Lead" text should appear since it matches previous
  })

  it('displays pipeline stage badge when no previous activity exists', () => {
    const activityWithStage = {
      ...mockActivity,
      pipeline_stage: 'Lead'
    }

    const wrapper = mount(ActivityItem, {
      props: {
        activity: activityWithStage,
        previousActivity: null
      }
    })

    // Should show stage badge when no previous activity
    expect(wrapper.text()).toContain('Lead')
  })

  it('applies correct colors to active pipeline stage badges', () => {
    const activeStages = [
      { stage: 'Lead', expectedClass: 'bg-yellow-100' },
      { stage: 'Qualified', expectedClass: 'bg-blue-100' },
      { stage: 'Proposal', expectedClass: 'bg-purple-100' },
      { stage: 'Client', expectedClass: 'bg-green-100' }
    ]

    activeStages.forEach(({ stage, expectedClass }) => {
      const wrapper = mount(ActivityItem, {
        props: {
          activity: {
            ...mockActivity,
            pipeline_stage: stage
          },
          previousActivity: {
            id: 0,
            pipeline_stage: 'Different Stage' // Ensure badge shows
          }
        }
      })

      // Find all badges
      const badges = wrapper.findAll('.rounded-full')
      // Check if any badge has the expected class
      const hasStageBadge = badges.some(badge => badge.classes().includes(expectedClass))
      expect(hasStageBadge).toBe(true)
    })
  })

  it('applies correct colors to passive pipeline stage badges', () => {
    const passiveStages = [
      { stage: 'Qualified Out', expectedClass: 'bg-gray-100' },
      { stage: 'Lost Proposal', expectedClass: 'bg-red-100' },
      { stage: 'Work Completed', expectedClass: 'bg-teal-100' },
      { stage: 'Archived', expectedClass: 'bg-slate-100' }
    ]

    passiveStages.forEach(({ stage, expectedClass }) => {
      const wrapper = mount(ActivityItem, {
        props: {
          activity: {
            ...mockActivity,
            pipeline_stage: stage
          },
          previousActivity: {
            id: 0,
            pipeline_stage: 'Different Stage' // Ensure badge shows
          }
        }
      })

      // Find all badges
      const badges = wrapper.findAll('.rounded-full')
      // Check if any badge has the expected class
      const hasStageBadge = badges.some(badge => badge.classes().includes(expectedClass))
      expect(hasStageBadge).toBe(true)
    })
  })
})
