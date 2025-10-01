-- =====================================================
-- Migration: Enhance CV Table
-- Version: 002_cv_management/001
-- Date: 2024-01-XX
-- Description: Add file management, processing status, and structured data
-- =====================================================

-- Add file integrity and versioning
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS file_hash VARCHAR(64),
ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.0';

-- Add processing status tracking
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS processing_status VARCHAR(50) DEFAULT 'pending',
ADD COLUMN IF NOT EXISTS processing_error TEXT;

-- Add structured data storage
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS raw_text TEXT,
ADD COLUMN IF NOT EXISTS structured_data JSONB,
ADD COLUMN IF NOT EXISTS skills_extracted JSONB;

-- Add CV analysis metadata
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS experience_years INTEGER,
ADD COLUMN IF NOT EXISTS education_level VARCHAR(100),
ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
ADD COLUMN IF NOT EXISTS seniority_level VARCHAR(50);

-- Add quality metrics
ALTER TABLE cvs 
ADD COLUMN IF NOT EXISTS ats_score INTEGER,
ADD COLUMN IF NOT EXISTS completeness_score INTEGER,
ADD COLUMN IF NOT EXISTS last_analyzed_at TIMESTAMP;

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_cvs_file_hash ON cvs(file_hash);
CREATE INDEX IF NOT EXISTS idx_cvs_processing_status ON cvs(processing_status);
CREATE INDEX IF NOT EXISTS idx_cvs_industry ON cvs(industry);
CREATE INDEX IF NOT EXISTS idx_cvs_seniority_level ON cvs(seniority_level);
CREATE INDEX IF NOT EXISTS idx_cvs_ats_score ON cvs(ats_score);
CREATE INDEX IF NOT EXISTS idx_cvs_last_analyzed ON cvs(last_analyzed_at);

-- JSONB indexes for structured data
CREATE INDEX IF NOT EXISTS idx_cvs_structured_data ON cvs USING GIN (structured_data);
CREATE INDEX IF NOT EXISTS idx_cvs_skills_extracted ON cvs USING GIN (skills_extracted);

-- Update existing CVs with default values
UPDATE cvs 
SET version = '1.0',
    processing_status = 'completed',
    ats_score = 0,
    completeness_score = 0
WHERE version IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN cvs.file_hash IS 'SHA-256 hash of file for duplicate detection';
COMMENT ON COLUMN cvs.processing_status IS 'Current processing status: pending, processing, completed, failed';
COMMENT ON COLUMN cvs.structured_data IS 'JSON object containing parsed CV structure';
COMMENT ON COLUMN cvs.skills_extracted IS 'JSON array of extracted skills with confidence scores';
COMMENT ON COLUMN cvs.ats_score IS 'ATS compatibility score (0-100)';
COMMENT ON COLUMN cvs.completeness_score IS 'CV completeness score (0-100)';
