-- =====================================================
-- Migration: Enhance User Sessions Table
-- Version: 001_user_management/002
-- Date: 2024-01-XX
-- Description: Add device tracking and session management
-- =====================================================

-- Add device and location tracking
ALTER TABLE user_sessions 
ADD COLUMN IF NOT EXISTS device_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS device_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS browser VARCHAR(100),
ADD COLUMN IF NOT EXISTS os VARCHAR(100),
ADD COLUMN IF NOT EXISTS country VARCHAR(100),
ADD COLUMN IF NOT EXISTS city VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP DEFAULT NOW();

-- Add refresh token support
ALTER TABLE user_sessions 
ADD COLUMN IF NOT EXISTS refresh_token VARCHAR(255);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_device_id ON user_sessions(device_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_device_type ON user_sessions(device_type);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_user_sessions_country ON user_sessions(country);

-- Add comments for documentation
COMMENT ON COLUMN user_sessions.device_id IS 'Unique device identifier for session tracking';
COMMENT ON COLUMN user_sessions.device_type IS 'Type of device: desktop, mobile, tablet';
COMMENT ON COLUMN user_sessions.last_activity_at IS 'Last time user was active in this session';
