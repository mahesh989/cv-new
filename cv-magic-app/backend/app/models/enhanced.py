"""
Enhanced Pydantic models for the CV analysis system

These models are used for API request/response validation and data serialization
for the enhanced CV processing, JD extraction, and analysis features.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


# Enums
class FileType(str, Enum):
    """Supported file types"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ProcessingStatus(str, Enum):
    """Processing status for async operations"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JDSource(str, Enum):
    """Job description sources"""
    URL = "url"
    DIRECT_TEXT = "direct_text"
    FILE_UPLOAD = "file_upload"


class AnalysisType(str, Enum):
    """Types of CV-JD analysis"""
    SKILL_MATCH = "skill_match"
    EXPERIENCE_MATCH = "experience_match"
    OVERALL_FIT = "overall_fit"


# Base response models
class SuccessResponse(BaseModel):
    """Generic success response"""
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Generic error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# CV Models
class CVInfo(BaseModel):
    """CV information model"""
    id: str
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None
    file_type: FileType
    file_size: int
    processing_status: ProcessingStatus
    upload_date: datetime
    updated_date: Optional[datetime] = None


class CVUploadResponse(BaseModel):
    """Response model for CV upload"""
    id: str
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None
    file_type: FileType
    file_size: int
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    upload_date: datetime = Field(default_factory=datetime.now)
    message: str = "CV uploaded successfully and processing started"


class CVListResponse(BaseModel):
    """Response model for CV list"""
    cvs: List[CVInfo]
    total: int
    page: int
    limit: int


class CVContentResponse(BaseModel):
    """Response model for CV content"""
    id: str
    filename: str
    title: Optional[str] = None
    text_content: str
    file_type: FileType
    processing_status: ProcessingStatus


# JD Models
class JDInfo(BaseModel):
    """Job description information model"""
    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    source_url: str
    source: JDSource
    processing_status: ProcessingStatus
    extraction_date: datetime
    updated_date: Optional[datetime] = None


class JDExtractionResponse(BaseModel):
    """Response model for JD extraction"""
    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    source_url: str
    source: JDSource
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    extraction_date: datetime = Field(default_factory=datetime.now)
    message: str = "JD extraction started successfully"


class JDListResponse(BaseModel):
    """Response model for JD list"""
    jds: List[JDInfo]
    total: int
    page: int
    limit: int


class JDContentResponse(BaseModel):
    """Response model for JD content"""
    id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    source_url: str
    source: JDSource
    content: str
    processing_status: ProcessingStatus


# Analysis Models
class AnalysisInfo(BaseModel):
    """Analysis information model"""
    id: str
    cv_id: str
    jd_id: str
    analysis_type: AnalysisType
    processing_status: ProcessingStatus
    analysis_date: datetime
    updated_date: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    """Response model for analysis creation"""
    id: str
    cv_id: str
    jd_id: str
    analysis_type: AnalysisType
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    analysis_date: datetime = Field(default_factory=datetime.now)
    message: str = "Analysis started successfully"


class AnalysisListResponse(BaseModel):
    """Response model for analysis list"""
    analyses: List[AnalysisInfo]
    total: int
    page: int
    limit: int


class AnalysisResultResponse(BaseModel):
    """Response model for analysis result"""
    id: str
    cv_id: str
    jd_id: str
    analysis_type: AnalysisType
    result: Dict[str, Any]
    processing_status: ProcessingStatus


# Additional models for API requests
class CVStatsResponse(BaseModel):
    """Response model for CV statistics"""
    cv_id: str
    filename: str
    file_size_bytes: int
    file_size_mb: float
    file_type: FileType
    processing_status: ProcessingStatus
    upload_date: datetime
    text_length: Optional[int] = None
    word_count: Optional[int] = None
    has_email: Optional[bool] = None
    has_phone: Optional[bool] = None
    has_skills_section: Optional[bool] = None
    has_experience_section: Optional[bool] = None
    has_education_section: Optional[bool] = None


class JDStatsResponse(BaseModel):
    """Response model for JD statistics"""
    jd_id: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    source: JDSource
    source_url: str
    processing_status: ProcessingStatus
    extraction_date: datetime
    content_length: Optional[int] = None
    word_count: Optional[int] = None
    has_requirements: Optional[bool] = None
    has_skills: Optional[bool] = None
    has_experience: Optional[bool] = None
    has_salary: Optional[bool] = None



class URLTestResponse(BaseModel):
    """Response model for URL extraction testing"""
    success: bool
    url: str
    extracted_title: Optional[str] = None
    extracted_company: Optional[str] = None
    extracted_location: Optional[str] = None
    content_preview: str
    content_length: int
    word_count: int
    key_info: Dict[str, Any]
    extraction_method: str


class SupportedSitesResponse(BaseModel):
    """Response model for supported sites list"""
    supported_sites: List[Dict[str, str]]
    total_sites: int
    note: str


# Detailed analysis result models
class SkillMatchResult(BaseModel):
    """Skill match analysis result"""
    analysis_type: str = "skill_match"
    cv_skills: List[str]
    jd_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]
    match_percentage: float
    total_cv_skills: int
    total_jd_skills: int
    matched_count: int
    suggestions: List[str]
    analysis_date: str


class ExperienceMatchResult(BaseModel):
    """Experience match analysis result"""
    analysis_type: str = "experience_match"
    cv_experience_score: int
    jd_experience_requirements: int
    experience_match_percentage: float
    suggestions: List[str]
    analysis_date: str


class OverallFitResult(BaseModel):
    """Overall fit analysis result"""
    analysis_type: str = "overall_fit"
    overall_score: float
    fit_level: str
    skill_match: SkillMatchResult
    experience_match: ExperienceMatchResult
    recommendations: List[str]
    analysis_date: str
