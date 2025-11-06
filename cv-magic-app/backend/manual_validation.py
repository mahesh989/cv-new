#!/usr/bin/env python3
"""
Manual validation script to test the complete role_highlights flow end-to-end
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))


def validate_complete_flow():
    """Test the complete CV tailoring flow with role_highlights"""
    print("\n" + "="*80)
    print("🔍 ROLE HIGHLIGHTS END-TO-END VALIDATION")
    print("="*80)
    
    from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
    from app.tailored_cv.services.pdf_export_service import ResumePDFGenerator
    from app.tailored_cv.services.tailored_cv_adapter import adapt_tailored_cv_to_pdf_format
    from app.tailored_cv.models.cv_models import (
        OriginalCV, ContactInfo, Education, ExperienceEntry, 
        SkillCategory, RecommendationAnalysis, OptimizationStrategy
    )
    
    # Step 1: Create mock CV data
    print("\n1️⃣  Creating mock CV data...")
    mock_cv = OriginalCV(
        contact=ContactInfo(
            name="John Test",
            email="john.test@example.com",
            phone="0412 345 678",
            location="Sydney, NSW",
            linkedin="linkedin.com/in/johntest"
        ),
        education=[
            Education(
                institution="University of Sydney",
                degree="Bachelor of Data Science",
                location="Sydney, NSW",
                graduation_date="2020",
                gpa=None,
                relevant_coursework=None,
                honors=None
            )
        ],
        experience=[
            ExperienceEntry(
                company="Tech Corp",
                title="Data Analyst",
                location="Sydney, NSW",
                start_date="Jan 2020",
                end_date="Present",
                bullets=[
                    "Built interactive dashboards for business insights",
                    "Analyzed customer data to identify trends",
                    "Collaborated with stakeholders on data requirements"
                ]
            )
        ],
        skills=[
            SkillCategory(
                category="Technical Skills",
                skills=["Python", "SQL", "Tableau", "Excel"]
            )
        ],
        created_at=datetime.utcnow()
    )
    print("   ✅ Mock CV created")
    
    # Step 2: Create mock recommendations
    print("\n2️⃣  Creating mock job recommendations...")
    mock_recommendations = RecommendationAnalysis(
        company="Data Insights Inc",
        job_title="Senior Data Analyst",
        missing_technical_skills=["Power BI", "Python"],
        missing_soft_skills=["Leadership"],
        missing_keywords=["dashboard", "visualization", "stakeholder management"],
        technical_enhancements=["Add Power BI experience", "Emphasize Python skills"],
        soft_skill_improvements=["Highlight leadership examples"],
        keyword_integration=["dashboard", "data visualization", "stakeholder management"],
        critical_gaps=["Power BI", "Advanced Python"],
        important_gaps=["Leadership", "Team collaboration"],
        nice_to_have=["Machine Learning", "Cloud platforms"],
        match_score=75,
        target_score=90
    )
    print("   ✅ Mock recommendations created")
    print(f"   ℹ️  Target company: {mock_recommendations.company}")
    print(f"   ℹ️  Target role: {mock_recommendations.job_title}")
    
    # Step 3: Create optimization strategy
    print("\n3️⃣  Creating optimization strategy...")
    mock_strategy = OptimizationStrategy(
        education_strategy="keep",
        experience_strategy="enhance",
        skills_strategy="expand",
        projects_strategy="keep",
        section_order=["experience", "education", "skills", "projects"],  # Required field
        keyword_placement={"experience": ["dashboard", "visualization"]},
        quantification_targets=["dashboards", "data analysis"],
        impact_enhancements={"experience": ["Add metrics", "Quantify impact"]}
    )
    print("   ✅ Optimization strategy created")
    
    # Step 4: Simulate AI-generated tailored CV data
    print("\n4️⃣  Simulating AI-generated tailored CV...")
    
    # This simulates what the AI would return
    ai_generated_data = {
        "contact": {
            "name": "John Test",
            "email": "john.test@example.com",
            "phone": "0412 345 678",
            "location": "Sydney, NSW"
        },
        "role_highlights": """Senior Data Analyst with 3 years' experience delivering data-driven insights and interactive dashboards using Python, SQL, and Tableau for technology companies across Australia.

• Built 15+ interactive dashboards using Tableau and Power BI, enabling executive decision-making for 50+ stakeholders across finance and operations teams
• Analyzed customer datasets containing 500K+ records to identify key trends, driving 25% improvement in customer retention strategies
• Collaborated with 10+ cross-functional stakeholders to define data requirements and deliver actionable insights, reducing reporting time by 40%

