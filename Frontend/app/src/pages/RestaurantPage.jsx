function StatusBadge({ available }) {
    return (
        <span className={available ? 'badge available' : 'badge unavailable'}>
            {available ? 'Available' : 'Unavailable'}
        </span>
    )
}

export default function RestaurantPage({ restaurant, onToggleFavourite }) {
    return (
        <div className="page-stack">
            <section className="restaurant-hero">
                <div>
                    <p className="eyebrow">{restaurant.cuisine}</p>
                    <h2>{restaurant.name}</h2>
                    <div className="chip-row">
                        <span className="chip">{restaurant.rating} ★</span>
                        <span className="chip">{restaurant.eta}</span>
                    </div>
                </div>

                <button
                    className="secondary-button"
                    onClick={() => onToggleFavourite(restaurant.id)}
                >
                    {restaurant.isFavourite ? 'Remove Favourite' : 'Add to Favourites'}
                </button>
            </section>

            <section className="menu-grid">
                {restaurant.menu.map((item) => (
                    <article key={item.id} className={`menu-card ${!item.available ? 'muted-card' : ''}`}>
                        <div className="row between start">
                            <div>
                                <h3>{item.name}</h3>
                                <p className="subtle">{item.description}</p>
                            </div>
                            <StatusBadge available={item.available} />
                        </div>

                        <div className="row between center">
                            <strong>${item.price.toFixed(2)}</strong>
                            <button className="primary-button" disabled={!item.available}>
                                {item.available ? 'Add to Cart' : 'Unavailable'}
                            </button>
                        </div>
                    </article>
                ))}
            </section>

            <section className="placeholder-grid">
                <article className="placeholder-card">
                    <h3>Notifications</h3>
                    <p className="subtle">
                        Placeholder for teammate feature. This section can later consume the notifications service.
                    </p>
                </article>

                <article className="placeholder-card">
                    <h3>ETA / Live Order Tracking</h3>
                    <p className="subtle">
                        Placeholder for teammate feature. Add current order status and ETA here.
                    </p>
                </article>
            </section>
        </div>
    )
}