"""
Pipeline metadata and file registry models
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger, UniqueConstraint, Index
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    # Use string user_id to avoid FK type mismatches with existing deployments (UUID vs INT)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)  # normalized key (e.g., Australia_for_UNHCR)
    display_name = Column(String(255), nullable=True)
    jd_url = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_company_user_name"),
    )


class CompanyFile(Base):
    __tablename__ = "company_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)

    file_type = Column(String(50), nullable=False, index=True)  # original_cv, tailored_cv, jd_original, skills_analysis, input_recommendation, ai_recommendation, cv_jd_matching, component_analysis, job_info
    file_format = Column(String(10), nullable=True)  # json, txt
    filename = Column(String(255), nullable=False)
    file_path = Column(String(700), nullable=False)
    file_size = Column(BigInteger, nullable=True)
    sha256 = Column(String(64), nullable=True, index=True)
    timestamp = Column(String(20), nullable=True, index=True)  # from filename (YYYYMMDD_HHMMSS)

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("ix_company_files_latest", "user_id", "company_id", "file_type", "timestamp"),
        UniqueConstraint("user_id", "company_id", "file_type", "sha256", name="uq_company_files_dedupe"),
    )


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    kind = Column(String(30), nullable=False, index=True)  # skills, cv_jd, component, input_reco, ai_reco, tailoring
    status = Column(String(20), default="completed", index=True)  # pending, running, completed, failed
    model_used = Column(String(100), nullable=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    meta_json = Column(JSONB, nullable=True)

    source_file_id = Column(Integer, ForeignKey("company_files.id"), nullable=True)
    output_file_id = Column(Integer, ForeignKey("company_files.id"), nullable=True)

    __table_args__ = (
        Index("ix_analysis_runs_latest", "user_id", "company_id", "kind", "started_at"),
    )


class CVVersion(Base):
    __tablename__ = "cv_versions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    cv_type = Column(String(20), nullable=False, index=True)  # original, tailored
    file_id = Column(Integer, ForeignKey("company_files.id"), nullable=False)
    preferred = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", "cv_type", name="uq_cv_versions_pointer"),
    )


