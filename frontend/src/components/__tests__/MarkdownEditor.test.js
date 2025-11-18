import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import MarkdownEditor from '../MarkdownEditor.vue'

describe('MarkdownEditor', () => {
  let wrapper

  beforeEach(() => {
    // Mock window.innerWidth for desktop mode
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    })
  })

  it('renders with empty content and placeholder', () => {
    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: '',
        placeholder: 'Write your notes...'
      }
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
    expect(textarea.attributes('placeholder')).toBe('Write your notes...')
    expect(textarea.element.value).toBe('')
  })

  it('displays initial markdown value in textarea', () => {
    const markdown = '# Hello World\n\nThis is a test.'
    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: markdown
      }
    })

    const textarea = wrapper.find('textarea')
    expect(textarea.element.value).toBe(markdown)
  })

  it('emits update:modelValue when text is input', async () => {
    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: ''
      }
    })

    const textarea = wrapper.find('textarea')
    await textarea.setValue('# Test Heading')

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    expect(wrapper.emitted('update:modelValue')[0]).toEqual(['# Test Heading'])
  })

  it('renders markdown preview with debouncing', async () => {
    vi.useFakeTimers()

    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: '**Bold text**'
      }
    })

    // Wait for debounce
    vi.advanceTimersByTime(300)
    await wrapper.vm.$nextTick()

    const preview = wrapper.find('.prose')
    expect(preview.html()).toContain('<strong>Bold text</strong>')

    vi.useRealTimers()
  })

  it('sanitizes HTML to prevent XSS attacks', async () => {
    vi.useFakeTimers()

    const xssMarkdown = '<script>alert("XSS")</script>\n\n# Safe Heading'
    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: xssMarkdown
      }
    })

    // Wait for debounce
    vi.advanceTimersByTime(300)
    await wrapper.vm.$nextTick()

    const preview = wrapper.find('.prose')
    // DOMPurify should strip the script tag
    expect(preview.html()).not.toContain('<script>')
    expect(preview.html()).toContain('<h1')
  })

  it('shows mobile toggle buttons on small screens', async () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: ''
      }
    })

    // Trigger resize event
    wrapper.vm.updateIsDesktop()
    await wrapper.vm.$nextTick()

    const toggleButtons = wrapper.findAll('button')
    expect(toggleButtons.length).toBeGreaterThanOrEqual(2)
    expect(toggleButtons[0].text()).toContain('Write')
    expect(toggleButtons[1].text()).toContain('Preview')
  })

  it('toggles between write and preview modes on mobile', async () => {
    // Mock mobile viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375
    })

    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: '# Test'
      }
    })

    wrapper.vm.updateIsDesktop()
    await wrapper.vm.$nextTick()

    // Start in write mode
    expect(wrapper.vm.mobileMode).toBe('write')

    // Click preview button
    const previewButton = wrapper.findAll('button').find(btn => btn.text() === 'Preview')
    await previewButton.trigger('click')

    expect(wrapper.vm.mobileMode).toBe('preview')
  })

  it('supports GitHub-Flavored Markdown features', async () => {
    vi.useFakeTimers()

    const gfmMarkdown = `
# Heading
## Subheading

**bold** and *italic*

- List item 1
- List item 2

\`\`\`javascript
const test = 'code block'
\`\`\`

~~strikethrough~~

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
`

    wrapper = mount(MarkdownEditor, {
      props: {
        modelValue: gfmMarkdown
      }
    })

    // Wait for debounce
    vi.advanceTimersByTime(300)
    await wrapper.vm.$nextTick()

    const preview = wrapper.find('.prose')
    const html = preview.html()

    // Check for various GFM features
    expect(html).toContain('<h1')
    expect(html).toContain('<strong>bold</strong>')
    expect(html).toContain('<em>italic</em>')
    expect(html).toContain('<ul')
    expect(html).toContain('<table')
    expect(html).toContain('<del>strikethrough</del>')

    vi.useRealTimers()
  })
})
