-- =====================================================
-- Migration: Create AI Usage Logs Table
-- Version: 005_analysis_tracking/002
-- Date: 2024-01-XX
-- Description: Track AI model usage and costs
-- =====================================================

CREATE TABLE IF NOT EXISTS ai_usage_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- AI service details
    provider VARCHAR(50) NOT NULL, -- openai, anthropic, claude, deepseek
    model VARCHAR(100) NOT NULL, -- gpt-4, claude-3-sonnet, etc.
    operation_type VARCHAR(50) NOT NULL, -- skill_extraction, cv_tailoring, job_analysis
    
    -- Usage metrics
    tokens_used INTEGER,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost DECIMAL(10,4),
    response_time_ms INTEGER,
    
    -- Request details
    request_id VARCHAR(255),
    session_id VARCHAR(255),
    endpoint VARCHAR(200),
    
    -- Results
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    error_code VARCHAR(50),
    
    -- Context
    cv_id INTEGER REFERENCES cvs(id) ON DELETE SET NULL,
    job_id INTEGER REFERENCES job_descriptions(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_user_id ON ai_usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_provider ON ai_usage_logs(provider);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_model ON ai_usage_logs(model);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_operation_type ON ai_usage_logs(operation_type);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_created_at ON ai_usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_success ON ai_usage_logs(success);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_cost ON ai_usage_logs(cost);
CREATE INDEX IF NOT EXISTS idx_ai_usage_logs_tokens_used ON ai_usage_logs(tokens_used);

-- Add comments for documentation
COMMENT ON TABLE ai_usage_logs IS 'Track AI model usage, costs, and performance metrics';
COMMENT ON COLUMN ai_usage_logs.provider IS 'AI service provider: openai, anthropic, claude, deepseek';
COMMENT ON COLUMN ai_usage_logs.model IS 'Specific AI model used';
COMMENT ON COLUMN ai_usage_logs.operation_type IS 'Type of operation performed';
COMMENT ON COLUMN ai_usage_logs.tokens_used IS 'Total tokens consumed in this request';
COMMENT ON COLUMN ai_usage_logs.cost IS 'Cost of this AI request in USD';
COMMENT ON COLUMN ai_usage_logs.response_time_ms IS 'Response time in milliseconds';
