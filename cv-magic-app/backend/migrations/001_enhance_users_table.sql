-- Migration: Enhance users table with subscription, billing, and preferences
-- Date: 2024-01-XX
-- Description: Add missing columns for production-ready user management

-- Add new columns to existing users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS subscription_plan VARCHAR(50) DEFAULT 'free',
ADD COLUMN IF NOT EXISTS subscription_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS billing_customer_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS monthly_analysis_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS monthly_analysis_limit INTEGER DEFAULT 5,
ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC',
ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'en',
ADD COLUMN IF NOT EXISTS notification_preferences JSONB DEFAULT '{}';

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_subscription_plan ON users(subscription_plan);
CREATE INDEX IF NOT EXISTS idx_users_subscription_expires ON users(subscription_expires_at);
CREATE INDEX IF NOT EXISTS idx_users_billing_customer ON users(billing_customer_id);

-- Update existing users to have default values
UPDATE users 
SET subscription_plan = 'free',
    monthly_analysis_count = 0,
    monthly_analysis_limit = 5,
    timezone = 'UTC',
    language = 'en',
    notification_preferences = '{}'
WHERE subscription_plan IS NULL;
