-- =====================================================
-- Migration: Create User Skills Table
-- Version: 004_skills_management/002
-- Date: 2024-01-XX
-- Description: Junction table linking users to their skills
-- =====================================================

CREATE TABLE IF NOT EXISTS user_skills (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills_master(id) ON DELETE CASCADE,
    cv_id INTEGER REFERENCES cvs(id) ON DELETE CASCADE,
    
    -- Skill proficiency
    proficiency_level VARCHAR(20), -- beginner, intermediate, advanced, expert
    years_experience DECIMAL(3,1),
    last_used_date DATE,
    
    -- Verification and confidence
    is_verified BOOLEAN DEFAULT FALSE,
    verification_source VARCHAR(100), -- cv_parsing, user_input, assessment
    confidence_score DECIMAL(3,2), -- 0.00 to 1.00
    
    -- Additional metadata
    skill_context TEXT, -- How/where this skill was used
    endorsements_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique combination
    UNIQUE(user_id, skill_id, cv_id)
);

-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_user_skills_user_id ON user_skills(user_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_skill_id ON user_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_cv_id ON user_skills(cv_id);
CREATE INDEX IF NOT EXISTS idx_user_skills_proficiency ON user_skills(proficiency_level);
CREATE INDEX IF NOT EXISTS idx_user_skills_years_experience ON user_skills(years_experience);
CREATE INDEX IF NOT EXISTS idx_user_skills_is_verified ON user_skills(is_verified);
CREATE INDEX IF NOT EXISTS idx_user_skills_confidence ON user_skills(confidence_score);

-- Add comments for documentation
COMMENT ON TABLE user_skills IS 'Junction table linking users to their skills with proficiency levels';
COMMENT ON COLUMN user_skills.proficiency_level IS 'Skill proficiency: beginner, intermediate, advanced, expert';
COMMENT ON COLUMN user_skills.years_experience IS 'Years of experience with this skill';
COMMENT ON COLUMN user_skills.verification_source IS 'How this skill was verified: cv_parsing, user_input, assessment';
COMMENT ON COLUMN user_skills.confidence_score IS 'Confidence in skill assessment (0.00-1.00)';
COMMENT ON COLUMN user_skills.skill_context IS 'Context or description of how this skill was used';
