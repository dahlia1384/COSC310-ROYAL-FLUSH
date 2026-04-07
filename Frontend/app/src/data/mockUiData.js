export const mockRestaurants = [
    {
        id: '1',
        name: 'Spice House',
        cuisine: 'Indian',
        rating: 4.7,
        eta: '22-32 min',
        address: 'City_2',
        isFavourite: true,
        menu: [
            { id: '1-butter-chicken', name: 'Butter Chicken', price: 17.99, description: 'Creamy tomato curry', available: true },
            { id: '1-paneer-tikka', name: 'Paneer Tikka', price: 15.49, description: 'Charred paneer starter', available: false },
            { id: '1-naan', name: 'Garlic Naan', price: 3.99, description: 'Fresh baked naan', available: true },
        ],
    },
    {
        id: '2',
        name: 'Tokyo Bowl',
        cuisine: 'Japanese',
        rating: 4.5,
        eta: '18-25 min',
        address: 'City_3',
        isFavourite: false,
        menu: [
            { id: '2-salmon-roll', name: 'Salmon Roll', price: 12.99, description: 'Fresh salmon roll', available: true },
            { id: '2-udon', name: 'Tempura Udon', price: 14.99, description: 'Hot noodle soup', available: true },
        ],
    },
]

export const mockRememberedItems = [
    { id: 'ri-1', name: 'Butter Chicken', restaurantName: 'Spice House', lastOrdered: '2 days ago' },
    { id: 'ri-2', name: 'Salmon Roll', restaurantName: 'Tokyo Bowl', lastOrdered: '1 week ago' },
]

export const mockOrders = [
    { id: 'o-1001', restaurantName: 'Spice House', total: 24.50, status: 'Delivered' },
    { id: 'o-1002', restaurantName: 'Tokyo Bowl', total: 18.99, status: 'Delivered' },
]