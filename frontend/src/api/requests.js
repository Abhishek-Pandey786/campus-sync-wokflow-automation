import client from './client'

export const getRequests = async (params = {}) => {
  const response = await client.get('/requests', { params })
  return response.data
}

export const getRequestById = async (id) => {
  const response = await client.get(`/requests/${id}`)
  return response.data
}

export const createRequest = async (data) => {
  const response = await client.post('/requests', data)
  return response.data
}
