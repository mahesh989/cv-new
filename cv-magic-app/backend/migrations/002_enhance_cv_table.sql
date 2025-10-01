-- Migration: Enhance CV table with better file management and structured data
-- Date: 2024-01-XX
-- Description: Add missing columns for production-ready CV management

-- Add new columns to existing cvs table
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64),
ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.0',
ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS processing_error TEXT,
ADD COLUMN IF NOT EXISTS raw_text TEXT,
ADD COLUMN IF NOT EXISTS structured_data JSONB,
ADD COLUMN IF NOT EXISTS skills_extracted JSONB,
ADD COLUMN IF NOT EXISTS experience_years INTEGER,
ADD COLUMN IF NOT EXISTS education_level VARCHAR(100),
ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
ADD COLUMN IF NOT EXISTS seniority_level VARCHAR(50),
ADD COLUMN IF NOT EXISTS ats_score INTEGER,
ADD COLUMN IF NOT EXISTS completeness_score INTEGER,
ADD COLUMN IF NOT EXISTS last_analyzed_at TIMESTAMP;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_cvs_file_hash ON cvs(file_hash);
CREATE INDEX IF NOT EXISTS idx_cvs_processing_status ON cvs(processing_status);
CREATE INDEX IF NOT EXISTS idx_cvs_industry ON cvs(industry);
CREATE INDEX IF NOT EXISTS idx_cvs_seniority_level ON cvs(seniority_level);
CREATE INDEX IF NOT EXISTS idx_cvs_ats_score ON cvs(ats_score);
CREATE INDEX IF NOT EXISTS idx_cvs_last_analyzed ON cvs(last_analyzed_at);

-- JSONB indexes for structured data
CREATE INDEX IF NOT EXISTS idx_cvs_structured_data ON cvs USING GIN (structured_data);
CREATE INDEX IF NOT EXISTS idx_cvs_skills_extracted ON cvs USING GIN (skills_extracted);

-- Update existing CVs to have default values
UPDATE cvs 
SET version = '1.0',
    processing_status = 'completed',
    ats_score = 0,
    completeness_score = 0
WHERE version IS NULL;
