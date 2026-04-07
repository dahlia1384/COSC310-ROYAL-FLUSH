const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(response) {
    const contentType = response.headers.get('content-type') || ''

    if (!response.ok) {
        const text = await response.text()
        throw new Error(`Request failed: ${response.status} ${text}`)
    }

    if (!contentType.includes('application/json')) {
        const text = await response.text()
        throw new Error(`Expected JSON but got: ${text.slice(0, 120)}`)
    }

    return response.json()
}

export async function fetchRestaurants(params = {}) {
    const query = new URLSearchParams()

    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
            query.set(key, value)
        }
    })

    const url = `${API_BASE}/restaurants${query.toString() ? `?${query.toString()}` : ''}`
    const response = await fetch(url)
    return handleResponse(response)
}

export async function fetchRestaurantMenu(restaurantId) {
    const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/menu-items`)
    return handleResponse(response)
}