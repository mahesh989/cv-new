"""
Pydantic models for CV generation and tailoring functionality
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Career experience levels"""
    ENTRY_LEVEL = "entry_level"  # 0-2 years
    MID_LEVEL = "mid_level"      # 3-7 years
    SENIOR_LEVEL = "senior_level"  # 7+ years


class ContactInfo(BaseModel):
    """Contact information structure"""
    name: str = Field(..., description="Full name")
    phone: Optional[str] = Field(None, description="Phone number")
    email: str = Field(..., description="Email address")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile URL")
    location: Optional[str] = Field(None, description="Current location")
    website: Optional[str] = Field(None, description="Personal website/portfolio")


class Education(BaseModel):
    """Education entry structure"""
    institution: str = Field(..., description="School/University name")
    degree: str = Field(..., description="Degree type and field")
    location: Optional[str] = Field(None, description="Institution location")
    graduation_date: Optional[str] = Field(None, description="Graduation date")
    gpa: Optional[str] = Field(None, description="GPA if relevant (>3.5)")
    relevant_coursework: Optional[List[str]] = Field(None, description="Relevant courses")
    honors: Optional[List[str]] = Field(None, description="Academic honors/achievements")


class ExperienceEntry(BaseModel):
    """Work experience entry structure"""
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    location: Optional[str] = Field(None, description="Work location")
    start_date: str = Field(..., description="Start date")
    end_date: Optional[str] = Field(None, description="End date (None if current)")
    duration: Optional[str] = Field(None, description="Duration string")
    bullets: List[str] = Field(..., description="Achievement bullets (max 4)")
    skills_used: Optional[List[str]] = Field(None, description="Technologies/skills used")


class Project(BaseModel):
    """Project entry structure"""
    name: str = Field(..., description="Project name")
    context: Optional[str] = Field(None, description="Project context/description")
    technologies: Optional[List[str]] = Field(None, description="Technologies used")
    bullets: List[str] = Field(..., description="Project achievements/outcomes")
    url: Optional[str] = Field(None, description="Project URL/repository")
    duration: Optional[str] = Field(None, description="Project duration")


class SkillCategory(BaseModel):
    """Skill category structure"""
    category: str = Field(..., description="Category name (e.g., 'Programming Languages')")
    skills: List[str] = Field(..., description="List of skills in this category")


