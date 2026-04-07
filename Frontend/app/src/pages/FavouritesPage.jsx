export default function FavouritesPage({ restaurants, onOpenRestaurant, onToggleFavourite }) {
    return (
        <div className="page-stack">
            <section className="section-card">
                <h2>Your Favourites</h2>
                <p className="subtle">Quick access to restaurants you come back to often.</p>
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
                                <button className="icon-button" onClick={() => onToggleFavourite(restaurant.id)}>
                                    ★
                                </button>
                            </div>

                            <button className="primary-button" onClick={() => onOpenRestaurant(restaurant.id)}>
                                Open
                            </button>
                        </div>
                    </article>
                ))}
            </section>
        </div>
    )
}