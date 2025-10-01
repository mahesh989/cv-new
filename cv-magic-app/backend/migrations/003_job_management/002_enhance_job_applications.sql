-- =====================================================
-- Migration: Enhance Job Applications Table
-- Version: 003_job_management/002
-- Date: 2024-01-XX
-- Description: Link job applications to job descriptions and add tracking
-- =====================================================

-- Add reference to job_descriptions table
ALTER TABLE job_applications 
ADD COLUMN IF NOT EXISTS job_description_id INTEGER REFERENCES job_descriptions(id) ON DELETE SET NULL;

-- Add application tracking
ALTER TABLE job_applications 
ADD COLUMN IF NOT EXISTS application_method VARCHAR(50), -- direct, email, portal, referral
ADD COLUMN IF NOT EXISTS application_platform VARCHAR(100), -- company_website, linkedin, indeed
ADD COLUMN IF NOT EXISTS cover_letter_path VARCHAR(500),
ADD COLUMN IF NOT EXISTS follow_up_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS interview_scheduled_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS rejection_reason TEXT;

-- Add salary and benefits tracking
ALTER TABLE job_applications 
ADD COLUMN IF NOT EXISTS offered_salary INTEGER,
ADD COLUMN IF NOT EXISTS offered_benefits JSONB;

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_job_applications_job_description_id ON job_applications(job_description_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_application_method ON job_applications(application_method);
CREATE INDEX IF NOT EXISTS idx_job_applications_application_platform ON job_applications(application_platform);
CREATE INDEX IF NOT EXISTS idx_job_applications_follow_up_date ON job_applications(follow_up_date);
CREATE INDEX IF NOT EXISTS idx_job_applications_interview_scheduled ON job_applications(interview_scheduled_at);

-- Add comments for documentation
COMMENT ON COLUMN job_applications.job_description_id IS 'Reference to job_descriptions table for better data normalization';
COMMENT ON COLUMN job_applications.application_method IS 'How the application was submitted';
COMMENT ON COLUMN job_applications.application_platform IS 'Platform used for application submission';
COMMENT ON COLUMN job_applications.offered_benefits IS 'JSON object containing offered benefits and perks';
