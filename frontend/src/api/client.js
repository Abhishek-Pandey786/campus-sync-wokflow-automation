import axios from 'axios'

const client = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

// Attach JWT token to every outgoing request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Global response interceptor — handles auth and server errors centrally
 * so individual pages don't need to duplicate this logic.
 *
 * 401 Unauthorized  → clear local storage and redirect to /login
 * 403 Forbidden      → enrich the error message for role-based access feedback
 * 5xx Server Error   → enrich the error message so pages can show a friendly banner
 */
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status

    if (status === 401) {
      // Token expired or invalid — force re-login
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    } else if (status === 403) {
      // Insufficient role — enrich so the page catch block can show a helpful message
      error.friendlyMessage =
        error.response?.data?.detail ??
        'Access denied. You do not have permission for this action.'
    } else if (status >= 500) {
      // Server-side error — enrich so pages can show a retry banner
      error.friendlyMessage =
        error.response?.data?.detail ??
        'Server error. Please try again in a moment.'
    } else if (status === 503) {
      // ML model not loaded
      error.friendlyMessage =
        'The ML model is not loaded. Please ask your admin to trigger a model retrain.'
    }

    return Promise.reject(error)
  }
)

export default client

