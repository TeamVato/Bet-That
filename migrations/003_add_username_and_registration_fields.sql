-- Migration 003: Add username and registration fields to users table
-- This migration adds the required fields for user registration and login

-- Add username column if it doesn't exist
ALTER TABLE users ADD COLUMN username VARCHAR(30) UNIQUE;

-- Add salt column for password hashing compatibility
ALTER TABLE users ADD COLUMN salt VARCHAR(64);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified);
CREATE INDEX IF NOT EXISTS idx_users_is_verified ON users(is_verified);

-- Update any existing users to have a default username based on email
-- This is safe to run multiple times
UPDATE users
SET username = LOWER(SUBSTR(email, 1, INSTR(email, '@') - 1))
WHERE username IS NULL;

-- Add check constraints for username format
-- Note: SQLite doesn't support adding constraints to existing tables easily
-- These would be enforced at the application level

COMMIT;
