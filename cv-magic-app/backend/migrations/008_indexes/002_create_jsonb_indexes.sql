-- =====================================================
-- Migration: Create JSONB Performance Indexes
-- Version: 008_indexes/002
-- Date: 2024-01-XX
-- Description: JSONB indexes for structured data queries
-- =====================================================

-- CV structured data indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cvs_structured_data_gin ON cvs USING GIN (structured_data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cvs_skills_extracted_gin ON cvs USING GIN (skills_extracted);

-- Job description indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_descriptions_structured_requirements_gin ON job_descriptions USING GIN (structured_requirements);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_descriptions_required_skills_gin ON job_descriptions USING GIN (required_skills);

-- Skills master indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skills_master_industry_relevance_gin ON skills_master USING GIN (industry_relevance);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skills_master_seniority_levels_gin ON skills_master USING GIN (seniority_levels);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skills_master_related_skills_gin ON skills_master USING GIN (related_skills);

-- Analysis history indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_history_input_data_gin ON analysis_history USING GIN (input_data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_history_output_data_gin ON analysis_history USING GIN (output_data);

-- Notification metadata indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_metadata_gin ON notifications USING GIN (metadata);

-- User preferences indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_notification_preferences_gin ON users USING GIN (notification_preferences);

-- Job application benefits indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_applications_offered_benefits_gin ON job_applications USING GIN (offered_benefits);

-- Add comments for documentation
COMMENT ON INDEX idx_cvs_structured_data_gin IS 'GIN index for CV structured data JSONB queries';
COMMENT ON INDEX idx_job_descriptions_required_skills_gin IS 'GIN index for job description required skills queries';
COMMENT ON INDEX idx_skills_master_industry_relevance_gin IS 'GIN index for skills industry relevance queries';
COMMENT ON INDEX idx_analysis_history_input_data_gin IS 'GIN index for analysis history input data queries';
COMMENT ON INDEX idx_notifications_metadata_gin IS 'GIN index for notification metadata queries';
