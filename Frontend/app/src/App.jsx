import { useMemo, useState } from 'react'
import './styles/tokens.css'
import './styles/app.css'

import { mockRestaurants, mockRememberedItems, mockOrders } from './data/mockUiData'
import AppShell from './components/layout/AppShell'
import HomePage from './pages/HomePage'
import RestaurantPage from './pages/RestaurantPage'
import FavouritesPage from './pages/FavouritesPage'
import ReorderPage from './pages/ReorderPage'
import OwnerDashboardPage from './pages/OwnerDashboardPage'

export default function App() {
    const [view, setView] = useState('home')
    const [restaurants, setRestaurants] = useState(mockRestaurants)
    const [selectedRestaurantId, setSelectedRestaurantId] = useState(mockRestaurants[0]?.id ?? null)
    const [search, setSearch] = useState('')
    const [role, setRole] = useState('CUSTOMER')

    const selectedRestaurant = restaurants.find(r => r.id === selectedRestaurantId) ?? null

    const filteredRestaurants = useMemo(() => {
        const q = search.trim().toLowerCase()
        if (!q) return restaurants

        return restaurants.filter((restaurant) => {
            const restaurantMatch =
                restaurant.name.toLowerCase().includes(q) ||
                restaurant.cuisine.toLowerCase().includes(q)

            const itemMatch = restaurant.menu.some(item =>
                item.name.toLowerCase().includes(q)
            )

            return restaurantMatch || itemMatch
        })
    }, [restaurants, search])

    function toggleFavourite(restaurantId) {
        setRestaurants(prev =>
            prev.map(r =>
                r.id === restaurantId ? { ...r, isFavourite: !r.isFavourite } : r
            )
        )
    }

    function toggleAvailability(restaurantId, menuItemId) {
        setRestaurants(prev =>
            prev.map(r =>
                r.id !== restaurantId
                    ? r
                    : {
                        ...r,
                        menu: r.menu.map(item =>
                            item.id === menuItemId
                                ? { ...item, available: !item.available }
                                : item
                        ),
                    }
            )
        )
    }

    return (
        <AppShell
            view={view}
            setView={setView}
            role={role}
            setRole={setRole}
            search={search}
            setSearch={setSearch}
        >
            {view === 'home' && (
                <HomePage
                    restaurants={filteredRestaurants}
                    onOpenRestaurant={(id) => {
                        setSelectedRestaurantId(id)
                        setView('restaurant')
                    }}
                    onToggleFavourite={toggleFavourite}
                />
            )}

            {view === 'restaurant' && selectedRestaurant && (
                <RestaurantPage
                    restaurant={selectedRestaurant}
                    onToggleFavourite={toggleFavourite}
                />
            )}

            {view === 'favourites' && (
                <FavouritesPage
                    restaurants={restaurants.filter(r => r.isFavourite)}
                    onOpenRestaurant={(id) => {
                        setSelectedRestaurantId(id)
                        setView('restaurant')
                    }}
                    onToggleFavourite={toggleFavourite}
                />
            )}

            {view === 'reorder' && (
                <ReorderPage
                    rememberedItems={mockRememberedItems}
                    recentOrders={mockOrders}
                />
            )}

            {view === 'owner' && (
                <OwnerDashboardPage
                    restaurants={restaurants}
                    onToggleAvailability={toggleAvailability}
                />
            )}
        </AppShell>
    )
}