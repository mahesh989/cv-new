"""Test to create actual directory structure with sample files in backend"""

import json
from pathlib import Path
from datetime import datetime
import shutil

def create_test_structure():
    # Configuration
    user_email = "admin@admin.com"
    company = "Test_Company_XYZ"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = Path("user/user_admin@admin.com/cv-analysis")

    print(f"\n🔨 Creating test structure for {company} at {timestamp}\n")

    try:
        # Clear existing test directory if it exists
        if (base_dir / "applied_companies" / company).exists():
            shutil.rmtree(base_dir / "applied_companies" / company)

        # 1. Create directory structure
        dirs_to_create = [
            base_dir / "applied_companies" / company,
            base_dir / "cvs" / "original",
            base_dir / "cvs" / "tailored",
            base_dir / "saved_jobs",
            base_dir / "uploads"
        ]

        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_path}")

        # 2. Create test files with realistic content
        
        # 2.1 Original CV files
        cv_content = {
            "text": "John Doe\nSenior Software Engineer\n\nExperience:\n- Lead Developer at Tech Corp\n- Senior Engineer at StartupX\n\nSkills:\nPython, AWS, React, TypeScript",
            "saved_at": datetime.now().isoformat(),
            "sections": {
                "personal_info": {"name": "John Doe", "title": "Senior Software Engineer"},
                "experience": [
                    {"company": "Tech Corp", "role": "Lead Developer", "duration": "2020-2023"},
                    {"company": "StartupX", "role": "Senior Engineer", "duration": "2018-2020"}
                ],
                "skills": ["Python", "AWS", "React", "TypeScript"]
            }
        }
        
        with open(base_dir / "cvs/original/original_cv.json", 'w') as f:
            json.dump(cv_content, f, indent=2)
        print(f"✅ Created: cvs/original/original_cv.json")

        with open(base_dir / "cvs/original/original_cv.txt", 'w') as f:
            f.write(cv_content["text"])
        print(f"✅ Created: cvs/original/original_cv.txt")

        # 2.2 Company analysis files
        # JD Original
        jd_content = {
            "text": f"Senior Software Engineer position at {company}\n\nRequired Skills:\n- Python\n- AWS\n- React\n- TypeScript",
            "saved_at": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"jd_original_{timestamp}.json", 'w') as f:
            json.dump(jd_content, f, indent=2)
        print(f"✅ Created: jd_original_{timestamp}.json")

        # Job Info
        job_info = {
            "company": company,
            "title": "Senior Software Engineer",
            "location": "Remote",
            "salary_range": "120k-150k",
            "posted_date": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"job_info_{company}_{timestamp}.json", 'w') as f:
            json.dump(job_info, f, indent=2)
        print(f"✅ Created: job_info_{company}_{timestamp}.json")

        # JD Analysis
        jd_analysis = {
            "required_skills": ["Python", "AWS", "React", "TypeScript"],
            "preferred_skills": ["Docker", "Kubernetes"],
            "experience_required": "5+ years",
            "analysis_timestamp": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"jd_analysis_{timestamp}.json", 'w') as f:
            json.dump(jd_analysis, f, indent=2)
        print(f"✅ Created: jd_analysis_{timestamp}.json")

        # Skills Analysis
        skills_analysis = {
            "matched_skills": ["Python", "AWS", "React", "TypeScript"],
            "missing_skills": ["Docker", "Kubernetes"],
            "score": 85,
            "analysis_timestamp": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"{company}_skills_analysis_{timestamp}.json", 'w') as f:
            json.dump(skills_analysis, f, indent=2)
        print(f"✅ Created: {company}_skills_analysis_{timestamp}.json")

        # CV-JD Matching
        matching = {
            "match_score": 85,
            "matched_requirements": ["Python", "AWS", "React", "TypeScript"],
            "missing_requirements": ["Docker", "Kubernetes"],
            "analysis_timestamp": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"cv_jd_matching_{timestamp}.json", 'w') as f:
            json.dump(matching, f, indent=2)
        print(f"✅ Created: cv_jd_matching_{timestamp}.json")

        # Component Analysis
        component_analysis = {
            "skills_score": 85,
            "experience_score": 90,
            "education_score": 80,
            "overall_score": 85,
            "analysis_timestamp": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"component_analysis_{timestamp}.json", 'w') as f:
            json.dump(component_analysis, f, indent=2)
        print(f"✅ Created: component_analysis_{timestamp}.json")

        # Input Recommendation
        input_recommendation = {
            "recommendations": [
                "Add Kubernetes experience",
                "Highlight Docker projects",
                "Add more detail about AWS implementations"
            ],
            "timestamp": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"{company}_input_recommendation_{timestamp}.json", 'w') as f:
            json.dump(input_recommendation, f, indent=2)
        print(f"✅ Created: {company}_input_recommendation_{timestamp}.json")

        # AI Recommendation
        ai_recommendation = {
            "improvements": [
                {
                    "section": "Skills",
                    "suggestions": ["Add Kubernetes skills", "Mention Docker experience"]
                },
                {
                    "section": "Experience",
                    "suggestions": ["Add metrics to AWS implementations", "Highlight team leadership"]
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        with open(base_dir / "applied_companies" / company / f"{company}_ai_recommendation_{timestamp}.json", 'w') as f:
            json.dump(ai_recommendation, f, indent=2)
        print(f"✅ Created: {company}_ai_recommendation_{timestamp}.json")

        # Tailored CV
        tailored_cv = {
            **cv_content,
            "tailored_for": company,
            "tailored_at": datetime.now().isoformat(),
            "modifications": [
                "Added Kubernetes learning projects",
                "Highlighted AWS implementations",
                "Added metrics to achievements"
            ]
        }
        with open(base_dir / "cvs/tailored" / f"{company}_tailored_cv_{timestamp}.json", 'w') as f:
            json.dump(tailored_cv, f, indent=2)
        print(f"✅ Created: {company}_tailored_cv_{timestamp}.json")

        # Saved Jobs
        saved_jobs = {
            "jobs": [job_info],
            "last_updated": datetime.now().isoformat(),
            "total_jobs": 1
        }
        with open(base_dir / "saved_jobs/saved_jobs.json", 'w') as f:
            json.dump(saved_jobs, f, indent=2)
        print(f"✅ Created: saved_jobs/saved_jobs.json")

        # Upload a dummy PDF
        with open(base_dir / "uploads/sample_cv.pdf", 'w') as f:
            f.write("Dummy PDF content")
        print(f"✅ Created: uploads/sample_cv.pdf")

        print(f"\n✨ Test structure created successfully at {base_dir}!")

        # Verify the structure
        print("\n🔍 Verifying structure...")
        all_files = list(Path(base_dir).rglob("*.*"))
        print(f"\nTotal files created: {len(all_files)}")
        print("\nDirectory structure:")
        for file in sorted(all_files):
            print(f"  {file.relative_to(base_dir)}")

    except Exception as e:
        print(f"\n❌ Error creating test structure: {e}")
        raise

if __name__ == "__main__":
    create_test_structure()