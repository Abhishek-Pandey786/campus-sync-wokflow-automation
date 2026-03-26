import client from './client'

export const getRequests = async (params = {}) => {
  const response = await client.get('/requests/', { params })
  return response.data
}

export const getRequest = async (id) => {
  const response = await client.get(`/requests/${id}`)
  return response.data
}

export const createRequest = async (data) => {
  const response = await client.post('/requests/', data)
  return response.data
}

export const updateRequest = async (id, data) => {
  const response = await client.put(`/requests/${id}`, data)
  return response.data
}

export const deleteRequest = async (id) => {
  await client.delete(`/requests/${id}`)
}
