-- For Feat1-User-Authentication-and-Authorization
-- Database Schema
-- Supports:
-- FR1: User registration with email, password, role
-- FR2: Role-based access control
-- FR3: Secure logout with session invalidation

-- USERS TABLE
-- Stores registered user accounts

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    role VARCHAR(50) NOT NULL
        CHECK (role IN ('CUSTOMER', 'RESTAURANT_OWNER')),

    -- Allows disabling user accounts without deleting them
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    -- Timestamp when the account was created
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Timestamp of last update
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- USER SESSIONS TABLE
-- Stores login sessions for logout + token invalidation

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    token_id VARCHAR(255) NOT NULL UNIQUE,
    is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,

    -- Relationship: session belongs to a user
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- INDEXES FOR PERFORMANCE

-- Speed up login lookups by email
CREATE INDEX IF NOT EXISTS idx_users_email
ON users(email);

-- Speed up session lookup by token
CREATE INDEX IF NOT EXISTS idx_sessions_token
ON user_sessions(token_id);

-- Speed up finding all sessions for a user
CREATE INDEX IF NOT EXISTS idx_sessions_user
ON user_sessions(user_id);