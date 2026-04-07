export default function HomePage({ restaurants, onOpenRestaurant, onToggleFavourite }) {
    return (
        <div className="page-stack">
            <section className="hero-card">
                <div>
                    <p className="eyebrow">Discover</p>
                    <h2>Find something good, fast</h2>
                    <p className="subtle">
                        Search restaurants, browse menus, and save your favourites.
                    </p>
                </div>
            </section>

            <section className="restaurant-grid">
                {restaurants.map((restaurant) => (
                    <article key={restaurant.id} className="restaurant-card">
                        <div className="restaurant-image" />
                        <div className="restaurant-card-body">
                            <div className="row between start">
                                <div>
                                    <h3>{restaurant.name}</h3>
                                    <p className="subtle">{restaurant.cuisine}</p>
                                </div>
                                <button
                                    className="icon-button"
                                    onClick={() => onToggleFavourite(restaurant.id)}
                                >
                                    {restaurant.isFavourite ? '★' : '☆'}
                                </button>
                            </div>

                            <div className="chip-row">
                                <span className="chip">{restaurant.rating} ★</span>
                                <span className="chip">{restaurant.eta}</span>
                            </div>

                            <button className="primary-button" onClick={() => onOpenRestaurant(restaurant.id)}>
                                View Menu
                            </button>
                        </div>
                    </article>
                ))}
            </section>
        </div>
    )
}