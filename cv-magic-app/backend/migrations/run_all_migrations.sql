-- =====================================================
-- Master Migration Script
-- Description: Run all database migrations in correct order
-- Usage: psql -d your_database -f run_all_migrations.sql
-- =====================================================

-- Start transaction
BEGIN;

-- Set search path
SET search_path = public;

-- Log migration start
\echo 'Starting database migrations...'
\echo 'Timestamp: ' || NOW();

-- =====================================================
-- 1. USER MANAGEMENT
-- =====================================================
\echo 'Running User Management migrations...'
\i 001_user_management/001_enhance_users_table.sql
\i 001_user_management/002_enhance_user_sessions.sql

-- =====================================================
-- 2. CV MANAGEMENT
-- =====================================================
\echo 'Running CV Management migrations...'
\i 002_cv_management/001_enhance_cv_table.sql

-- =====================================================
-- 3. JOB MANAGEMENT
-- =====================================================
\echo 'Running Job Management migrations...'
\i 003_job_management/001_create_job_descriptions.sql
\i 003_job_management/002_enhance_job_applications.sql

-- =====================================================
-- 4. SKILLS MANAGEMENT
-- =====================================================
\echo 'Running Skills Management migrations...'
\i 004_skills_management/001_create_skills_master.sql
\i 004_skills_management/002_create_user_skills.sql

-- =====================================================
-- 5. ANALYSIS TRACKING
-- =====================================================
\echo 'Running Analysis Tracking migrations...'
\i 005_analysis_tracking/001_create_analysis_history.sql
\i 005_analysis_tracking/002_create_ai_usage_logs.sql

-- =====================================================
-- 6. NOTIFICATIONS
-- =====================================================
\echo 'Running Notifications migrations...'
\i 006_notifications/001_create_notifications.sql

-- =====================================================
-- 7. MONITORING
-- =====================================================
\echo 'Running Monitoring migrations...'
\i 007_monitoring/001_create_api_usage.sql

-- =====================================================
-- 8. PERFORMANCE INDEXES
-- =====================================================
\echo 'Running Performance Index migrations...'
\i 008_indexes/001_create_core_indexes.sql
\i 008_indexes/002_create_jsonb_indexes.sql

-- Log migration completion
\echo 'All migrations completed successfully!'
\echo 'Timestamp: ' || NOW();

-- Commit transaction
COMMIT;

-- Display final status
\echo 'Database migration completed successfully!'
\echo 'New tables created:'
\echo '- job_descriptions'
\echo '- skills_master'
\echo '- user_skills'
\echo '- analysis_history'
\echo '- ai_usage_logs'
\echo '- notifications'
\echo '- api_usage'
\echo ''
\echo 'Enhanced tables:'
\echo '- users (added subscription, billing, preferences)'
\echo '- user_sessions (added device tracking)'
\echo '- cvs (added file management, structured data)'
\echo '- job_applications (linked to job_descriptions)'
\echo ''
\echo 'Performance indexes created for optimal query performance.'
