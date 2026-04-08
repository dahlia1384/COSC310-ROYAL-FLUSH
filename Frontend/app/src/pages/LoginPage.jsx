import { useState } from 'react'
import { loginUser, registerUser } from '../api'

function setAuthCookie(email, password, customerId, role) {
    const value = encodeURIComponent(JSON.stringify({ email, password, customerId, role }))
    // 7-day expiry
    const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toUTCString()
    document.cookie = `rf_auth=${value}; expires=${expires}; path=/; SameSite=Strict`
}

export default function LoginPage({ onAuthSuccess, onCancel }) {
    const [mode, setMode] = useState('signin') // 'signin' | 'register'
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [role, setRole] = useState('CUSTOMER')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)

    async function handleSubmit(e) {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            if (mode === 'signin') {
                const data = await loginUser({ email, password })
                // data: { token, user: { id, email, role } }
                const token = data.token || data.access_token
                const user = data.user ?? data
                localStorage.setItem('auth_token', token)
                setAuthCookie(email, password, user.id, user.role)
                onAuthSuccess(user, token)
            } else {
                const data = await registerUser({ email, password, role })
                // auto sign-in after register
                const signInData = await loginUser({ email, password })
                const token = signInData.token || signInData.access_token
                const user = data.user ?? signInData.user ?? signInData
                localStorage.setItem('auth_token', token)
                setAuthCookie(email, password, user.id, user.role)
                onAuthSuccess(user, token)
            }
        } catch (err) {
            setError(err.message || 'Something went wrong')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-overlay">
            <div className="auth-card">
                <div className="auth-tabs">
                    <button
                        className={mode === 'signin' ? 'auth-tab active' : 'auth-tab'}
                        onClick={() => { setMode('signin'); setError('') }}
                    >
                        Sign In
                    </button>
                    <button
                        className={mode === 'register' ? 'auth-tab active' : 'auth-tab'}
                        onClick={() => { setMode('register'); setError('') }}
                    >
                        Register
                    </button>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    <label>
                        Email
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            autoComplete="email"
                            placeholder="you@example.com"
                        />
                    </label>

                    <label>
                        Password
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
                            placeholder="••••••••"
                        />
                    </label>

                    {mode === 'register' && (
                        <label>
                            Account type
                            <select value={role} onChange={(e) => setRole(e.target.value)}>
                                <option value="CUSTOMER">Customer</option>
                                <option value="RESTAURANT_OWNER">Restaurant Owner</option>
                            </select>
                        </label>
                    )}

                    {error && <p className="auth-error">{error}</p>}

                    <button className="primary-btn full" type="submit" disabled={loading}>
                        {loading ? 'Please wait…' : mode === 'signin' ? 'Sign In' : 'Create Account'}
                    </button>

                    <button type="button" className="ghost-btn full" onClick={onCancel}>
                        Cancel
                    </button>
                </form>
            </div>
        </div>
    )
}