class OriginalCV(BaseModel):
    """Original CV data structure"""
    contact: ContactInfo
    education: List[Education]
    experience: List[ExperienceEntry]
    projects: Optional[List[Project]] = Field(None, description="Projects section")
    skills: List[SkillCategory] = Field(..., description="Categorized skills")
    
    # Metadata
    experience_level: Optional[ExperienceLevel] = Field(None, description="Calculated experience level")
    total_years_experience: Optional[int] = Field(None, description="Total years of experience")
    created_at: Optional[datetime] = Field(None, description="CV creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class RecommendationAnalysis(BaseModel):
    """Recommendation analysis structure from CV-JD matching"""
    company: str = Field(..., description="Target company name")
    job_title: str = Field(..., description="Target job title")
    
    # Gap Analysis
    missing_technical_skills: List[str] = Field(..., description="Technical skills gaps")
    missing_soft_skills: List[str] = Field(..., description="Soft skills gaps")
    missing_keywords: List[str] = Field(..., description="Missing domain keywords")
    
    # Enhancement Recommendations
    technical_enhancements: List[str] = Field(..., description="Technical skills to add/emphasize")
    soft_skill_improvements: List[str] = Field(..., description="Soft skills to highlight")
    keyword_integration: List[str] = Field(..., description="Keywords to naturally integrate")
    
    # Company-Specific
    company_values: Optional[List[str]] = Field(None, description="Company values to align with")
    industry_terminology: Optional[List[str]] = Field(None, description="Industry-specific terms")
    culture_alignment: Optional[List[str]] = Field(None, description="Cultural alignment suggestions")
    
    # Priority Levels
    critical_gaps: List[str] = Field(..., description="Priority 1 - Critical missing elements")
    important_gaps: List[str] = Field(..., description="Priority 2 - Important improvements")
    nice_to_have: List[str] = Field(..., description="Priority 3 - Enhancement opportunities")
    
    # Metadata
    match_score: Optional[int] = Field(None, description="Current CV-JD match score")
    target_score: Optional[int] = Field(None, description="Target score after optimization")
    analysis_date: Optional[datetime] = Field(None, description="Analysis timestamp")


class OptimizationStrategy(BaseModel):
    """CV optimization strategy"""
    section_order: List[str] = Field(..., description="Recommended section order")
    education_strategy: str = Field(..., description="How to position education")
    keyword_placement: Dict[str, List[str]] = Field(..., description="Where to place keywords")
    quantification_targets: List[str] = Field(..., description="Areas needing quantification")
    impact_enhancements: Dict[str, List[str]] = Field(..., description="Impact statement improvements")


class TailoredCV(BaseModel):
    """Tailored CV data structure - FULL VERSION with all metadata"""
    # Core CV Structure
    contact: ContactInfo
    education: List[Education]
    experience: List[ExperienceEntry]
    projects: Optional[List[Project]] = Field(None, description="Enhanced projects section")
    skills: List[SkillCategory] = Field(..., description="Optimized categorized skills")
    
    # Optimization Metadata
    source_cv_id: Optional[str] = Field(None, description="Original CV identifier")
    target_company: str = Field(..., description="Target company name")
    target_role: str = Field(..., description="Target job title")
    optimization_strategy: OptimizationStrategy = Field(..., description="Applied optimization strategy")
    
    # Enhancement Summary
    enhancements_applied: Dict[str, Any] = Field(..., description="Summary of applied enhancements")
    keywords_integrated: List[str] = Field(..., description="Successfully integrated keywords")
    quantifications_added: List[str] = Field(..., description="New quantifications added")
    
    # Quality Metrics
    estimated_ats_score: Optional[int] = Field(None, description="Estimated ATS score")
    keyword_density: Optional[Dict[str, float]] = Field(None, description="Keyword density analysis")
    impact_statement_compliance: Optional[float] = Field(None, description="% bullets following impact formula")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    framework_version: str = Field(default="1.0", description="Framework version used")


class CleanTailoredCV(BaseModel):
    """Clean tailored CV data structure - ONLY CV content, no metadata"""
    # Core CV Structure Only
    contact: ContactInfo
    education: List[Education]
    experience: List[ExperienceEntry]
    projects: Optional[List[Project]] = Field(None, description="Projects section")
    skills: List[SkillCategory] = Field(..., description="Skills")
    
    # Minimal metadata for tracking
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_edited: Optional[datetime] = Field(None, description="Last edit timestamp")
    manually_edited: Optional[bool] = Field(False, description="Whether manually edited")
    

class CVTailoringRequest(BaseModel):
    """Request model for CV tailoring"""
    original_cv: OriginalCV = Field(..., description="Original CV data")
    recommendations: RecommendationAnalysis = Field(..., description="Recommendation analysis")
    company_folder: Optional[str] = Field(None, description="Company-specific folder path")
    custom_instructions: Optional[str] = Field(None, description="Additional tailoring instructions")
    target_ats_score: Optional[int] = Field(80, description="Target ATS score")
    

class CVTailoringResponse(BaseModel):
    """Response model for CV tailoring"""
    tailored_cv: TailoredCV = Field(..., description="Generated tailored CV")
    processing_summary: Dict[str, Any] = Field(..., description="Processing summary and statistics")
    recommendations_applied: List[str] = Field(..., description="List of applied recommendations")
    warnings: Optional[List[str]] = Field(None, description="Any warnings or limitations")
    success: bool = Field(True, description="Processing success status")


class CVValidationError(BaseModel):
    """CV validation error structure"""
    field: str = Field(..., description="Field with error")
    message: str = Field(..., description="Error message")
    severity: str = Field(..., description="Error severity: error, warning, info")


class CVValidationResult(BaseModel):
    """CV validation result"""
    is_valid: bool = Field(..., description="Overall validation status")
    errors: List[CVValidationError] = Field(..., description="Validation errors")
    warnings: List[CVValidationError] = Field(..., description="Validation warnings")
    suggestions: List[str] = Field(..., description="Improvement suggestions")


# Utility Models for API Responses

class CompanyRecommendation(BaseModel):
    """Company-specific recommendation file structure"""
    company: str
    job_title: str
    recommendations: RecommendationAnalysis
    file_path: str
    last_updated: datetime


class AvailableCompanies(BaseModel):
    """Available companies with recommendations"""
    companies: List[CompanyRecommendation] = Field(..., description="List of available companies")
    total_count: int = Field(..., description="Total number of companies")


class ProcessingStatus(BaseModel):
    """CV processing status"""
    status: str = Field(..., description="Processing status")
    progress: int = Field(..., description="Progress percentage")
    current_step: str = Field(..., description="Current processing step")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    message: Optional[str] = Field(None, description="Status message")