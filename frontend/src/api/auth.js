import client from './client'

export const login = async (email, password) => {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)
  const response = await client.post('/auth/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}

export const getMe = async () => {
  const response = await client.get('/auth/me')
  return response.data
}
