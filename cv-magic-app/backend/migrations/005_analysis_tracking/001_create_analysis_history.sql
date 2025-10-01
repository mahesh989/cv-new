-- =====================================================
-- Migration: Create Analysis History Table
-- Version: 005_analysis_tracking/001
-- Date: 2024-01-XX
-- Description: Complete audit trail for all analysis operations
-- =====================================================

CREATE TABLE IF NOT EXISTS analysis_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    cv_id INTEGER REFERENCES cvs(id) ON DELETE SET NULL,
    job_id INTEGER REFERENCES job_descriptions(id) ON DELETE SET NULL,
    
    -- Analysis type and details
    analysis_type VARCHAR(50) NOT NULL, -- cv_parsing, job_matching, skill_extraction, ats_scoring
    analysis_subtype VARCHAR(50), -- detailed, quick, batch, custom
    
    -- Input/Output data
    input_data JSONB,
    output_data JSONB,
    
    -- Performance metrics
    processing_time_ms INTEGER,
    ai_model_used VARCHAR(100),
    api_cost DECIMAL(10,4),
    tokens_used INTEGER,
    
    -- Results and quality
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    quality_score DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Request metadata
    request_id VARCHAR(255), -- For tracking related requests
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_analysis_history_user_id ON analysis_history(user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_cv_id ON analysis_history(cv_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_job_id ON analysis_history(job_id);
CREATE INDEX IF NOT EXISTS idx_analysis_history_analysis_type ON analysis_history(analysis_type);
CREATE INDEX IF NOT EXISTS idx_analysis_history_success ON analysis_history(success);
CREATE INDEX IF NOT EXISTS idx_analysis_history_created_at ON analysis_history(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_history_ai_model ON analysis_history(ai_model_used);
CREATE INDEX IF NOT EXISTS idx_analysis_history_request_id ON analysis_history(request_id);

-- JSONB indexes for structured data
CREATE INDEX IF NOT EXISTS idx_analysis_history_input_data ON analysis_history USING GIN (input_data);
CREATE INDEX IF NOT EXISTS idx_analysis_history_output_data ON analysis_history USING GIN (output_data);

-- Add comments for documentation
COMMENT ON TABLE analysis_history IS 'Complete audit trail for all analysis operations';
COMMENT ON COLUMN analysis_history.analysis_type IS 'Type of analysis performed';
COMMENT ON COLUMN analysis_history.input_data IS 'JSON object containing input parameters and data';
COMMENT ON COLUMN analysis_history.output_data IS 'JSON object containing analysis results';
COMMENT ON COLUMN analysis_history.processing_time_ms IS 'Time taken to complete analysis in milliseconds';
COMMENT ON COLUMN analysis_history.api_cost IS 'Cost of API calls for this analysis';
COMMENT ON COLUMN analysis_history.confidence_score IS 'Confidence in analysis results (0.00-1.00)';
COMMENT ON COLUMN analysis_history.quality_score IS 'Quality assessment of analysis output (0.00-1.00)';
