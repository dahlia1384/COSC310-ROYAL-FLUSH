const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

async function handleResponse(response) {
    const contentType = response.headers.get('content-type') || ''

    if (!response.ok) {
        let message = `Request failed with status ${response.status}`

        try {
            if (contentType.includes('application/json')) {
                const data = await response.json()
                message = data.detail || data.message || message
            } else {
                const text = await response.text()
                message = text || message
            }
        } catch {

        }

        throw new Error(message)
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
            query.set(key, String(value))
        }
    })

    const response = await fetch(
        `${API_BASE}/restaurants${query.toString() ? `?${query.toString()}` : ''}`,
        {
            headers: {
                Accept: 'application/json',
            },
        }
    )

    return handleResponse(response)
}

export async function fetchRestaurantMenu(restaurantId) {
    const response = await fetch(`${API_BASE}/restaurants/${restaurantId}/menu-items`, {
        headers: {
            Accept: 'application/json',
        },
    })

    return handleResponse(response)
}

export async function fetchCurrentUser(token) {
    const headers = {
        Accept: 'application/json',
    }

    if (token) {
        headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE}/auth/me`, {
        headers,
    })

    return handleResponse(response)
}
export async function placeOrder({ restaurant_id, customer_id, items, delivery_method, customer_city }) {
    const response = await fetch(`${API_BASE}/orders/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ restaurant_id, customer_id, items, delivery_method, customer_city }),
    })
    return handleResponse(response)
}

export async function payOrder(orderId, { customer_id, payment_method, simulate_success }) {
    const response = await fetch(`${API_BASE}/orders/${orderId}/pay`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ customer_id, payment_method, simulate_success }),
    })
    return handleResponse(response)
}

export async function fetchCustomerOrders(customerId) {
    const response = await fetch(`${API_BASE}/orders/customer/${customerId}`, {
        headers: { Accept: 'application/json' },
    })
    return handleResponse(response)
}

export async function loginUser({ email, password }) {
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ email, password }),
    })
    return handleResponse(response)
}

export async function registerUser({ email, password, role }) {
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ email, password, role }),
    })
    return handleResponse(response)
}

function getAuthCookie() {
    const match = document.cookie.match(/(?:^|;\s*)rf_auth=([^;]+)/)
    if (!match) return null
    try { return JSON.parse(decodeURIComponent(match[1])) } catch { return null }
}
 
export async function getWallet() {
    const auth = getAuthCookie()
    if (!auth) throw new Error('Not authenticated')
 
    const query = new URLSearchParams({ email: auth.email, password: auth.password })
    const response = await fetch(`${API_BASE}/wallet?${query}`, {
        method: 'POST',
        headers: { Accept: 'application/json' },
    })
    return handleResponse(response)
}
 
export async function putWallet(customerId, { amount, payment_method }) {
    const query = new URLSearchParams({ customer_id: customerId })
    const response = await fetch(`${API_BASE}/wallet/topup?${query}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ amount, payment_method }),
    })
    return handleResponse(response)
}