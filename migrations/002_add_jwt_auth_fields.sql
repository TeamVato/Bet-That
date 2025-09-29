-- JWT Authentication Enhancement Migration
-- Adds JWT-specific fields to the users table for comprehensive authentication
-- Run with: sqlite3 storage/odds.db < migrations/002_add_jwt_auth_fields.sql

-- Add JWT and security fields to users table
ALTER TABLE users ADD COLUMN password_hash TEXT;
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN email_verified_at DATETIME;
ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'pending_verification' CHECK (status IN ('active', 'suspended', 'pending_verification', 'banned'));
ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN verification_level TEXT DEFAULT 'basic' CHECK (verification_level IN ('basic', 'enhanced', 'premium'));
ALTER TABLE users ADD COLUMN first_name TEXT;
ALTER TABLE users ADD COLUMN last_name TEXT;
ALTER TABLE users ADD COLUMN timezone TEXT DEFAULT 'UTC';
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users ADD COLUMN last_login_at DATETIME;
ALTER TABLE users ADD COLUMN last_activity_at DATETIME;
ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN locked_until DATETIME;
ALTER TABLE users ADD COLUMN password_changed_at DATETIME;
ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN two_factor_secret TEXT;
ALTER TABLE users ADD COLUMN backup_codes TEXT; -- JSON array of backup codes
ALTER TABLE users ADD COLUMN preferred_sports TEXT; -- JSON array
ALTER TABLE users ADD COLUMN notification_preferences TEXT; -- JSON object
ALTER TABLE users ADD COLUMN ui_preferences TEXT; -- JSON object
ALTER TABLE users ADD COLUMN created_by TEXT;
ALTER TABLE users ADD COLUMN deleted_at DATETIME;

-- Add indexes for JWT authentication
CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified);
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login_at);
CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_users_locked_until ON users(locked_until);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users(deleted_at);

-- Create JWT token blacklist table
CREATE TABLE IF NOT EXISTS jwt_token_blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jti TEXT UNIQUE NOT NULL, -- JWT ID
    user_id INTEGER NOT NULL,
    token_type TEXT NOT NULL CHECK (token_type IN ('access', 'refresh', 'password_reset')),
    expires_at DATETIME NOT NULL,
    revoked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT, -- Optional revocation reason
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_jti ON jwt_token_blacklist(jti);
CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_user_id ON jwt_token_blacklist(user_id);
CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_expires_at ON jwt_token_blacklist(expires_at);
CREATE INDEX IF NOT EXISTS idx_jwt_blacklist_type ON jwt_token_blacklist(token_type);

-- Create authentication log table for security auditing
CREATE TABLE IF NOT EXISTS auth_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_type TEXT NOT NULL, -- login, logout, password_change, token_refresh, etc.
    ip_address TEXT NOT NULL,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    additional_data TEXT, -- JSON object with extra context
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_auth_logs_user_id ON auth_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_auth_logs_event_type ON auth_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_auth_logs_ip_address ON auth_logs(ip_address);
CREATE INDEX IF NOT EXISTS idx_auth_logs_created_at ON auth_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_auth_logs_success ON auth_logs(success);

-- Create user sessions table for session management
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT UNIQUE NOT NULL,
    refresh_token_jti TEXT UNIQUE,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_refresh_token_jti ON user_sessions(refresh_token_jti);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity_at);

-- Update existing users to have proper status
UPDATE users SET status = 'active' WHERE status IS NULL AND is_active = TRUE;
UPDATE users SET status = 'suspended' WHERE is_active = FALSE;

-- Add risk management fields to users table
ALTER TABLE users ADD COLUMN max_bet_size DECIMAL(12,2) DEFAULT 1000.00;
ALTER TABLE users ADD COLUMN daily_bet_limit DECIMAL(12,2) DEFAULT 5000.00;
ALTER TABLE users ADD COLUMN monthly_bet_limit DECIMAL(12,2) DEFAULT 50000.00;
ALTER TABLE users ADD COLUMN risk_tolerance TEXT DEFAULT 'medium' CHECK (risk_tolerance IN ('low', 'medium', 'high'));
ALTER TABLE users ADD COLUMN auto_kelly_sizing BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN max_kelly_fraction REAL DEFAULT 0.25;
