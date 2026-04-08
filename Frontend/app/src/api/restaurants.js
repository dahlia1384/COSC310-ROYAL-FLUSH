const API_BASE = 'http://localhost:8000'

export async function fetchRestaurants(params = {}) {
    const query = new URLSearchParams(params).toString()
    const res = await fetch(`${API_BASE}/restaurants${query ? `?${query}` : ''}`)
    if (!res.ok) throw new Error('Failed to fetch restaurants')
    return res.json()
}

export async function fetchRestaurantMenu(restaurantId) {
    const res = await fetch(`${API_BASE}/restaurants/${restaurantId}/menu-items`)
    if (!res.ok) throw new Error('Failed to fetch menu')
    return res.json()
}