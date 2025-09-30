"""
Test module for analysis results endpoint in skills_analysis.py
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json
from datetime import datetime
import shutil
import os

from app.main import app
from app.utils.user_path_utils import get_user_base_path

# Test client
client = TestClient(app)

# Test data
TEST_COMPANY = "TestCompany"
TEST_USER_EMAIL = "test@example.com"
ADMIN_EMAIL = "admin@admin.com"
TEST_TOKEN = "test_token"  # We'll mock token verification

# Mock data for analysis file
MOCK_ANALYSIS_DATA = {
    "cv_skills": {
        "technical_skills": ["Python", "JavaScript"],
        "soft_skills": ["Communication", "Leadership"],
        "domain_keywords": ["Web Development", "API"]
    },
    "jd_skills": {
        "technical_skills": ["Python", "React"],
        "soft_skills": ["Communication", "Teamwork"],
        "domain_keywords": ["Web Development", "Frontend"]
    },
    "preextracted_comparison_entries": [
        {
            "timestamp": datetime.now().isoformat(),
            "model_used": "test_model",
            "content": "Technical Skills Match Rate: 75%\nSoft Skills Match Rate: 80%\nDomain Keywords Match Rate: 85%"
        }
    ],
    "component_analysis_entries": [
        {
            "timestamp": datetime.now().isoformat(),
            "extracted_scores": {
                "skills_relevance": 85,
                "experience_alignment": 80
            }
        }
    ],
    "ats_calculation_entries": [
        {
            "timestamp": datetime.now().isoformat(),
            "final_ats_score": 82,
            "category_status": "good"
        }
    ]
}

@pytest.fixture(autouse=True)
def setup_and_cleanup():
    """Setup test environment and clean up after tests"""
    # Setup base directories
    base_dir = Path("user")
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Create directories for both admin and test user
    for email in [ADMIN_EMAIL, TEST_USER_EMAIL]:
        # Create user-specific directory structure
        user_folder = f"user_{email}"
        user_base = base_dir / user_folder / "cv-analysis"
        user_base.mkdir(parents=True, exist_ok=True)
        
        # Create required subdirectories
        for subdir in ["applied_companies", "cvs/original", "cvs/tailored", "saved_jobs", "uploads"]:
            (user_base / subdir).mkdir(parents=True, exist_ok=True)
        
        # Create company directory and analysis file
        company_dir = user_base / "applied_companies" / TEST_COMPANY
        company_dir.mkdir(parents=True, exist_ok=True)
        
        # Create analysis file
        analysis_file = company_dir / f"{TEST_COMPANY}_skills_analysis.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(MOCK_ANALYSIS_DATA, f)
    
    yield
    
    # Cleanup after tests
    shutil.rmtree(base_dir, ignore_errors=True)

# Mock the token verification
def mock_verify_token(token):
    """Mock token verification for testing"""
    if token == TEST_TOKEN:
        return type("TokenData", (), {"email": TEST_USER_EMAIL})
    return None

# Patch the verify_token function
@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    """Mock authentication for tests"""
    monkeypatch.setattr("app.routes.skills_analysis.verify_token", mock_verify_token)

def test_get_analysis_results_without_token():
    """Test getting analysis results without auth token (should use admin path)"""
    response = client.get(f"/api/analysis-results/{TEST_COMPANY}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["company"] == TEST_COMPANY
    assert "skills_analysis" in data
    assert "preextracted_comparison" in data
    assert "component_analysis" in data
    assert "ats_score" in data
    
    # Verify data matches mock data
    assert data["skills_analysis"]["cv_skills"]["technical_skills"] == sorted(MOCK_ANALYSIS_DATA["cv_skills"]["technical_skills"])
    assert data["ats_score"]["final_ats_score"] == MOCK_ANALYSIS_DATA["ats_calculation_entries"][0]["final_ats_score"]

def test_get_analysis_results_with_valid_token():
    """Test getting analysis results with valid auth token"""
    response = client.get(
        f"/api/analysis-results/{TEST_COMPANY}",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["company"] == TEST_COMPANY
    # Verify all data components are present
    assert all(key in data for key in ["skills_analysis", "preextracted_comparison", "component_analysis", "ats_score"])

def test_get_analysis_results_company_not_found():
    """Test getting analysis results for non-existent company"""
    response = client.get("/api/analysis-results/NonExistentCompany")
    assert response.status_code == 404
    assert "error" in response.json()

def test_get_analysis_results_with_invalid_token():
    """Test getting analysis results with invalid auth token"""
    response = client.get(
        f"/api/analysis-results/{TEST_COMPANY}",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 200  # Should still work, falling back to admin
    
    data = response.json()
    assert data["company"] == TEST_COMPANY
    assert "skills_analysis" in data

def test_match_rates_extraction():
    """Test extraction of match rates from preextracted comparison"""
    response = client.get(f"/api/analysis-results/{TEST_COMPANY}")
    assert response.status_code == 200
    
    data = response.json()
    match_rates = data["preextracted_comparison"]["match_rates"]
    assert match_rates["technical_skills"] == 75
    assert match_rates["soft_skills"] == 80
    assert match_rates["domain_keywords"] == 85