import { ref } from 'vue'

const baseUrl = import.meta.env.VITE_API_URL || ''

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const request = async (endpoint, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const res = await fetch(`${baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`)
      }

      const json = await res.json()
      if (json.status !== 'ok') {
        throw new Error(json.message || 'Unknown error')
      }

      return json.data
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  const get = (endpoint) => request(endpoint)

  const post = (endpoint, body) =>
    request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    })

  return {
    loading,
    error,
    get,
    post,
    request
  }
}
