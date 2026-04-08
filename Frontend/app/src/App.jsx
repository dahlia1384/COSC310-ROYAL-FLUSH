import { useEffect, useMemo, useState } from 'react'
import './styles/app.css'
import {
  fetchRestaurants,
  fetchRestaurantMenu,
  fetchCurrentUser,
  getWallet,
  putWallet,
  placeOrder,
  payOrder,
  fetchCustomerOrders,
} from './api'
import ETABox from './components/common/ETABox'
import { fetchDelivery } from './api/orders'
import LoginPage from './pages/LoginPage'
import NotificationList from './components/common/NotificationList'
{/* import OrderStatusCard from './components/common/OrderStatusCard'*/}

const STORAGE_KEYS = {
    favourites: 'fd_favourite_restaurant_ids',
    orders: 'fd_order_history',
    remembered: 'fd_remembered_items',
    notifications: 'fd_notifications',
}

function readJson(key, fallback) {
    try {
        const raw = localStorage.getItem(key)
        return raw ? JSON.parse(raw) : fallback
    } catch {
        return fallback
    }
}

function currency(value) {
    return `$${Number(value).toFixed(2)}`
}

function App() {
    const [search, setSearch] = useState('')
    const [view, setView] = useState('discover')

    const [restaurants, setRestaurants] = useState([])
    const [selectedRestaurantId, setSelectedRestaurantId] = useState(null)
    const [menusByRestaurant, setMenusByRestaurant] = useState({})
    const [loadingRestaurants, setLoadingRestaurants] = useState(true)
    const [loadingMenu, setLoadingMenu] = useState(false)
    const [error, setError] = useState('')

    const [cart, setCart] = useState([])

    const [favouriteIds, setFavouriteIds] = useState(() =>
        typeof window === 'undefined' ? [] : readJson(STORAGE_KEYS.favourites, [])
    )
    const [orderHistory, setOrderHistory] = useState([])
    const [rememberedItems, setRememberedItems] = useState(() =>
        typeof window === 'undefined' ? [] : readJson(STORAGE_KEYS.remembered, [])
    )
    const [notifications, setNotifications] = useState(() =>
        typeof window === 'undefined' ? [] : readJson(STORAGE_KEYS.notifications, [])
    )

    const [filters, setFilters] = useState({
        location: '',
        cuisine: '',
        minRating: '',
        customerLocation: '',
        sortBy: 'relevance',
    })

    const [currentUser, setCurrentUser] = useState(null)
    const [authMode, setAuthMode] = useState('preview')
    const [showAuth, setShowAuth] = useState(false)

    useEffect(() => {
        localStorage.setItem(STORAGE_KEYS.favourites, JSON.stringify(favouriteIds))
    }, [favouriteIds])


    useEffect(() => {
        localStorage.setItem(STORAGE_KEYS.remembered, JSON.stringify(rememberedItems))
    }, [rememberedItems])

    useEffect(() => {
        localStorage.setItem(STORAGE_KEYS.notifications, JSON.stringify(notifications))
    }, [notifications])

    useEffect(() => {
        async function loadCurrentUser() {
            const token = localStorage.getItem('auth_token')

            if (!token) {
                setCurrentUser(null)
                setAuthMode('preview')
                return
            }

            try {
                const user = await fetchCurrentUser(token)
                setCurrentUser(user)
                setAuthMode('live')
            } catch {
                setCurrentUser(null)
                setAuthMode('preview')
            }
        }

        loadCurrentUser()
    }, [])

    useEffect(() => {
        async function loadRestaurants() {
            try {
                setLoadingRestaurants(true)
                setError('')

                const backendSortBy =
                    filters.sortBy === 'proximity' ? 'delivery_time' : filters.sortBy

                const data = await fetchRestaurants({
                    keyword: search.trim() || undefined,
                    location: filters.location || undefined,
                    cuisine: filters.cuisine || undefined,
                    min_rating: filters.minRating || undefined,
                    sort_by: backendSortBy || 'relevance',
                    customer_location:
                        backendSortBy === 'delivery_time'
                            ? filters.customerLocation || undefined
                            : undefined,
                })

                setRestaurants(data)

                if (data.length > 0) {
                    setSelectedRestaurantId((prev) =>
                        prev && data.some((r) => r.id === prev) ? prev : data[0].id
                    )
                } else {
                    setSelectedRestaurantId(null)
                }
            } catch (err) {
                setError(err.message || 'Failed to load restaurants')
            } finally {
                setLoadingRestaurants(false)
            }
        }

        loadRestaurants()
    }, [search, filters])

    useEffect(() => {
        async function loadMenu() {
            if (!selectedRestaurantId || menusByRestaurant[selectedRestaurantId]) return

            try {
                setLoadingMenu(true)
                const menu = await fetchRestaurantMenu(selectedRestaurantId)
                setMenusByRestaurant((prev) => ({ ...prev, [selectedRestaurantId]: menu }))
            } catch (err) {
                setError(err.message || 'Failed to load menu')
            } finally {
                setLoadingMenu(false)
            }
        }

        loadMenu()
    }, [selectedRestaurantId, menusByRestaurant])

    const restaurantsWithUi = useMemo(() => {
        return restaurants.map((restaurant) => ({
            ...restaurant,
            cover: restaurant.cuisine || 'Restaurant',
            eta:
                restaurant.estimated_delivery_time != null
                    ? `${restaurant.estimated_delivery_time} min`
                    : 'Fast delivery',
            isFavourite: favouriteIds.includes(restaurant.id),
            menu: menusByRestaurant[restaurant.id] || [],
        }))
    }, [restaurants, favouriteIds, menusByRestaurant])

    const selectedRestaurant =
        restaurantsWithUi.find((restaurant) => restaurant.id === selectedRestaurantId) ?? null

    const favouriteRestaurants = restaurantsWithUi.filter((restaurant) => restaurant.isFavourite)

    const cartTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)

    function goToRestaurant(restaurantId) {
        setSelectedRestaurantId(restaurantId)
        setView('restaurant')
    }

    function toggleFavourite(restaurantId) {
        setFavouriteIds((prev) =>
            prev.includes(restaurantId)
                ? prev.filter((id) => id !== restaurantId)
                : [...prev, restaurantId]
        )
    }

    function addNotification(message, type) {
        const newNotification = {
            id: `NOTIF-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
            message,
            type,
            read: false,
            createdAt: new Date().toLocaleString(),
        }

        setNotifications((prev) => [newNotification, ...prev].slice(0, 20))
    }

    function markNotificationAsRead(notificationId) {
        setNotifications((prev) =>
            prev.map((notification) =>
                notification.id === notificationId
                    ? { ...notification, read: true }
                    : notification
            )
        )
    }

    function addToCart(restaurantId, item) {
        if (item.available === false) return

        const restaurant = restaurantsWithUi.find((r) => r.id === restaurantId)
        if (!restaurant) return

        setCart((prev) => {
            const existing = prev.find((cartItem) => cartItem.id === item.id)

            if (existing) {
                return prev.map((cartItem) =>
                    cartItem.id === item.id
                        ? { ...cartItem, quantity: cartItem.quantity + 1 }
                        : cartItem
                )
            }

            return [
                ...prev,
                {
                    ...item,
                    quantity: 1,
                    restaurantId,
                    restaurantName: restaurant.name,
                },
            ]
        })
    }

    function canManageRestaurant(restaurant) {
        if (authMode !== 'live') return false
        if (!currentUser) return false
        if (currentUser.role !== 'RESTAURANT_OWNER') return false
        return restaurant.owner_id === currentUser.id
    }

    function toggleAvailability(restaurantId, itemId) {
        const restaurant = restaurantsWithUi.find((r) => r.id === restaurantId)
        if (!restaurant || !canManageRestaurant(restaurant)) return

        setMenusByRestaurant((prev) => ({
            ...prev,
            [restaurantId]: (prev[restaurantId] || []).map((item) =>
                item.id === itemId ? { ...item, available: !(item.available === false) } : item
            ),
        }))
    }

    function removeFromCart(itemId) {
        setCart((prev) => prev.filter((item) => item.id !== itemId))
    }

    function buildRememberedItemsFromOrder(order) {
        const nextItems = order.items.map((item) => ({
            id: `${order.id}-${item.id}`,
            menuItemId: item.id,
            name: item.name,
            price: item.price,
            restaurantId: order.restaurantId,
            restaurantName: order.restaurantName,
            lastOrderedLabel: 'Just now',
        }))

        setRememberedItems((prev) => {
            const merged = [...nextItems, ...prev]
            const unique = []
            const seen = new Set()

            for (const item of merged) {
                const key = `${item.restaurantId}-${item.menuItemId}`
                if (!seen.has(key)) {
                    seen.add(key)
                    unique.push(item)
                }
            }

            return unique.slice(0, 8)
        })
    }

    async function checkoutCart() {
    if (cart.length === 0) return
    if (!currentUser) {
        setShowAuth(true)
        return
    }

    setCheckoutLoading(true)
    setCheckoutError('')

    const restaurantId = cart[0].restaurantId
    const restaurantName = cart[0].restaurantName
    const customer_city = selectedRestaurant?.address || 'City_1'

    try {
        const created = await placeOrder({
            restaurant_id: restaurantId,
            customer_id: currentUser.id,
            delivery_method: deliveryMethod,
            customer_city,
            items: cart.map((item) => ({
                menu_item_id: item.id,
                quantity: item.quantity,
            })),
        })

        const orderId = created.order_id

        await payOrder(orderId, {
            customer_id: currentUser.id,
            payment_method: paymentMethod,
            simulate_success: true,
        })

        const order = {
            id: `ORD-${Date.now()}`,
            restaurantId,
            restaurantName,
            createdAt: new Date().toLocaleString(),
            status: 'Placed',
            total: cartTotal,
            items: cart.map((item) => ({
                id: item.id,
                name: item.name,
                price: item.price,
                quantity: item.quantity,
            })),
        }

        setOrderHistory((prev) => [order, ...prev].slice(0, 10))
        buildRememberedItemsFromOrder(order)
        setCart([])
        setView('orderAgain')
    } catch (err) {
        setCheckoutError(err.message || 'Failed to place order')
    } finally {
        setCheckoutLoading(false)
    }
}

    function reorderSingleItem(rememberedItem) {
        const restaurant = restaurantsWithUi.find((r) => r.id === rememberedItem.restaurantId)
        const liveItem = restaurant?.menu.find((item) => item.id === rememberedItem.menuItemId)

        if (!restaurant || !liveItem || liveItem.available === false) return

        addToCart(restaurant.id, liveItem)
        setSelectedRestaurantId(restaurant.id)
        setView('restaurant')
    }

    function handleAuthSuccess(user, token) {
        setCurrentUser(user)
        setAuthMode('live')
        setShowAuth(false)
        localStorage.setItem('auth_token', token)
    }

    async function handleAddFunds() {
        const amount = parseFloat(addFundsAmount)
        if (!amount || amount <= 0) { setAddFundsError('Enter a valid amount'); return }
        setAddFundsLoading(true)
        setAddFundsError('')
        try {
            const data = await putWallet(currentUser.id, { amount, payment_method: addFundsMethod })
            setWalletBalance(Number(data.wallet ?? data.new_balance ?? walletBalance + amount))
            setShowAddFunds(false)
            setAddFundsAmount('')
        } catch (err) {
            setAddFundsError(err.message || 'Payment failed')
        } finally {
            setAddFundsLoading(false)
        }
    } 

    function handleSignOut() {
        setCurrentUser(null)
        setAuthMode('preview')
        localStorage.removeItem('auth_token')
        // clear the auth cookie
        document.cookie = 'rf_auth=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict'
    }

    function reorderWholeOrder(order) {
        const restaurant = restaurantsWithUi.find((r) => r.id === order.restaurantId)
        if (!restaurant) return

        const nextCart = []

        for (const orderItem of order.items) {
            const liveItem = restaurant.menu.find((item) => item.id === orderItem.id)
            if (liveItem && liveItem.available !== false) {
                nextCart.push({
                    ...liveItem,
                    quantity: orderItem.quantity,
                    restaurantId: restaurant.id,
                    restaurantName: restaurant.name,
                })
            }
        }

        if (nextCart.length === 0) return

        setCart(nextCart)
        setSelectedRestaurantId(restaurant.id)
        setView('restaurant')
    }

    function simulateOrderStatusUpdate(orderId, nextStatus) {
        setOrderHistory((prev) =>
            prev.map((order) =>
                order.id === orderId
                    ? {
                          ...order,
                          status: nextStatus,
                      }
                    : order
            )
        )

        const updatedOrder = orderHistory.find((order) => order.id === orderId)
        if (updatedOrder) {
            addNotification(
                `Your order from ${updatedOrder.restaurantName} is now ${nextStatus.toLowerCase()}.`,
                nextStatus.toLowerCase().replaceAll(' ', '_')
            )
        }
    }

    return (
        <div className="app-shell">
            <header className="topbar">
                <div className="brand">
                    <div className="brand-mark">RF</div>
                    <div>
                        <h1>Royal Flush</h1>
                        <p>Your go-to local food delivery app.</p>
                    </div>
                </div>

                <div className="topbar-controls">
                    <input
                        className="search-input"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search restaurants or dishes"
                    />
                </div>

                <div className="auth-topbar">
                    {currentUser ? (
                        <>
                            <span className="muted">{currentUser.email}</span>
                            <button className="secondary-btn" onClick={handleSignOut}>Sign Out</button>
                        </>
                    ) : (
                        <button className="primary-btn" onClick={() => setShowAuth(true)}>Sign In / Register</button>
                    )}
                </div>
            </header>

            {showAuth && (
                <LoginPage
                    onAuthSuccess={handleAuthSuccess}
                    onCancel={() => setShowAuth(false)}
                />
            )}

            <div className="shell-grid">
                <aside className="sidebar">
                    <button className={view === 'discover' ? 'nav active' : 'nav'} onClick={() => setView('discover')}>
                        Discover
                    </button>
                    <button className={view === 'favourites' ? 'nav active' : 'nav'} onClick={() => setView('favourites')}>
                        Favourites
                    </button>
                    <button className={view === 'orderAgain' ? 'nav active' : 'nav'} onClick={() => setView('orderAgain')}>
                        Order Again
                    </button>
                    <button className={view === 'notifications' ? 'nav active' : 'nav'} onClick={() => setView('notifications')}>
                        Notifications
                    </button>
                    <button className={view === 'currentOrders' ? 'nav active' : 'nav'} onClick={() => setView('currentOrders')}>
                        Current Orders
                    </button>
                    <button className={view === 'restaurant' ? 'nav active' : 'nav'} onClick={() => setView('restaurant')}>
                        Restaurant
                    </button>
                    {currentUser?.role === 'RESTAURANT_OWNER' && (
                        <button className={view === 'owner' ? 'nav active' : 'nav'} onClick={() => setView('owner')}>
                            Owner Dashboard
                        </button>
                    )}
                </aside>

                <main className="content">
                    {error && (
                        <section className="section-card">
                            <p className="muted">{error}</p>
                        </section>
                    )}

                    {view === 'discover' && (
                        <>
                            <section className="hero-card">
                                <div>
                                    <p className="eyebrow">Discover</p>
                                    <p className="muted">
                                        Browse restaurants in your area, search by cuisine or keywords, and sort by what matters most.
                                    </p>
                                </div>
                            </section>

                            <section className="section-card">
                                <h2>Browse Restaurants</h2>
                                <p className="muted">
                                    Filter by location, cuisine, minimum rating, and sort by rating, proximity, or relevance.
                                </p>

                                <div className="filters-grid">
                                    <input
                                        value={filters.location}
                                        onChange={(e) =>
                                            setFilters((prev) => ({ ...prev, location: e.target.value }))
                                        }
                                        placeholder="Filter by location"
                                    />

                                    <input
                                        value={filters.cuisine}
                                        onChange={(e) =>
                                            setFilters((prev) => ({ ...prev, cuisine: e.target.value }))
                                        }
                                        placeholder="Filter by cuisine"
                                    />

                                    <select
                                        value={filters.minRating}
                                        onChange={(e) =>
                                            setFilters((prev) => ({ ...prev, minRating: e.target.value }))
                                        }
                                    >
                                        <option value="">Any rating</option>
                                        <option value="3">3.0+</option>
                                        <option value="3.5">3.5+</option>
                                        <option value="4">4.0+</option>
                                        <option value="4.5">4.5+</option>
                                    </select>

                                    <select
                                        value={filters.sortBy}
                                        onChange={(e) =>
                                            setFilters((prev) => ({ ...prev, sortBy: e.target.value }))
                                        }
                                    >
                                        <option value="relevance">Relevance</option>
                                        <option value="rating">Rating</option>
                                        <option value="proximity">Proximity</option>
                                    </select>

                                    {filters.sortBy === 'proximity' && (
                                        <input
                                            value={filters.customerLocation}
                                            onChange={(e) =>
                                                setFilters((prev) => ({
                                                    ...prev,
                                                    customerLocation: e.target.value,
                                                }))
                                            }
                                            placeholder="Your location (e.g. City_2)"
                                        />
                                    )}

                                    <button
                                        className="ghost-btn"
                                        onClick={() =>
                                            setFilters({
                                                location: '',
                                                cuisine: '',
                                                minRating: '',
                                                customerLocation: '',
                                                sortBy: 'relevance',
                                            })
                                        }
                                    >
                                        Clear filters
                                    </button>
                                </div>
                            </section>

                            {loadingRestaurants ? (
                                <section className="section-card">
                                    <p className="muted">Loading restaurants...</p>
                                </section>
                            ) : (
                                <section className="card-grid">
                                    {restaurantsWithUi.map((restaurant) => (
                                        <article key={restaurant.id} className="restaurant-card">
                                            <div className="restaurant-cover">{restaurant.cover}</div>
                                            <div className="restaurant-body">
                                                <div className="row between start">
                                                    <div>
                                                        <h3>{restaurant.name}</h3>
                                                        <p className="muted">{restaurant.cuisine || 'Cuisine not listed'}</p>
                                                    </div>
                                                    <button
                                                        className="icon-button"
                                                        onClick={() => toggleFavourite(restaurant.id)}
                                                        aria-label="Toggle favourite"
                                                    >
                                                        {restaurant.isFavourite ? '★' : '☆'}
                                                    </button>
                                                </div>

                                                <div className="chip-row">
                                                    {restaurant.rating != null && <span className="chip">{restaurant.rating} ★</span>}
                                                    <span className="chip">{restaurant.eta}</span>
                                                    {restaurant.address && <span className="chip">{restaurant.address}</span>}
                                                </div>

                                                <button className="primary-btn" onClick={() => goToRestaurant(restaurant.id)}>
                                                    View menu
                                                </button>
                                            </div>
                                        </article>
                                    ))}
                                </section>
                            )}
                        </>
                    )}

                    {view === 'favourites' && (
                        <>
                            <section className="section-card">
                                <h2>Favourite Restaurants</h2>
                                <p className="muted">Saved locally for quick access until backend favourites endpoints are added.</p>
                            </section>

                            {favouriteRestaurants.length === 0 ? (
                                <section className="section-card">
                                    <p className="muted">You haven’t favourited any restaurants yet.</p>
                                </section>
                            ) : (
                                <section className="card-grid">
                                    {favouriteRestaurants.map((restaurant) => (
                                        <article key={restaurant.id} className="restaurant-card">
                                            <div className="restaurant-cover">{restaurant.cover}</div>
                                            <div className="restaurant-body">
                                                <div className="row between start">
                                                    <div>
                                                        <h3>{restaurant.name}</h3>
                                                        <p className="muted">{restaurant.cuisine || 'Cuisine not listed'}</p>
                                                    </div>
                                                    <button className="icon-button" onClick={() => toggleFavourite(restaurant.id)}>
                                                        ★
                                                    </button>
                                                </div>

                                                <button className="primary-btn" onClick={() => goToRestaurant(restaurant.id)}>
                                                    Open restaurant
                                                </button>
                                            </div>
                                        </article>
                                    ))}
                                </section>
                            )}
                        </>
                    )}

                    {view === 'orderAgain' && (
                        <>
                            <section className="section-card">
                                <h2>Order Again</h2>
                                <p className="muted">
                                    Remembered items and quick reorder are currently stored on the frontend side.
                                </p>
                            </section>

                            <section className="two-col-grid">
                                <article className="section-card">
                                    <h3>Remembered Items</h3>
                                    {rememberedItems.length === 0 ? (
                                        <p className="muted">Once you place an order, recently ordered items will appear here.</p>
                                    ) : (
                                        <div className="stack-list">
                                            {rememberedItems.map((item) => (
                                                <div key={item.id} className="list-row">
                                                    <div>
                                                        <strong>{item.name}</strong>
                                                        <p className="muted">{item.restaurantName}</p>
                                                    </div>
                                                    <div className="row gap-sm">
                                                        <span className="chip">{currency(item.price)}</span>
                                                        <button className="secondary-btn" onClick={() => reorderSingleItem(item)}>
                                                            Reorder
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </article>

                                <article className="section-card">
                                    <h3>Recent Orders</h3>
                                    {orderHistory.length === 0 ? (
                                        <p className="muted">No completed orders yet.</p>
                                    ) : (
                                        <div className="stack-list">
                                            {orderHistory.map((order) => (
                                                <div key={order.id} className="order-card">
                                                    <div className="row between start">
                                                        <div>
                                                            <strong>{order.restaurantName}</strong>
                                                            <p className="muted">{order.id}</p>
                                                            <p className="muted">{order.createdAt}</p>
                                                        </div>
                                                        <div className="order-meta">
                                                            <strong>{currency(order.total)}</strong>
                                                            <span className="chip">{order.status}</span>
                                                        </div>
                                                    </div>

                                                    <div className="order-items-preview">
                                                        {order.items.map((item) => (
                                                            <span key={`${order.id}-${item.id}`} className="preview-pill">
                                                                {item.name} × {item.quantity}
                                                            </span>
                                                        ))}
                                                    </div>

                                                    <button className="primary-btn" onClick={() => reorderWholeOrder(order)}>
                                                        Reorder this order
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </article>
                            </section>
                        </>
                    )}

                    {view === 'notifications' && (
                        <>
                            <section className="section-card">
                                <h2>Notifications</h2>
                                <p className="muted">
                                    Stay updated as your order moves through different stages.
                                </p>
                            </section>

                            <section className="section-card">
                                <NotificationList
                                    notifications={notifications}
                                    onMarkRead={markNotificationAsRead}
                                />
                            </section>
                        </>
                    )}

                    {view === 'currentOrders' && (
                        <>
                            <section className="section-card">
                                <h2>Current Orders</h2>
                                <p className="muted">
                                    Track the status of your active orders in real time.
                                </p>
                            </section>

                            {activeOrders.length === 0 ? (
                                <section className="section-card">
                                    <p className="muted">No active orders right now.</p>
                                </section>
                            ) : (
                                <section className="stack-list">
                                    {activeOrders.map((order) => (
                                        <article key={order.id} className="section-card">
                                            <div className="order-card">
                                            <div className="row between start">
                                                <div>
                                                    <strong>{order.restaurantName}</strong>
                                                    <p className="muted">{order.id}</p>
                                                    <p className="muted">{order.createdAt}</p>
                                                </div>
                                                <div className="order-meta">
                                                    <strong>{currency(order.total)}</strong>
                                                    <span className="chip">{order.status}</span>
                                                </div>
                                            </div>

                                            <div className="order-items-preview">
                                                {order.items.map((item) => (
                                                    <span key={`${order.id}-${item.id}`} className="preview-pill">
                                                        {item.name} × {item.quantity}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                            <div className="row gap-sm" style={{ marginTop: '12px' }}>
                                                <button
                                                    className="secondary-btn"
                                                    onClick={() => simulateOrderStatusUpdate(order.id, 'Confirmed')}
                                                >
                                                    Mark Confirmed
                                                </button>
                                                <button
                                                    className="secondary-btn"
                                                    onClick={() => simulateOrderStatusUpdate(order.id, 'Preparing')}
                                                >
                                                    Mark Preparing
                                                </button>
                                                <button
                                                    className="secondary-btn"
                                                    onClick={() => simulateOrderStatusUpdate(order.id, 'Out for Delivery')}
                                                >
                                                    Mark Out for Delivery
                                                </button>
                                                <button
                                                    className="secondary-btn"
                                                    onClick={() => simulateOrderStatusUpdate(order.id, 'Completed')}
                                                >
                                                    Mark Completed
                                                </button>
                                            </div>
                                        </article>
                                    ))}
                                </section>
                            )}
                        </>
                    )}

                    {view === 'restaurant' && selectedRestaurant && (
                        <>
                            <section className="restaurant-hero">
                                <div>
                                    <p className="eyebrow">{selectedRestaurant.cuisine || 'Restaurant'}</p>
                                    <h2>{selectedRestaurant.name}</h2>
                                    <div className="chip-row">
                                        {selectedRestaurant.rating != null && <span className="chip">{selectedRestaurant.rating} ★</span>}
                                        <span className="chip">{selectedRestaurant.eta}</span>
                                        {selectedRestaurant.address && <span className="chip">{selectedRestaurant.address}</span>}
                                    </div>
                                </div>

                                <button
                                    className="secondary-btn"
                                    onClick={() => toggleFavourite(selectedRestaurant.id)}
                                >
                                    {selectedRestaurant.isFavourite ? 'Remove favourite' : 'Add to favourites'}
                                </button>
                            </section>

                            {loadingMenu && !selectedRestaurant.menu.length ? (
                                <section className="section-card">
                                    <p className="muted">Loading menu...</p>
                                </section>
                            ) : (
                                <section className="menu-grid">
                                    {selectedRestaurant.menu.map((item) => (
                                        <article
                                            key={item.id}
                                            className={`menu-card ${item.available === false ? 'menu-card--muted' : ''}`}
                                        >
                                            <div className="row between start">
                                                <div>
                                                    <h3>{item.name}</h3>
                                                    <p className="muted">{item.description || 'No description available.'}</p>
                                                </div>
                                                <span className={item.available === false ? 'badge badge--off' : 'badge badge--ok'}>
                                                    {item.available === false ? 'Unavailable' : 'Available'}
                                                </span>
                                            </div>

                                            <div className="row between center">
                                                <strong>{currency(item.price)}</strong>
                                                <button
                                                    className="primary-btn"
                                                    disabled={item.available === false}
                                                    onClick={() => addToCart(selectedRestaurant.id, item)}
                                                >
                                                    {item.available === false ? 'Unavailable' : 'Add to cart'}
                                                </button>
                                            </div>
                                        </article>
                                    ))}
                                </section>
                            )}

                            <section className="placeholder-grid">
                                <article className="placeholder-card">
                                    <h3>Notifications</h3>
                                    <p className="muted">View real-time updates about your order.</p>
                                    <button className="primary-btn" onClick={() => setView('notifications')}>
                                        Open notifications
                                    </button>
                                </article>
                                <article className="placeholder-card">
                                    <h3>ETA Tracking</h3>
                                    <ETABox 
                                        order={selectedOrder} 
                                        restaurant={selectedRestaurant} 
                                        delivery={selectedDelivery} 
                                    />
                                </article>
                            </section>
                        </>
                    )}

                    {view === 'owner' && currentUser?.role === 'RESTAURANT_OWNER' && (
                        <>
                            <section className="section-card">
                                <h2>Owner Dashboard</h2>
                                <p className="muted">
                                    Owner actions are only enabled when there is a real authenticated owner session and the restaurant belongs to that owner.
                                </p>
                                {authMode === 'preview' && (
                                    <p className="muted">
                                        Preview mode: switching the dropdown changes the layout only. It does not grant real editing permissions.
                                    </p>
                                )}
                            </section>

                            {restaurantsWithUi.map((restaurant) => {
                                const canManage = canManageRestaurant(restaurant)

                                return (
                                    <section key={restaurant.id} className="section-card">
                                        <div className="row between center">
                                            <div>
                                                <h3>{restaurant.name}</h3>
                                                <p className="muted">{restaurant.cuisine || 'Cuisine not listed'}</p>
                                            </div>
                                            <span className="chip">{restaurant.menu.length} items</span>
                                        </div>

                                        {!canManage && (
                                            <p className="muted owner-note">
                                                {authMode === 'preview'
                                                    ? 'Preview mode: owner controls are disabled until a real owner account is logged in.'
                                                    : 'You do not own this restaurant, so availability controls are disabled.'}
                                            </p>
                                        )}

                                        <div className="stack-list">
                                            {restaurant.menu.map((item) => (
                                                <div key={item.id} className="list-row">
                                                    <div>
                                                        <strong>{item.name}</strong>
                                                        <p className="muted">{currency(item.price)}</p>
                                                    </div>
                                                    <div className="row gap-sm">
                                                        <span className={item.available === false ? 'badge badge--off' : 'badge badge--ok'}>
                                                            {item.available === false ? 'Unavailable' : 'Available'}
                                                        </span>
                                                        <button
                                                            className="secondary-btn"
                                                            disabled={!canManage}
                                                            onClick={() => toggleAvailability(restaurant.id, item.id)}
                                                        >
                                                            Toggle availability
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </section>
                                )
                            })}
                        </>
                    )}
                </main>

                <aside className="cart-panel">
                    <section className="section-card">
                        <h2>Wallet</h2>
                        {currentUser ? (
                            <>
                                <p className="muted">Available balance</p>
                                <strong className="wallet-balance">
                                    {walletLoading ? '…' : currency(walletBalance)}
                                </strong>

                                {!showAddFunds ? (
                                    <div className="cart-footer">
                                        <button className="secondary-btn full" onClick={() => { setShowAddFunds(true); setAddFundsError('') }}>
                                            Add Funds
                                        </button>
                                    </div>
                                ) : (
                                    <div className="cart-footer" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '12px' }}>
                                        <input
                                            type="number"
                                            min="1"
                                            step="0.01"
                                            placeholder="Amount (e.g. 20.00)"
                                            value={addFundsAmount}
                                            onChange={(e) => setAddFundsAmount(e.target.value)}
                                        />
                                        <select value={addFundsMethod} onChange={(e) => setAddFundsMethod(e.target.value)}>
                                            <option value="credit_card">Credit card</option>
                                            <option value="debit_card">Debit card</option>
                                            <option value="paypal">PayPal</option>
                                            <option value="bank_transfer">Bank transfer</option>
                                        </select>
                                        {addFundsError && <p className="muted" style={{ color: 'var(--color-text-danger)' }}>{addFundsError}</p>}
                                        <button className="primary-btn full" onClick={handleAddFunds} disabled={addFundsLoading}>
                                            {addFundsLoading ? 'Processing…' : 'Confirm'}
                                        </button>
                                        <button className="ghost-btn full" onClick={() => { setShowAddFunds(false); setAddFundsError('') }} disabled={addFundsLoading}>
                                            Cancel
                                        </button>
                                    </div>
                                )}
                            </>
                        ) : (
                            <>
                                <p className="muted">Sign in to view and use your wallet.</p>
                                <button className="primary-btn full" onClick={() => setShowAuth(true)}>
                                    Sign In
                                </button>
                            </>
                        )}
                    </section>

                    <section className="section-card">
                        <h2>Cart</h2>

                        {cart.length === 0 ? (
                            <p className="muted">Your cart is empty.</p>
                        ) : (
                            <>
                                <div className="stack-list">
                                    {cart.map((item) => (
                                        <div key={item.id} className="list-row">
                                            <div>
                                                <strong>{item.name}</strong>
                                                <p className="muted">
                                                    {item.restaurantName} · {item.quantity} × {currency(item.price)}
                                                </p>
                                            </div>
                                            <button className="ghost-btn" onClick={() => removeFromCart(item.id)}>
                                                Remove
                                            </button>
                                        </div>
                                    ))}
                                </div>

                                <div className="cart-footer">
                                    <div className="row between center">
                                        <strong>Total</strong>
                                        <strong>{currency(cartTotal)}</strong>
                                    </div>

                                    <label style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                                        Delivery method
                                        <select value={deliveryMethod} onChange={(e) => setDeliveryMethod(e.target.value)} style={{ marginTop: 4 }}>
                                            <option value="car">Car</option>
                                            <option value="bike">Bike</option>
                                            <option value="foot">Foot</option>
                                        </select>
                                    </label>

                                    <label style={{ fontSize: '0.85rem', fontWeight: 500 }}>
                                        Payment method
                                        <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)} style={{ marginTop: 4 }}>
                                            <option value="credit_card">Credit card</option>
                                            <option value="debit_card">Debit card</option>
                                            <option value="paypal">PayPal</option>
                                            <option value="wallet">Wallet</option>
                                        </select>
                                    </label>

                                    {checkoutError && <p className="auth-error">{checkoutError}</p>}

                                    <button className="primary-btn full" onClick={checkoutCart} disabled={checkoutLoading}>
                                        {checkoutLoading ? 'Placing order…' : currentUser ? 'Place order' : 'Sign in to order'}
                                    </button>
                                </div>
                            </>
                        )}
                    </section>
                </aside>

            </div>
        </div>
    )
}

export default App