-- =====================================================
-- Migration: Create Skills Master Table
-- Version: 004_skills_management/001
-- Date: 2024-01-XX
-- Description: Centralized skills database for the platform
-- =====================================================

CREATE TABLE IF NOT EXISTS skills_master (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(200) UNIQUE NOT NULL,
    skill_category VARCHAR(100), -- technical, soft, language, certification
    skill_subcategory VARCHAR(100), -- programming, design, management, etc.
    
    -- Skill metadata
    industry_relevance JSONB, -- Which industries use this skill
    seniority_levels JSONB, -- junior, mid, senior requirements
    related_skills JSONB, -- Skills that often go together
    
    -- Market data
    demand_score INTEGER, -- 0-100 based on job postings
    salary_impact DECIMAL(5,2), -- Average salary increase %
    trending_score INTEGER, -- 0-100 based on growth
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_skills_master_skill_name ON skills_master(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_master_category ON skills_master(skill_category);
CREATE INDEX IF NOT EXISTS idx_skills_master_subcategory ON skills_master(skill_subcategory);
CREATE INDEX IF NOT EXISTS idx_skills_master_demand_score ON skills_master(demand_score DESC);
CREATE INDEX IF NOT EXISTS idx_skills_master_trending_score ON skills_master(trending_score DESC);
CREATE INDEX IF NOT EXISTS idx_skills_master_is_active ON skills_master(is_active);

-- JSONB indexes for structured data
CREATE INDEX IF NOT EXISTS idx_skills_master_industry_relevance ON skills_master USING GIN (industry_relevance);
CREATE INDEX IF NOT EXISTS idx_skills_master_seniority_levels ON skills_master USING GIN (seniority_levels);
CREATE INDEX IF NOT EXISTS idx_skills_master_related_skills ON skills_master USING GIN (related_skills);

-- Add comments for documentation
COMMENT ON TABLE skills_master IS 'Master database of all skills with market intelligence';
COMMENT ON COLUMN skills_master.skill_name IS 'Standardized skill name (e.g., "Python", "Project Management")';
COMMENT ON COLUMN skills_master.skill_category IS 'High-level category: technical, soft, language, certification';
COMMENT ON COLUMN skills_master.skill_subcategory IS 'Specific subcategory within the main category';
COMMENT ON COLUMN skills_master.industry_relevance IS 'JSON object mapping industries to relevance scores';
COMMENT ON COLUMN skills_master.demand_score IS 'Market demand score based on job postings (0-100)';
COMMENT ON COLUMN skills_master.salary_impact IS 'Average salary increase percentage for this skill';
COMMENT ON COLUMN skills_master.trending_score IS 'Growth trend score based on recent job postings (0-100)';

-- Insert some common skills to get started
INSERT INTO skills_master (skill_name, skill_category, skill_subcategory, demand_score, salary_impact, trending_score) VALUES
('Python', 'technical', 'programming', 95, 15.5, 90),
('JavaScript', 'technical', 'programming', 90, 12.3, 85),
('Project Management', 'soft', 'management', 80, 18.2, 75),
('Communication', 'soft', 'interpersonal', 85, 10.1, 80),
('SQL', 'technical', 'database', 88, 14.7, 82),
('React', 'technical', 'frontend', 92, 16.8, 88),
('Leadership', 'soft', 'management', 75, 22.5, 70),
('Machine Learning', 'technical', 'ai_ml', 85, 25.3, 95),
('AWS', 'technical', 'cloud', 87, 20.1, 90),
('Agile', 'soft', 'methodology', 78, 13.2, 72)
ON CONFLICT (skill_name) DO NOTHING;
