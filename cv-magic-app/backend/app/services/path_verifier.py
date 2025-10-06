"""Path Verification Service

This service handles verification of file paths during analysis to ensure correct structure.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PathVerifier:
    def __init__(self, debug: bool = True):
        self.debug = debug
        self._indent = 0

    def _log(self, message: str):
        if self.debug:
            indent = "  " * self._indent
            logger.info(f"{indent}{message}")

    def verify_analysis_paths(self, company: str, user_email: Optional[str] = None):
        """Verify all analysis-related paths for a company"""
        self._log(f"\n📌 Verifying paths for {company}")
        self._indent += 1

        # Get base paths
        from app.utils.user_path_utils import get_user_base_path, get_user_company_analysis_paths
        base_dir = get_user_base_path(user_email)
        company_paths = get_user_company_analysis_paths(user_email, company)

        # 1. Verify base structure
        self._log("\n🔍 Checking base structure:")
        required_dirs = [
            base_dir / "applied_companies" / company,
            base_dir / "cvs" / "original",
            base_dir / "cvs" / "tailored",
            base_dir / "saved_jobs",
            base_dir / "uploads"
        ]

        for dir_path in required_dirs:
            if dir_path.exists() and dir_path.is_dir():
                self._log(f"✅ Directory exists: {dir_path}")
            else:
                self._log(f"❌ Missing directory: {dir_path}")

        # 2. Check company-specific files
        self._log("\n🔍 Checking company files:")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Expected file paths for this timestamp
        expected_files = {
            "JD Original": company_paths["jd_original"](timestamp),
            "Job Info": company_paths["job_info"](timestamp),
            "JD Analysis": company_paths["jd_analysis"](timestamp),
            "CV-JD Matching": company_paths["cv_jd_matching"](timestamp),
            "Component Analysis": company_paths["component_analysis"](timestamp),
            "Skills Analysis": company_paths["skills_analysis"](timestamp),
            "Input Recommendation": company_paths["input_recommendation"](timestamp),
            "AI Recommendation": company_paths["ai_recommendation"](timestamp),
            "Tailored CV": company_paths["tailored_cv"](timestamp)
        }

        for name, path in expected_files.items():
            # Verify path format
            if str(path).startswith(str(base_dir)):
                self._log(f"✅ Valid path for {name}: {path}")
            else:
                self._log(f"❌ Invalid path for {name}: {path}")
                self._log(f"   Should start with: {base_dir}")

            # Check if similar files exist (any timestamp)
            parent = path.parent
            if parent.exists():
                similar_files = list(parent.glob(path.stem.split("_20")[0] + "_*.json"))
                if similar_files:
                    self._log(f"  📄 Found {len(similar_files)} existing file(s):")
                    for f in similar_files:
                        self._log(f"    - {f.name}")
                else:
                    self._log(f"  ⚠️  No existing files found in {parent}")
            else:
                self._log(f"  ⚠️  Directory doesn't exist: {parent}")

        # 3. Verify non-timestamped files
        self._log("\n🔍 Checking static files:")
        static_files = [
            base_dir / "cvs/original/original_cv.json",
            base_dir / "cvs/original/original_cv.txt",
            base_dir / "saved_jobs/saved_jobs.json"
        ]

        for file_path in static_files:
            if file_path.exists():
                self._log(f"✅ File exists: {file_path}")
                if file_path.suffix == '.json':
                    try:
                        with open(file_path) as f:
                            json.load(f)  # Verify JSON is valid
                        self._log(f"  ✅ Valid JSON content")
                    except json.JSONDecodeError:
                        self._log(f"  ❌ Invalid JSON content")
                    except Exception as e:
                        self._log(f"  ❌ Error reading file: {e}")
            else:
                self._log(f"❌ Missing file: {file_path}")

        # 4. Print directory tree
        self._log("\n📁 Current structure:")
        self._print_tree(base_dir / "applied_companies" / company)
        self._print_tree(base_dir / "cvs")
        
        self._indent -= 1

    def verify_file_content(self, file_path: Path, required_fields: Optional[List[str]] = None):
        """Verify content of a specific file"""
        self._log(f"\n📌 Verifying content of {file_path.name}")
        self._indent += 1

        if not file_path.exists():
            self._log("❌ File does not exist")
            self._indent -= 1
            return False

        try:
            with open(file_path) as f:
                content = json.load(f)

            # Check required fields
            if required_fields:
                missing = [field for field in required_fields if field not in content]
                if missing:
                    self._log(f"❌ Missing required fields: {missing}")
                else:
                    self._log("✅ All required fields present")

            # Print content summary
            self._log("\n📄 Content summary:")
            self._print_dict_summary(content)

            self._indent -= 1
            return True

        except json.JSONDecodeError:
            self._log("❌ Invalid JSON content")
            self._indent -= 1
            return False
        except Exception as e:
            self._log(f"❌ Error reading file: {e}")
            self._indent -= 1
            return False

    def _print_dict_summary(self, data: Dict, prefix: str = ""):
        """Print a summary of dictionary content"""
        for key, value in data.items():
            if isinstance(value, dict):
                self._log(f"{prefix}{key}:")
                self._print_dict_summary(value, prefix + "  ")
            elif isinstance(value, list):
                self._log(f"{prefix}{key}: {len(value)} items")
            else:
                if isinstance(value, str) and len(value) > 50:
                    self._log(f"{prefix}{key}: {value[:50]}...")
                else:
                    self._log(f"{prefix}{key}: {value}")

    def _print_tree(self, path: Path, prefix: str = ""):
        """Print directory tree"""
        if not path.exists():
            return

        self._log(f"{prefix}📁 {path.name}/")
        prefix = prefix + "  "

        try:
            for item in sorted(path.iterdir()):
                if item.is_file():
                    self._log(f"{prefix}📄 {item.name}")
                else:
                    self._print_tree(item, prefix)
        except Exception as e:
            self._log(f"{prefix}❌ Error listing directory: {e}")

# Global instance
path_verifier = PathVerifier()