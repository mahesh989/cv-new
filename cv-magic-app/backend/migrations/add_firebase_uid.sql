-- Migration: add firebase_uid column to users table
-- Run this against your existing PostgreSQL database once.
-- New databases get the column automatically via create_tables().

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS firebase_uid VARCHAR(128) UNIQUE,
    ALTER COLUMN hashed_password DROP NOT NULL;

CREATE INDEX IF NOT EXISTS ix_users_firebase_uid ON users (firebase_uid);
