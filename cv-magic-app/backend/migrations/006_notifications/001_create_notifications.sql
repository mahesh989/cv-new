-- =====================================================
-- Migration: Create Notifications Table
-- Version: 006_notifications/001
-- Date: 2024-01-XX
-- Description: User notification and alert system
-- =====================================================

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Notification details
    type VARCHAR(50) NOT NULL, -- job_match, application_update, system_alert, analysis_complete
    category VARCHAR(50), -- info, warning, error, success
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    
    -- Content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    action_url VARCHAR(500), -- URL for action button
    action_text VARCHAR(100), -- Text for action button
    
    -- Related entities
    related_cv_id INTEGER REFERENCES cvs(id) ON DELETE SET NULL,
    related_job_id INTEGER REFERENCES job_descriptions(id) ON DELETE SET NULL,
    related_application_id INTEGER REFERENCES job_applications(id) ON DELETE SET NULL,
    
    -- Status and delivery
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    delivery_method VARCHAR(50) DEFAULT 'in_app', -- in_app, email, push, sms
    sent_at TIMESTAMP,
    delivery_status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, failed
    
    -- Metadata
    metadata JSONB, -- Additional data for the notification
    expires_at TIMESTAMP, -- When notification expires
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);
CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_delivery_method ON notifications(delivery_method);
CREATE INDEX IF NOT EXISTS idx_notifications_delivery_status ON notifications(delivery_status);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_expires_at ON notifications(expires_at);

-- JSONB indexes for metadata
CREATE INDEX IF NOT EXISTS idx_notifications_metadata ON notifications USING GIN (metadata);

-- Add comments for documentation
COMMENT ON TABLE notifications IS 'User notification and alert system';
COMMENT ON COLUMN notifications.type IS 'Type of notification: job_match, application_update, system_alert, analysis_complete';
COMMENT ON COLUMN notifications.category IS 'Notification category: info, warning, error, success';
COMMENT ON COLUMN notifications.priority IS 'Notification priority: low, medium, high, urgent';
COMMENT ON COLUMN notifications.delivery_method IS 'How notification is delivered: in_app, email, push, sms';
COMMENT ON COLUMN notifications.delivery_status IS 'Delivery status: pending, sent, delivered, failed';
COMMENT ON COLUMN notifications.metadata IS 'Additional JSON data for the notification';
COMMENT ON COLUMN notifications.expires_at IS 'When the notification expires and should be removed';
