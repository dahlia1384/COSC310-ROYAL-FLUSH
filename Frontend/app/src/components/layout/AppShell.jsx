export default function AppShell({
    children,
    view,
    setView,
    role,
    setRole,
    search,
    setSearch,
}) {
    return (
        <div className="app">
            <header className="topbar">
                <div className="brand-block">
                    <div className="brand-logo">FD</div>
                    <div>
                        <h1>Food Delivery</h1>
                        <p>Browse, favourite, reorder, and manage availability</p>
                    </div>
                </div>

                <div className="topbar-actions">
                    <input
                        className="search-input"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search restaurants or dishes"
                    />

                    <select value={role} onChange={(e) => setRole(e.target.value)}>
                        <option value="CUSTOMER">Customer</option>
                        <option value="RESTAURANT_OWNER">Restaurant Owner</option>
                    </select>
                </div>
            </header>

            <div className="page-shell">
                <aside className="sidebar">
                    <button className={view === 'home' ? 'nav active' : 'nav'} onClick={() => setView('home')}>Discover</button>
                    <button className={view === 'favourites' ? 'nav active' : 'nav'} onClick={() => setView('favourites')}>Favourites</button>
                    <button className={view === 'reorder' ? 'nav active' : 'nav'} onClick={() => setView('reorder')}>Order Again</button>
                    <button className={view === 'owner' ? 'nav active' : 'nav'} onClick={() => setView('owner')}>Owner Dashboard</button>
                </aside>

                <main className="content">{children}</main>
            </div>
        </div>
    )
}