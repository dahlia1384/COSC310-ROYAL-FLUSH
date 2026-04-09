const API_BASE = 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }

  return res
}

export const client = {
  async get(path) {
    const res = await request(path, { method: 'GET' })
    return { data: await res.json() }
  },

  async post(path, body) {
    const res = await request(path, {
      method: 'POST',
      body: JSON.stringify(body),
    })
    return { data: await res.json() }
  },

  async put(path, body) {
    const res = await request(path, {
      method: 'PUT',
      body: JSON.stringify(body),
    })
    return { data: await res.json() }
  },
}