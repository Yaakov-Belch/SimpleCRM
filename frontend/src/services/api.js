const API_BASE_URL = 'http://localhost:8000/api'

class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
  }
}

async function handleResponse(response) {
  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch {
      errorData = { message: response.statusText }
    }

    const message = errorData.error?.message || errorData.detail || errorData.message || 'An error occurred'
    throw new ApiError(message, response.status, errorData)
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return null
  }

  return response.json()
}

function getAuthHeaders() {
  const token = localStorage.getItem('sessionToken')
  const headers = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

function getAuthHeadersMultipart() {
  const token = localStorage.getItem('sessionToken')
  const headers = {}

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Don't set Content-Type for multipart/form-data, browser will set it with boundary
  return headers
}

export async function apiGet(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  })

  return handleResponse(response)
}

export async function apiPost(endpoint, data) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })

  return handleResponse(response)
}

export async function apiPut(endpoint, data) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data),
  })

  return handleResponse(response)
}

export async function apiDelete(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  })

  return handleResponse(response)
}

// Contact API methods
export async function createContact(contactData) {
  return apiPost('/contacts', contactData)
}

export async function getContacts(params = {}) {
  const queryParams = new URLSearchParams()

  if (params.page) queryParams.append('page', params.page)
  if (params.limit) queryParams.append('limit', params.limit)
  if (params.search) queryParams.append('search', params.search)
  if (params.stage) queryParams.append('stage', params.stage)

  const query = queryParams.toString()
  return apiGet(`/contacts${query ? '?' + query : ''}`)
}

export async function getContactById(id) {
  return apiGet(`/contacts/${id}`)
}

export async function updateContact(id, contactData) {
  return apiPut(`/contacts/${id}`, contactData)
}

export async function deleteContact(id) {
  return apiDelete(`/contacts/${id}`)
}

// Pipeline stage API methods
export async function updateContactStage(contactId, stage) {
  return apiPut(`/contacts/${contactId}`, { pipeline_stage: stage })
}

export async function getPipelineStats() {
  return apiGet('/contacts/pipeline-stats')
}

// Activity API methods
export async function getActivitiesForContact(contactId) {
  return apiGet(`/contacts/${contactId}/activities`)
}

export async function createActivity(contactId, activityData) {
  return apiPost(`/contacts/${contactId}/activities`, activityData)
}

export async function getActivityById(activityId) {
  return apiGet(`/activities/${activityId}`)
}

export async function updateActivity(activityId, activityData) {
  return apiPut(`/activities/${activityId}`, activityData)
}

export async function deleteActivity(activityId) {
  return apiDelete(`/activities/${activityId}`)
}

export async function getAllActivities(params = {}) {
  const queryParams = new URLSearchParams()

  if (params.type) queryParams.append('type', params.type)
  if (params.search) queryParams.append('search', params.search)

  const query = queryParams.toString()
  return apiGet(`/activities${query ? '?' + query : ''}`)
}

// Attachment API methods
export async function uploadAttachment(activityId, file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/activities/${activityId}/attachments`, {
    method: 'POST',
    headers: getAuthHeadersMultipart(),
    body: formData,
  })

  return handleResponse(response)
}

export async function downloadAttachment(activityId, attachmentId) {
  const token = localStorage.getItem('sessionToken')
  const headers = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}/activities/${activityId}/attachments/${attachmentId}`, {
    method: 'GET',
    headers,
  })

  if (!response.ok) {
    throw new ApiError('Failed to download attachment', response.status)
  }

  return response.blob()
}

export async function deleteAttachment(activityId, attachmentId) {
  return apiDelete(`/activities/${activityId}/attachments/${attachmentId}`)
}

export { ApiError }
