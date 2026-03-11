import client from './client'

export const predictDelay = async (payload) => {
  const response = await client.post('/predict/delay', payload)
  return response.data
}

export const getModelInfo = async () => {
  const response = await client.get('/predict/model-info')
  return response.data
}

export const getPredictHealth = async () => {
  const response = await client.get('/predict/health')
  return response.data
}
