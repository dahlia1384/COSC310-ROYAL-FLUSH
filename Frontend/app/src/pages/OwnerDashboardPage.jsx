export default function OwnerDashboardPage({ restaurants, onToggleAvailability }) {
    return (
        <div className="page-stack">
            <section className="section-card">
                <h2>Restaurant Owner Dashboard</h2>
                <p className="subtle">
                    Dedicated admin area for managing restaurants and menu item availability.
                </p>
            </section>

            {restaurants.map((restaurant) => (
                <section key={restaurant.id} className="section-card">
                    <div className="row between center">
                        <div>
                            <h3>{restaurant.name}</h3>
                            <p className="subtle">{restaurant.cuisine}</p>
                        </div>
                        <span className="chip">{restaurant.menu.length} menu items</span>
                    </div>

                    <div className="admin-menu-list">
                        {restaurant.menu.map((item) => (
                            <div key={item.id} className="admin-menu-row">
                                <div>
                                    <strong>{item.name}</strong>
                                    <p className="subtle">${item.price.toFixed(2)}</p>
                                </div>

                                <div className="row center gap-sm">
                                    <span className={item.available ? 'badge available' : 'badge unavailable'}>
                                        {item.available ? 'Available' : 'Unavailable'}
                                    </span>
                                    <button
                                        className="secondary-button"
                                        onClick={() => onToggleAvailability(restaurant.id, item.id)}
                                    >
                                        Toggle Availability
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>
            ))}

            <section className="placeholder-grid">
                <article className="placeholder-card">
                    <h3>Notifications Management</h3>
                    <p className="subtle">Placeholder for teammate feature.</p>
                </article>

                <article className="placeholder-card">
                    <h3>ETA / Delivery Operations</h3>
                    <p className="subtle">Placeholder for teammate feature.</p>
                </article>

                <article className="placeholder-card">
                    <h3>Wallet / Payments</h3>
                    <p className="subtle">Placeholder for teammate feature.</p>
                </article>
            </section>
        </div>
    )
}