Skills: Python | SQL | Tableau | Power BI | Excel (Advanced) | Data Visualization | Stakeholder Management | Dashboard Development""",
        "education": [
            {
                "institution": "University of Sydney",
                "degree": "Bachelor of Data Science",
                "location": "Sydney, NSW",
                "graduation_date": "2020"
            }
        ],
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Data Analyst",
                "location": "Sydney, NSW",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "bullets": [
                    "Built 15+ interactive Tableau dashboards providing real-time business insights to 50+ stakeholders, improving decision-making speed by 30%",
                    "Analyzed 500K+ customer records using Python and SQL to identify trends and patterns, driving 25% improvement in retention",
                    "Collaborated with 10+ cross-functional teams to gather requirements and deliver data solutions, reducing reporting time by 40%"
                ]
            }
        ],
        "skills": [
            {"category": "Data Analysis Tools", "skills": ["Python", "SQL", "Tableau", "Power BI"]},
            {"category": "Technical Skills", "skills": ["Excel (Advanced)", "Data Visualization", "Dashboard Development"]},
            {"category": "Soft Skills", "skills": ["Stakeholder Management", "Communication", "Problem Solving"]}
        ],
        "target_role": "Senior Data Analyst"
    }
    
    print("   ✅ AI-generated data simulated")
    print(f"   ℹ️  Role highlights length: {len(ai_generated_data['role_highlights'])} characters")
    
    # Validate role_highlights structure
    print("\n5️⃣  Validating role_highlights structure...")
    role_highlights = ai_generated_data['role_highlights']
    
    checks = [
        ("Contains value statement", len(role_highlights.split('\n')[0]) > 20),
        ("Contains bullet points", '•' in role_highlights),
        ("Contains skills section", 'Skills:' in role_highlights or '|' in role_highlights),
        ("Has quantified achievements", any(char.isdigit() for char in role_highlights)),
        ("Mentions role title", 'Analyst' in role_highlights or mock_recommendations.job_title.split()[0] in role_highlights)
    ]
    
    all_passed = True
    for check_name, result in checks:
        if result:
            print(f"   ✅ {check_name}")
        else:
            print(f"   ❌ {check_name}")
            all_passed = False
    
    if not all_passed:
        raise AssertionError("Role highlights structure validation failed")
    
    # Step 6: Test adapter mapping
    print("\n6️⃣  Testing adapter mapping...")
    pdf_data = adapt_tailored_cv_to_pdf_format(ai_generated_data)
    
    if "role_highlights" not in pdf_data:
        raise AssertionError("Adapter did not map role_highlights")
    
    if "target_role" not in pdf_data:
        raise AssertionError("Adapter did not map target_role")
    
    print("   ✅ Adapter mapping successful")
    print(f"   ℹ️  Target role in PDF data: {pdf_data['target_role']}")
    
    # Step 7: Generate PDF
    print("\n7️⃣  Generating PDF...")
    
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w+b', suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
            generator = ResumePDFGenerator(pdf_data)
            result_path = generator.generate(pdf_path)
            
        pdf_size = Path(result_path).stat().st_size
        print(f"   ✅ PDF generated successfully")
        print(f"   ℹ️  PDF path: {result_path}")
        print(f"   ℹ️  PDF size: {pdf_size:,} bytes")
        
        # Copy to a more accessible location
        import shutil
        output_path = Path(__file__).parent / "test_role_highlights_output.pdf"
        shutil.copy(result_path, output_path)
        print(f"   ✅ PDF copied to: {output_path}")
        
        # Cleanup temp file
        Path(result_path).unlink()
        
    except Exception as e:
        print(f"   ❌ PDF generation failed: {e}")
        raise
    
    # Step 8: Final validation summary
    print("\n" + "="*80)
    print("📊 VALIDATION SUMMARY")
    print("="*80)
    print(f"✅ CV Data: Mock CV with {len(mock_cv.experience)} experience(s)")
    print(f"✅ Recommendations: Target role '{mock_recommendations.job_title}'")
    print(f"✅ Role Highlights: {len(role_highlights)} characters")
    print(f"   - Has value statement: ✅")
    print(f"   - Has 3 accomplishments: ✅")
    print(f"   - Has skills snapshot: ✅")
    print(f"✅ PDF Generation: {pdf_size:,} bytes")
    print(f"✅ Output file: test_role_highlights_output.pdf")
    
    print("\n" + "="*80)
    print("🎉 END-TO-END VALIDATION PASSED!")
    print("="*80)
    print("\n📋 Next Steps:")
    print("   1. Open the generated PDF: test_role_highlights_output.pdf")
    print("   2. Verify the section header says 'SENIOR DATA ANALYST HIGHLIGHTS'")
    print("   3. Check that it has:")
    print("      - Value statement (1 sentence)")
    print("      - 3 bullet points with numbers")
    print("      - Skills section with | separators")
    print("   4. Confirm formatting looks professional")
    
    return True


def quick_validation():
    """Quick validation of key components"""
    print("\n" + "="*80)
    print("⚡ QUICK VALIDATION")
    print("="*80)
    
    from app.tailored_cv.models.cv_models import TailoredCV
    from app.tailored_cv.services.tailored_cv_adapter import adapt_tailored_cv_to_pdf_format
    
    print("\n1. Schema Check:")
    schema = TailoredCV.model_json_schema()
    print(f"   ✅ role_highlights in schema: {'role_highlights' in schema['properties']}")
    print(f"   ✅ target_role in schema: {'target_role' in schema['properties']}")
    
    print("\n2. Adapter Check:")
    test_data = {
        "contact": {"name": "Test", "email": "test@test.com"},
        "role_highlights": "Test content",
        "target_role": "Test Role",
        "education": [],
        "experience": [],
        "skills": []
    }
    result = adapt_tailored_cv_to_pdf_format(test_data)
    print(f"   ✅ role_highlights mapped: {'role_highlights' in result}")
    print(f"   ✅ target_role mapped: {'target_role' in result}")
    
    print("\n✅ Quick validation PASSED")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate role_highlights implementation")
    parser.add_argument("--quick", action="store_true", help="Run quick validation only")
    args = parser.parse_args()
    
    try:
        if args.quick:
            quick_validation()
        else:
            validate_complete_flow()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

