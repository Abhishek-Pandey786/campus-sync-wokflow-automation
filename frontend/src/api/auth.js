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

export const register = async ({ fullName, email, password }) => {
  const response = await client.post('/auth/register', {
    full_name: fullName,
    email,
    password,
    role: 'student'   // students self-register; admins are created manually
  })
  return response.data
}

export const getMe = async () => {
  const response = await client.get('/auth/me')
  return response.data
}
