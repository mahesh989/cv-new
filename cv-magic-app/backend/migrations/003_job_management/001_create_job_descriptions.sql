-- =====================================================
-- Migration: Create Job Descriptions Table
-- Version: 003_job_management/001
-- Date: 2024-01-XX
-- Description: Separate job descriptions from job applications
-- =====================================================

CREATE TABLE IF NOT EXISTS job_descriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Job identification
    job_url TEXT,
    job_title VARCHAR(200) NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    company_domain VARCHAR(255),
    
    -- Job details
    location VARCHAR(200),
    job_type VARCHAR(50), -- full-time, part-time, contract, internship
    salary_min INTEGER,
    salary_max INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Content storage
    raw_description TEXT,
    structured_requirements JSONB,
    
    -- Extracted requirements
    required_skills JSONB,
    required_experience_years INTEGER,
    required_education VARCHAR(100),
    required_certifications JSONB,
    
    -- Analysis metadata
    industry VARCHAR(100),
    seniority_level VARCHAR(50),
    remote_friendly BOOLEAN,
    
    -- Source and extraction info
    source VARCHAR(100), -- linkedin, indeed, company_website, manual
    extraction_confidence DECIMAL(3,2), -- 0.00 to 1.00
    last_scraped_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_job_descriptions_user_id ON job_descriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_company ON job_descriptions(company_name);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_job_title ON job_descriptions(job_title);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_industry ON job_descriptions(industry);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_seniority ON job_descriptions(seniority_level);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_location ON job_descriptions(location);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_job_type ON job_descriptions(job_type);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_created_at ON job_descriptions(created_at);

-- JSONB indexes for structured data
CREATE INDEX IF NOT EXISTS idx_job_descriptions_structured_requirements ON job_descriptions USING GIN (structured_requirements);
CREATE INDEX IF NOT EXISTS idx_job_descriptions_required_skills ON job_descriptions USING GIN (required_skills);

-- Add comments for documentation
COMMENT ON TABLE job_descriptions IS 'Stores job descriptions separately from applications for better data management';
COMMENT ON COLUMN job_descriptions.job_url IS 'Original URL where job was found';
COMMENT ON COLUMN job_descriptions.structured_requirements IS 'JSON object containing parsed job requirements';
COMMENT ON COLUMN job_descriptions.required_skills IS 'JSON array of required skills with importance levels';
COMMENT ON COLUMN job_descriptions.extraction_confidence IS 'Confidence score for automated extraction (0.00-1.00)';
COMMENT ON COLUMN job_descriptions.source IS 'Source platform where job was found';
