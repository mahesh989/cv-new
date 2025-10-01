-- =====================================================
-- Migration Validation Script
-- Description: Validate that all migrations were applied correctly
-- Usage: psql -d your_database -f validate_migrations.sql
-- =====================================================

-- Set search path
SET search_path = public;

\echo 'Validating database migrations...'
\echo 'Timestamp: ' || NOW();
\echo ''

-- Check if all tables exist
\echo 'Checking table existence...'
SELECT 
    CASE 
        WHEN COUNT(*) = 8 THEN '✅ All new tables created successfully'
        ELSE '❌ Missing tables: ' || (8 - COUNT(*)) || ' tables not found'
    END as table_check
FROM information_schema.tables 
WHERE table_name IN (
    'job_descriptions', 'skills_master', 'user_skills', 
    'analysis_history', 'ai_usage_logs', 'notifications', 'api_usage'
);

-- Check enhanced columns in existing tables
\echo ''
\echo 'Checking enhanced columns in existing tables...'

-- Check users table enhancements
SELECT 
    CASE 
        WHEN COUNT(*) >= 5 THEN '✅ Users table enhanced successfully'
        ELSE '❌ Users table missing columns: ' || (5 - COUNT(*)) || ' columns not found'
    END as users_check
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('subscription_plan', 'monthly_analysis_count', 'timezone', 'language', 'notification_preferences');

-- Check CV table enhancements
SELECT 
    CASE 
        WHEN COUNT(*) >= 5 THEN '✅ CV table enhanced successfully'
        ELSE '❌ CV table missing columns: ' || (5 - COUNT(*)) || ' columns not found'
    END as cv_check
FROM information_schema.columns 
WHERE table_name = 'cvs' 
AND column_name IN ('file_hash', 'processing_status', 'structured_data', 'ats_score', 'completeness_score');

-- Check job_applications enhancements
SELECT 
    CASE 
        WHEN COUNT(*) >= 3 THEN '✅ Job applications table enhanced successfully'
        ELSE '❌ Job applications table missing columns: ' || (3 - COUNT(*)) || ' columns not found'
    END as job_apps_check
FROM information_schema.columns 
WHERE table_name = 'job_applications' 
AND column_name IN ('job_description_id', 'application_method', 'application_platform');

-- Check indexes
\echo ''
\echo 'Checking critical indexes...'
SELECT 
    CASE 
        WHEN COUNT(*) >= 10 THEN '✅ Critical indexes created successfully'
        ELSE '❌ Missing indexes: ' || (10 - COUNT(*)) || ' indexes not found'
    END as index_check
FROM pg_indexes 
WHERE indexname IN (
    'idx_users_subscription_plan', 'idx_cvs_processing_status', 
    'idx_job_descriptions_user_id', 'idx_skills_master_skill_name',
    'idx_user_skills_user_id', 'idx_analysis_history_user_id',
    'idx_ai_usage_logs_user_id', 'idx_notifications_user_id',
    'idx_api_usage_user_id', 'idx_cvs_structured_data_gin'
);

-- Check foreign key constraints
\echo ''
\echo 'Checking foreign key constraints...'
SELECT 
    CASE 
        WHEN COUNT(*) >= 7 THEN '✅ Foreign key constraints created successfully'
        ELSE '❌ Missing foreign keys: ' || (7 - COUNT(*)) || ' constraints not found'
    END as fk_check
FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' 
AND constraint_name IN (
    'job_descriptions_user_id_fkey', 'user_skills_user_id_fkey',
    'user_skills_skill_id_fkey', 'analysis_history_user_id_fkey',
    'ai_usage_logs_user_id_fkey', 'notifications_user_id_fkey',
    'api_usage_user_id_fkey'
);

-- Display table sizes
\echo ''
\echo 'Table sizes after migration:'
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN (
    'users', 'cvs', 'job_applications', 'job_descriptions', 
    'skills_master', 'user_skills', 'analysis_history', 
    'ai_usage_logs', 'notifications', 'api_usage'
)
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Final validation summary
\echo ''
\echo '========================================'
\echo 'MIGRATION VALIDATION COMPLETE'
\echo '========================================'
\echo 'If all checks show ✅, your database is ready!'
\echo 'If any checks show ❌, please review the migration logs.'
\echo ''
\echo 'Next steps:'
\echo '1. Update your SQLAlchemy models to match new schema'
\echo '2. Test your application with the new database structure'
\echo '3. Update your API endpoints to use new tables'
\echo '4. Consider data migration for existing records'
