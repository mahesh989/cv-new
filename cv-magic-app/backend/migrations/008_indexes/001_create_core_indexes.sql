-- =====================================================
-- Migration: Create Core Performance Indexes
-- Version: 008_indexes/001
-- Date: 2024-01-XX
-- Description: Essential indexes for query performance
-- =====================================================

-- User-related indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users(email) WHERE is_active = TRUE;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_subscription_active ON users(subscription_plan, is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at ON users(created_at);

-- CV-related indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cvs_user_active ON cvs(user_id, is_active);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cvs_processing_status ON cvs(processing_status) WHERE processing_status != 'completed';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cvs_analyzed_at ON cvs(last_analyzed_at) WHERE last_analyzed_at IS NOT NULL;

-- Job-related indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_descriptions_user_created ON job_descriptions(user_id, created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_descriptions_company_title ON job_descriptions(company_name, job_title);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_applications_user_status ON job_applications(user_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_applications_application_date ON job_applications(application_date);

-- Analysis-related indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_history_user_type ON analysis_history(user_id, analysis_type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_analysis_history_created_at ON analysis_history(created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_usage_logs_user_provider ON ai_usage_logs(user_id, provider);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ai_usage_logs_created_at ON ai_usage_logs(created_at);

-- Skills-related indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_skills_user_proficiency ON user_skills(user_id, proficiency_level);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_skills_master_category_active ON skills_master(skill_category, is_active);

-- Notification indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read, created_at) WHERE is_read = FALSE;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_type_priority ON notifications(type, priority);

-- API usage indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_usage_user_endpoint ON api_usage(user_id, endpoint);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_api_usage_status_created ON api_usage(status_code, created_at);

-- Add comments for documentation
COMMENT ON INDEX idx_users_email_active IS 'Index for active user email lookups';
COMMENT ON INDEX idx_cvs_user_active IS 'Index for user CV queries with active status';
COMMENT ON INDEX idx_job_descriptions_user_created IS 'Index for user job descriptions ordered by creation date';
COMMENT ON INDEX idx_analysis_history_user_type IS 'Index for user analysis history by type';
COMMENT ON INDEX idx_notifications_user_unread IS 'Index for unread user notifications';
