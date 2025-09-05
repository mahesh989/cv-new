"""
CV and job application related database models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CV(Base):
    """CV file storage model"""
    
    __tablename__ = "cvs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    title = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    file_type = Column(String(100), nullable=False)  # MIME type
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Analysis data (if CV has been analyzed)
    technical_skills = Column(Text, nullable=True)  # JSON string
    soft_skills = Column(Text, nullable=True)  # JSON string
    domain_keywords = Column(Text, nullable=True)  # JSON string
    analyzed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<CV(user_id={self.user_id}, filename='{self.filename}')>"


class JobApplication(Base):
    """Job application tracking model"""
    
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=True, index=True)
    
    # Job details
    job_title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    job_url = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    
    # Application details
    application_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="applied")  # applied, pending, interview, rejected, accepted
    notes = Column(Text, nullable=True)
    
    # Analysis results (if job was analyzed against CV)
    match_score = Column(Integer, nullable=True)  # Percentage match
    matched_skills = Column(Text, nullable=True)  # JSON string
    missing_skills = Column(Text, nullable=True)  # JSON string
    recommendations = Column(Text, nullable=True)  # JSON string
    analyzed_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<JobApplication(user_id={self.user_id}, job_title='{self.job_title}', company='{self.company}')>"


class CVAnalysis(Base):
    """CV analysis results model"""
    
    __tablename__ = "cv_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Extracted skills and information
    technical_skills = Column(Text, nullable=True)  # JSON string
    soft_skills = Column(Text, nullable=True)  # JSON string
    domain_keywords = Column(Text, nullable=True)  # JSON string
    experience_years = Column(Integer, nullable=True)
    education = Column(Text, nullable=True)
    
    # Analysis metadata
    analysis_version = Column(String(10), default="1.0")
    analysis_model = Column(String(50), nullable=True)  # e.g., "gpt-4", "claude-3"
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<CVAnalysis(cv_id={self.cv_id}, user_id={self.user_id})>"


class JobComparison(Base):
    """Job comparison results model"""
    
    __tablename__ = "job_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=False, index=True)
    job_application_id = Column(Integer, ForeignKey("job_applications.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job requirements (extracted from job description)
    required_technical_skills = Column(Text, nullable=True)  # JSON string
    required_soft_skills = Column(Text, nullable=True)  # JSON string
    required_domain_keywords = Column(Text, nullable=True)  # JSON string
    
    # Comparison results
    match_score = Column(Integer, nullable=False)  # Overall match percentage
    matched_technical_skills = Column(Text, nullable=True)  # JSON string
    matched_soft_skills = Column(Text, nullable=True)  # JSON string
    matched_domain_keywords = Column(Text, nullable=True)  # JSON string
    missing_technical_skills = Column(Text, nullable=True)  # JSON string
    missing_soft_skills = Column(Text, nullable=True)  # JSON string
    missing_domain_keywords = Column(Text, nullable=True)  # JSON string
    
    # AI-generated recommendations
    recommendations = Column(Text, nullable=True)  # JSON string
    
    # Comparison metadata
    comparison_version = Column(String(10), default="1.0")
    comparison_model = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<JobComparison(cv_id={self.cv_id}, user_id={self.user_id}, match_score={self.match_score})>"
