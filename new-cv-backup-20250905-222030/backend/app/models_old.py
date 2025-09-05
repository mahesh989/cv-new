"""
Database models for CV Agent application
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class CVUploadRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class CVUploadResponse(BaseModel):
    id: str = Field(..., description="Unique CV identifier")
    filename: str = Field(..., description="Original filename")
    title: Optional[str] = None
    description: Optional[str] = None
    file_size: int = Field(..., description="File size in bytes")
    file_type: FileType = Field(..., description="File type")
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    text_content: Optional[str] = None
    
    class Config:
        use_enum_values = True


class CVInfo(BaseModel):
    id: str
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None
    file_size: int
    file_type: FileType
    upload_date: datetime
    processing_status: ProcessingStatus
    text_length: Optional[int] = None
    
    class Config:
        use_enum_values = True


class CVListResponse(BaseModel):
    cvs: List[CVInfo]
    total: int
    page: int
    limit: int


class CVContentResponse(BaseModel):
    id: str
    filename: str
    title: Optional[str] = None
    text_content: str
    file_type: FileType
    processing_status: ProcessingStatus
    
    class Config:
        use_enum_values = True


class JDExtractionRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None
    
    def validate_input(self):
        if not self.url and not self.text:
            raise ValueError("Either URL or text must be provided")
        if self.url and self.text:
            raise ValueError("Provide either URL or text, not both")


class JDExtractionResponse(BaseModel):
    id: str = Field(..., description="Unique JD identifier") 
    source_url: Optional[str] = None
    source_type: str = Field(..., description="'url' or 'text'")
    extracted_text: str = Field(..., description="Cleaned job description text")
    extraction_date: datetime = Field(default_factory=datetime.utcnow)
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.COMPLETED)
    text_length: int = Field(..., description="Length of extracted text")
    
    class Config:
        use_enum_values = True


class SkillExtractionRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Text to extract skills from")
    ai_model: Optional[str] = Field(default="gpt-4o-mini", description="AI model to use")


class SkillExtractionResponse(BaseModel):
    technical_skills: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    domain_keywords: List[str] = Field(default_factory=list)
    ai_model_used: str
    processing_time: float = Field(..., description="Processing time in seconds")
    
    
class CVAnalysisRequest(BaseModel):
    cv_id: str = Field(..., description="CV identifier")
    jd_id: Optional[str] = None
    jd_text: Optional[str] = None
    ai_model: Optional[str] = Field(default="gpt-4o-mini")
    
    def validate_jd_input(self):
        if not self.jd_id and not self.jd_text:
            raise ValueError("Either jd_id or jd_text must be provided")


class CVAnalysisResponse(BaseModel):
    id: str = Field(..., description="Analysis identifier")
    cv_id: str
    jd_id: Optional[str] = None
    analysis_result: str = Field(..., description="AI analysis result")
    ai_model_used: str
    processing_time: float
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    details: Optional[str] = None
    error_code: Optional[str] = None
    
    
class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message")
    data: Optional[dict] = None


class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    uptime: Optional[float] = None
