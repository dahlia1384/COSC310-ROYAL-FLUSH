export default function ReorderPage({ rememberedItems, recentOrders }) {
    return (
        <div className="page-stack">
            <section className="section-card">
                <h2>Order Again</h2>
                <p className="subtle">
                    Surface previously ordered items and recent orders for quick access.
                </p>
            </section>

            <section className="two-col">
                <article className="section-card">
                    <h3>Remembered Items</h3>
                    <div className="stack-list">
                        {rememberedItems.map((item) => (
                            <div key={item.id} className="list-row">
                                <div>
                                    <strong>{item.name}</strong>
                                    <p className="subtle">{item.restaurantName}</p>
                                </div>
                                <span className="chip">{item.lastOrdered}</span>
                            </div>
                        ))}
                    </div>
                </article>

                <article className="section-card">
                    <h3>Recent Orders</h3>
                    <div className="stack-list">
                        {recentOrders.map((order) => (
                            <div key={order.id} className="list-row">
                                <div>
                                    <strong>{order.restaurantName}</strong>
                                    <p className="subtle">Order {order.id}</p>
                                </div>
                                <div className="right-align">
                                    <strong>${order.total.toFixed(2)}</strong>
                                    <p className="subtle">{order.status}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </article>
            </section>

            <section className="placeholder-grid">
                <article className="placeholder-card">
                    <h3>Full Order History</h3>
                    <p className="subtle">
                        Placeholder for teammate implementation if they own the full reorder/history workflow.
                    </p>
                </article>
            </section>
        </div>
    )
}