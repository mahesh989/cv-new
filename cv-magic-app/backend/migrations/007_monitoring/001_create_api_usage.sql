-- =====================================================
-- Migration: Create API Usage Table
-- Version: 007_monitoring/001
-- Date: 2024-01-XX
-- Description: Track API usage and performance metrics
-- =====================================================

CREATE TABLE IF NOT EXISTS api_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- API details
    endpoint VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    
    -- Usage metrics
    response_time_ms INTEGER,
    request_size_bytes INTEGER,
    response_size_bytes INTEGER,
    
    -- AI usage (if applicable)
    ai_model VARCHAR(100),
    tokens_used INTEGER,
    cost DECIMAL(10,4),
    
    -- Request details
    ip_address INET,
    user_agent TEXT,
    referer VARCHAR(500),
    
    -- Context
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    
    -- Error tracking
    error_message TEXT,
    error_type VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_usage_method ON api_usage(method);
CREATE INDEX IF NOT EXISTS idx_api_usage_status_code ON api_usage(status_code);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX IF NOT EXISTS idx_api_usage_response_time ON api_usage(response_time_ms);
CREATE INDEX IF NOT EXISTS idx_api_usage_ai_model ON api_usage(ai_model);
CREATE INDEX IF NOT EXISTS idx_api_usage_cost ON api_usage(cost);

-- Add comments for documentation
COMMENT ON TABLE api_usage IS 'Track API usage, performance, and costs';
COMMENT ON COLUMN api_usage.endpoint IS 'API endpoint that was called';
COMMENT ON COLUMN api_usage.method IS 'HTTP method used';
COMMENT ON COLUMN api_usage.status_code IS 'HTTP status code returned';
COMMENT ON COLUMN api_usage.response_time_ms IS 'Response time in milliseconds';
COMMENT ON COLUMN api_usage.tokens_used IS 'AI tokens consumed (if applicable)';
COMMENT ON COLUMN api_usage.cost IS 'Cost of this API call in USD';
