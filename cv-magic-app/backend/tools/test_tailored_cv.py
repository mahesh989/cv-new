import argparse
import json
import os
import sys
from pathlib import Path


def add_backend_to_sys_path(this_file: Path) -> Path:
    """Return backend root and ensure it's in sys.path."""
    backend_root = this_file.resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
    return backend_root


def adapt_tailored_cv_to_pdf_format(tailored_cv_data: dict) -> dict:
    """Simple adapter that converts tailored JSON into the PDF generator schema."""
    contact = tailored_cv_data.get("contact") or tailored_cv_data.get("personal_information") or {}

    pdf_data = {
        "personal_information": {
            "name": contact.get("name", "Candidate"),
            "location": contact.get("location", ""),
            "phone": contact.get("phone", ""),
            "email": contact.get("email", ""),
            "linkedin": contact.get("linkedin", ""),
            "github": contact.get("website", ""),
            "portfolio_links": {
                "blogs": contact.get("blogs", ""),
                "dashboard_portfolio": contact.get("portfolio", ""),
            },
        },
        "career_profile": tailored_cv_data.get("career_profile") or {},
        "experience": tailored_cv_data.get("experience", []),
        "education": tailored_cv_data.get("education", []),
        "skills": {"technical_skills": []},
        "projects": tailored_cv_data.get("projects", []),
        "certifications": tailored_cv_data.get("certifications", []),
    }

    skills_section = tailored_cv_data.get("skills")
    if isinstance(skills_section, dict):
        for category, skills in skills_section.items():
            if isinstance(skills, list):
                for s in skills:
                    pdf_data["skills"]["technical_skills"].append(f"{category}: {s}")
    elif isinstance(skills_section, list):
        pdf_data["skills"]["technical_skills"].extend(skills_section)

    # Normalize experience responsibilities key
    for exp in pdf_data["experience"]:
        if isinstance(exp, dict):
            if "responsibilities" not in exp:
                bullets = exp.get("bullets") or []
                exp["responsibilities"] = list(map(str, bullets))

            # Build duration if not present but start/end exist
            if not exp.get("duration"):
                start = (exp.get("start_date") or "").strip()
                end = (exp.get("end_date") or "").strip() or "Present"
                if start:
                    exp["duration"] = f"{start} – {end}"

    return pdf_data


def inspect_tailored_json(path: Path) -> None:
    print("\n📋 Tailored CV Structure:")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Keys in root: {list(data.keys())}")
    pi = data.get("personal_information") or data.get("contact") or {}
    if pi:
        print("\n👤 Personal Information:")
        print(f"  Name: {pi.get('name','N/A')}")
        print(f"  Email: {pi.get('email','N/A')}")
        print(f"  Location: {pi.get('location','N/A')}")
    cp = data.get("career_profile") or {}
    if cp:
        print("\n📝 Career Profile:")
        print(f"  Summary length: {len(cp.get('summary',''))}")
    exp = data.get("experience") or []
    print("\n💼 Experience:")
    print(f"  Number of jobs: {len(exp)}")
    for i, e in enumerate(exp[:3]):
        print(f"  Job {i+1}: {e.get('title','N/A')} at {e.get('company','N/A')}")
        print(f"    Duration: {e.get('duration','N/A')}")
        print(f"    Bullets/responsibilities: {len((e.get('responsibilities') or e.get('bullets') or []))}")
    edu = data.get("education") or []
    print("\n🎓 Education:")
    print(f"  Number of entries: {len(edu)}")
    skills = data.get("skills")
    print("\n🛠️ Skills:")
    if isinstance(skills, dict):
        print(f"  Categories: {list(skills.keys())}")
    elif isinstance(skills, list):
        print(f"  Flat list length: {len(skills)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Test tailored CV → PDF generation")
    parser.add_argument("--json", required=True, help="Path to tailored CV JSON file")
    parser.add_argument("--out", required=False, default=None, help="Output PDF path")
    args = parser.parse_args()

    this_file = Path(__file__)
    backend_root = add_backend_to_sys_path(this_file)

    json_path = Path(args.json)
    if not json_path.exists():
        print(f"❌ Tailored CV file not found: {json_path}")
        return 1

    print("🔍 Examining tailored CV structure...")
    print(f"📁 File size: {json_path.stat().st_size} bytes")
    inspect_tailored_json(json_path)

    with json_path.open("r", encoding="utf-8") as f:
        tailored = json.load(f)
    pdf_data = adapt_tailored_cv_to_pdf_format(tailored)
    print("\n✅ Adapted data successfully")
    print(f"  Experience entries: {len(pdf_data.get('experience', []))}")
    print(f"  Education entries: {len(pdf_data.get('education', []))}")
    print(f"  Skills: {len((pdf_data.get('skills') or {}).get('technical_skills', []))}")

    try:
        from app.tailored_cv.services.pdf_export_service import ResumePDFGenerator
    except Exception as e:
        print(f"❌ Could not import PDF generator: {e}")
        return 1

    out_path = Path(args.out) if args.out else backend_root / "test_output.pdf"
    generator = ResumePDFGenerator(pdf_data)
    generator.generate(str(out_path))
    if out_path.exists():
        print(f"\n🎉 SUCCESS: PDF created at {out_path}")
        print(f"📏 File size: {out_path.stat().st_size} bytes")
        return 0
    print("❌ ERROR: PDF file was not created")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


