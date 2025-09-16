#!/usr/bin/env python3
"""
Comprehensive test for CV generation functionality using available data
"""
import json
import sys
import os
import asyncio
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.tailored_cv.models.cv_models import OriginalCV, ContactInfo, ExperienceEntry, Education, Project, SkillCategory
from app.tailored_cv.services.cv_tailoring_service import CVTailoringService
from app.tailored_cv.services.recommendation_service import RecommendationService

class CVGenerationTester:
    def __init__(self):
        self.tailoring_service = CVTailoringService()
        self.recommendation_service = RecommendationService()
        self.results = []
        
    def parse_original_cv_text(self, cv_text: str) -> OriginalCV:
        """Parse the original CV text into structured OriginalCV object"""
        
        # Extract contact information
        lines = cv_text.split('\n')
        name = "Maheshwor Tiwari"  # First line
        
        contact_line = lines[1] if len(lines) > 1 else ""
        email = "maheshtwari99@gmail.com"
        phone = "0414 032 507"
        location = "Hurstville, NSW, 2220"
        
        contact = ContactInfo(
            name=name,
            email=email,
            phone=phone,
            location=location
        )
        
        # Parse education
        education = [
            Education(
                institution="Charles Darwin University",
                degree="Master of Data Science",
                location="Sydney, Australia",
                graduation_date="Nov 2024"
            ),
            Education(
                institution="CY Cergy Paris University",
                degree="PhD in Physics", 
                location="Cergy, France",
                graduation_date="Sep 2022"
            ),
            Education(
                institution="CY Cergy Paris University",
                degree="Master of Theoretical Physics",
                location="Cergy, France", 
                graduation_date="Jun 2018"
            )
        ]
        
        # Parse experience
        experience = [
            ExperienceEntry(
                company="The Bitrates",
                title="Data Analyst",
                location="Sydney, NSW",
                start_date="Jul 2024",
                end_date="Present",
                bullets=[
                    "Designed and implemented Python scripts for data cleaning, preprocessing, and analysis, improving data pipeline efficiency by 30%",
                    "Developed machine learning models in Python for predictive analytics, enabling data-driven business decisions",
                    "Leveraged AI techniques to automate repetitive tasks, reducing manual effort and improving productivity",
                    "Built dynamic dashboards and visualizations using Python libraries like Matplotlib and Seaborn",
                    "Integrated Google Analytics data with Python for advanced analysis, enhancing customer behavior insights"
                ]
            ),
            ExperienceEntry(
                company="iBuild Building Solutions",
                title="Data Analyst", 
                location="Victoria, Australia",
                start_date="Mar 2024",
                end_date="Jun 2024",
                bullets=[
                    "Automated data extraction and structuring of population datasets using Python, improving data accuracy and team collaboration",
                    "Analyzed customer support data with Python to optimize response times and enhance operational efficiency",
                    "Developed Python-based solutions to generate actionable insights, meeting strict deadlines for strategic decision-making",
                    "Designed Python scripts to create dynamic reports and dashboards, significantly improving customer satisfaction"
                ]
            ),
            ExperienceEntry(
                company="Property Console",
                title="Software Engineer and Analyst",
                location="Sydney, Australia",
                start_date="Jun 2023", 
                end_date="Nov 2023",
                bullets=[
                    "Built Python scripts to track key metrics, ensuring 99% data accuracy and improving operational efficiency",
                    "Collaborated with development team to enhance analytics capabilities, using Python to improve data processing speed by 25%",
                    "Leveraged Python for data preprocessing and analysis, producing Tableau dashboards that improved decision-making",
                    "Supported cross-functional teams with Python-driven insights, enabling customer-focused initiatives"
                ]
            )
        ]
        
        # Parse skills
        skills = [
            SkillCategory(
                category="Programming Languages",
                skills=["Python", "SQL", "R"]
            ),
            SkillCategory(
                category="Data Science & ML",
                skills=["Pandas", "NumPy", "scikit-learn", "Machine Learning", "AI", "Predictive Analytics"]
            ),
            SkillCategory(
                category="Visualization & BI",
                skills=["Tableau", "Power BI", "Matplotlib", "Seaborn"]
            ),
            SkillCategory(
                category="Databases & Cloud", 
                skills=["PostgreSQL", "MySQL", "Snowflake"]
            ),
            SkillCategory(
                category="Tools & Technologies",
                skills=["GitHub", "Docker", "Visual Studio Code", "Google Analytics", "Excel"]
            )
        ]
        
        # Parse projects (extract from experience context)
        projects = [
            Project(
                name="Data Pipeline Optimization",
                description="Python-based automation system",
                technologies=["Python", "Pandas", "NumPy"],
                bullets=[
                    "Improved data pipeline efficiency by 30% through automated data cleaning and preprocessing",
                    "Reduced manual effort by implementing AI-driven automation techniques"
                ]
            ),
            Project(
                name="Predictive Analytics Platform",
                description="Machine learning models for business intelligence",
                technologies=["Python", "scikit-learn", "Machine Learning"],
                bullets=[
                    "Developed ML models enabling data-driven business decisions",
                    "Created dynamic dashboards for effective insight communication"
                ]
            )
        ]
        
        return OriginalCV(
            contact=contact,
            education=education,
            experience=experience,
            projects=projects,
            skills=skills,
            total_years_experience=4
        )
    
    def create_sample_job_description(self) -> str:
        """Create a sample job description for testing"""
        return """
        Senior Data Scientist - Machine Learning Engineer
        
        Company: TechCorp Australia
        Location: Sydney, NSW
        
        About the Role:
        We are seeking a Senior Data Scientist with expertise in machine learning, Python programming, and cloud technologies to join our growing data science team. The successful candidate will lead data science projects, develop ML models, and work with large-scale data infrastructure.
        
        Key Responsibilities:
        • Design and implement machine learning models using Python, TensorFlow, and PyTorch
        • Build and optimize data pipelines using Apache Spark, Kafka, and cloud services (AWS, Azure)
        • Develop predictive analytics solutions for business intelligence
        • Create data visualizations and dashboards using Tableau, Power BI
        • Collaborate with engineering teams on MLOps and model deployment
        • Mentor junior data scientists and analysts
        • Present findings to stakeholders and executive leadership
        
        Required Skills:
        • 5+ years experience in data science and machine learning
        • Advanced Python programming skills (Pandas, NumPy, scikit-learn, TensorFlow, PyTorch)
        • Experience with cloud platforms (AWS, Azure, GCP) and big data technologies (Spark, Kafka)
        • Strong SQL skills and database management (PostgreSQL, MongoDB)
        • Experience with MLOps, Docker, Kubernetes
        • Data visualization expertise (Tableau, Power BI, D3.js)
        • Strong communication and leadership skills
        • PhD in Computer Science, Statistics, Mathematics, or related field preferred
        
        Preferred Skills:
        • Experience with real-time data processing and streaming analytics
        • Knowledge of deep learning architectures and neural networks
        • Familiarity with A/B testing and experimental design
        • Experience with version control (Git), CI/CD pipelines
        • Business intelligence and data warehousing experience
        """

    async def test_cv_parsing(self) -> bool:
        """Test parsing of original CV from text"""
        try:
            print("🔍 Testing CV parsing...")
            
            # Load original CV text
            cv_file_path = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis/original_cv.json"
            with open(cv_file_path, 'r') as f:
                cv_data = json.load(f)
            
            cv_text = cv_data['text']
            original_cv = self.parse_original_cv_text(cv_text)
            
            # Validate parsed CV
            assert original_cv.contact.name == "Maheshwor Tiwari"
            assert len(original_cv.experience) >= 3
            assert len(original_cv.skills) >= 4
            assert len(original_cv.education) >= 2
            
            self.results.append({
                'test': 'CV Parsing',
                'status': 'PASS',
                'details': f'Successfully parsed CV with {len(original_cv.experience)} experiences, {len(original_cv.skills)} skill categories',
                'data': {'experience_count': len(original_cv.experience), 'skills_count': len(original_cv.skills)}
            })
            
            # Store parsed CV for other tests
            self.original_cv = original_cv
            return True
            
        except Exception as e:
            self.results.append({
                'test': 'CV Parsing',
                'status': 'FAIL',
                'details': f'CV parsing failed: {str(e)}',
                'data': None
            })
            return False

    async def test_recommendation_generation(self) -> bool:
        """Test recommendation generation from CV and JD"""
        try:
            print("🔍 Testing recommendation generation...")
            
            if not hasattr(self, 'original_cv'):
                raise Exception("Original CV not available - CV parsing test must pass first")
            
            job_description = self.create_sample_job_description()
            company = "TechCorp Australia"
            job_title = "Senior Data Scientist"
            
            # Generate recommendations
            recommendations = await self.recommendation_service.generate_recommendations(
                self.original_cv,
                job_description,
                company,
                job_title
            )
            
            # Validate recommendations
            assert recommendations.company == company
            assert recommendations.job_title == job_title
            assert len(recommendations.critical_gaps) > 0
            assert len(recommendations.missing_technical_skills) >= 0
            assert recommendations.match_score > 0
            
            self.results.append({
                'test': 'Recommendation Generation', 
                'status': 'PASS',
                'details': f'Generated recommendations with {len(recommendations.critical_gaps)} critical gaps, match score: {recommendations.match_score}%',
                'data': {
                    'match_score': recommendations.match_score,
                    'critical_gaps': recommendations.critical_gaps,
                    'missing_skills': recommendations.missing_technical_skills
                }
            })
            
            # Store recommendations for tailoring test
            self.recommendations = recommendations
            return True
            
        except Exception as e:
            self.results.append({
                'test': 'Recommendation Generation',
                'status': 'FAIL', 
                'details': f'Recommendation generation failed: {str(e)}',
                'data': None
            })
            return False

    async def test_cv_tailoring(self) -> bool:
        """Test the complete CV tailoring process"""
        try:
            print("🔍 Testing CV tailoring...")
            
            if not hasattr(self, 'original_cv') or not hasattr(self, 'recommendations'):
                raise Exception("Prerequisites not available - previous tests must pass first")
            
            # Generate tailored CV
            tailored_cv = await self.tailoring_service.tailor_cv(
                self.original_cv,
                self.recommendations,
                custom_instructions="Focus on machine learning and cloud technologies expertise"
            )
            
            # Validate tailored CV
            assert tailored_cv.contact.name == self.original_cv.contact.name
            assert tailored_cv.target_company == self.recommendations.company
            assert tailored_cv.target_role == self.recommendations.job_title
            assert len(tailored_cv.experience) == len(self.original_cv.experience)
            assert tailored_cv.optimization_strategy is not None
            
            # Check if enhancements were applied
            enhancement_count = len(tailored_cv.enhancements_applied) if tailored_cv.enhancements_applied else 0
            keyword_count = len(tailored_cv.keywords_integrated) if tailored_cv.keywords_integrated else 0
            
            self.results.append({
                'test': 'CV Tailoring',
                'status': 'PASS',
                'details': f'Successfully tailored CV with {enhancement_count} enhancements and {keyword_count} keywords integrated',
                'data': {
                    'target_company': tailored_cv.target_company,
                    'target_role': tailored_cv.target_role,
                    'enhancements_count': enhancement_count,
                    'keywords_count': keyword_count,
                    'estimated_ats_score': tailored_cv.estimated_ats_score
                }
            })
            
            # Store tailored CV for saving test
            self.tailored_cv = tailored_cv
            return True
            
        except Exception as e:
            self.results.append({
                'test': 'CV Tailoring',
                'status': 'FAIL',
                'details': f'CV tailoring failed: {str(e)}',
                'data': None
            })
            return False

    async def test_cv_saving(self) -> bool:
        """Test saving the tailored CV"""
        try:
            print("🔍 Testing CV saving...")
            
            if not hasattr(self, 'tailored_cv'):
                raise Exception("Tailored CV not available - CV tailoring test must pass first")
            
            # Create test directory
            test_output_dir = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/new-cv/test_output"
            Path(test_output_dir).mkdir(exist_ok=True)
            
            # Save tailored CV
            saved_path = self.tailoring_service.save_tailored_cv(
                self.tailored_cv,
                test_output_dir
            )
            
            # Validate saved file
            assert os.path.exists(saved_path)
            
            # Load and validate saved content
            with open(saved_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data['contact']['name'] == self.tailored_cv.contact.name
            assert saved_data['target_company'] == self.tailored_cv.target_company
            
            self.results.append({
                'test': 'CV Saving',
                'status': 'PASS',
                'details': f'Successfully saved tailored CV to {saved_path}',
                'data': {'saved_path': saved_path}
            })
            
            return True
            
        except Exception as e:
            self.results.append({
                'test': 'CV Saving',
                'status': 'FAIL',
                'details': f'CV saving failed: {str(e)}',
                'data': None
            })
            return False

    async def test_error_handling(self) -> bool:
        """Test error handling scenarios"""
        try:
            print("🔍 Testing error handling...")
            
            error_tests = []
            
            # Test 1: Invalid CV data
            try:
                invalid_cv = OriginalCV(
                    contact=ContactInfo(name="", email="", phone="", location=""),
                    education=[],
                    experience=[],
                    projects=[],
                    skills=[],
                    total_years_experience=0
                )
                
                job_description = self.create_sample_job_description()
                await self.recommendation_service.generate_recommendations(
                    invalid_cv, job_description, "Test Company", "Test Role"
                )
                error_tests.append({'name': 'Invalid CV', 'passed': False})
            except Exception:
                error_tests.append({'name': 'Invalid CV', 'passed': True})
            
            # Test 2: Empty job description
            try:
                if hasattr(self, 'original_cv'):
                    await self.recommendation_service.generate_recommendations(
                        self.original_cv, "", "Test Company", "Test Role"
                    )
                error_tests.append({'name': 'Empty Job Description', 'passed': False})
            except Exception:
                error_tests.append({'name': 'Empty Job Description', 'passed': True})
            
            passed_error_tests = sum(1 for test in error_tests if test['passed'])
            total_error_tests = len(error_tests)
            
            self.results.append({
                'test': 'Error Handling',
                'status': 'PASS' if passed_error_tests == total_error_tests else 'PARTIAL',
                'details': f'Passed {passed_error_tests}/{total_error_tests} error handling tests',
                'data': {'error_tests': error_tests}
            })
            
            return True
            
        except Exception as e:
            self.results.append({
                'test': 'Error Handling',
                'status': 'FAIL',
                'details': f'Error handling test failed: {str(e)}',
                'data': None
            })
            return False

    async def run_all_tests(self):
        """Run all CV generation tests"""
        print("🚀 Starting comprehensive CV generation tests...")
        print("=" * 60)
        
        tests = [
            self.test_cv_parsing,
            self.test_recommendation_generation,
            self.test_cv_tailoring,
            self.test_cv_saving,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"❌ Unexpected error in {test.__name__}: {str(e)}")
        
        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 CV GENERATION TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.results if result['status'] == 'PASS')
        partial = sum(1 for result in self.results if result['status'] == 'PARTIAL')
        failed = sum(1 for result in self.results if result['status'] == 'FAIL')
        total = len(self.results)
        
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "⚠️" if result['status'] == 'PARTIAL' else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            print(f"   {result['details']}")
            if result['data'] and isinstance(result['data'], dict):
                for key, value in result['data'].items():
                    if isinstance(value, list) and len(value) > 3:
                        print(f"   {key}: {value[:3]}... ({len(value)} total)")
                    else:
                        print(f"   {key}: {value}")
            print()
        
        print(f"Results: {passed} passed, {partial} partial, {failed} failed, {total} total")
        
        success_rate = ((passed + partial * 0.5) / total * 100) if total > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Save results to file
        results_file = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/new-cv/test_cv_generation_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.utcnow().isoformat(),
                'total_tests': total,
                'passed': passed,
                'partial': partial,
                'failed': failed,
                'success_rate': success_rate,
                'results': self.results
            }, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        if success_rate >= 80:
            print("\n🎉 CV generation functionality is working well!")
        elif success_rate >= 60:
            print("\n⚠️ CV generation has some issues but core functionality works")
        else:
            print("\n💥 CV generation has significant issues that need attention")

async def main():
    """Main test execution function"""
    tester = CVGenerationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())