-- =====================================================
-- Migration: Enhance Users Table
-- Version: 001_user_management/001
-- Date: 2024-01-XX
-- Description: Add subscription, billing, and user preferences
-- =====================================================

-- Add subscription and billing columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(50) DEFAULT 'free',
ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS billing_customer_id VARCHAR(255);

-- Add usage tracking columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS monthly_analysis_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS monthly_analysis_limit INTEGER DEFAULT 5;

-- Add user preferences
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC',
ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{}';

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_users_subscription_plan ON users(subscription_plan);
CREATE INDEX IF NOT EXISTS idx_users_subscription_expires ON users(subscription_expires_at);
CREATE INDEX IF NOT EXISTS idx_users_billing_customer ON users(billing_customer_id);
CREATE INDEX IF NOT EXISTS idx_users_monthly_usage ON users(monthly_analysis_count);

-- Update existing users with default values
UPDATE users 
SET subscription_plan = 'free',
    monthly_analysis_count = 0,
    monthly_analysis_limit = 5,
    timezone = 'UTC',
    language = 'en',
    notification_preferences = '{}'
WHERE subscription_plan IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN users.subscription_plan IS 'User subscription tier: free, basic, premium, enterprise';
COMMENT ON COLUMN users.monthly_analysis_count IS 'Number of analyses performed this month';
COMMENT ON COLUMN users.monthly_analysis_limit IS 'Maximum analyses allowed per month';
COMMENT ON COLUMN users.notification_preferences IS 'JSON object storing user notification preferences';
