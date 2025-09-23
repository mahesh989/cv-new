"""
Unified Latest File Selector (App Module)
Only selects latest tailored CV for a company.
Raises error if no tailored CV exists. No fallback to original.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class FileContext:
    json_path: Optional[Path] = None
    txt_path: Optional[Path] = None
    exists: bool = False
    file_type: str = ""  # "tailored", "analysis"
    timestamp: Optional[str] = None
    company: str = ""


class UnifiedLatestFileSelector:
    """
    Single unified file selector that always picks the latest available tailored CV.
    Eliminates fresh/rerun logic; if no tailored exists, raises FileNotFoundError.
    """

    def __init__(self, base_path: str = "/Users/mahesh/Documents/Github/cv-new/cv-magic-app/backend/cv-analysis"):
        self.base_path = Path(base_path)
        self.cvs_path = self.base_path / "cvs"
        self.tailored_path = self.cvs_path / "tailored"
        self.original_path = self.cvs_path / "original"

    def get_latest_cv_for_company(self, company: str) -> FileContext:
        """
        Get the absolute latest CV file for a company (tailored only).
        Pattern: {company}_tailored_cv_{YYYYMMDD_HHMMSS}.json
        """
        print(f"🔍 Searching for latest CV for company: {company}")

        candidates = self._find_tailored_cv_files(company)
        print(f"📁 Found {len(candidates)} tailored CV candidates")

        if not candidates:
            print("❌ No tailored CV candidates found")
            raise FileNotFoundError(f"No tailored CV found for company: {company}")

        latest_cv = self._select_best_cv_candidate(candidates, company)
        print(f"✅ Selected latest CV: {latest_cv.file_type} - {latest_cv.json_path}")
        return latest_cv

    def get_latest_cv_across_all(self, company: str) -> FileContext:
        """
        Get the latest CV across tailored and original folders by timestamp.
        If both exist, whichever has the newest timestamp wins.
        Base files without timestamp are treated as oldest.
        """
        print(f"🔍 Searching for latest CV across tailored+original for company: {company}")
        candidates: List[Tuple[Path, Optional[Path], str, str]] = []  # (json, txt, ts, type)

        # Tailored candidates
        for json_path, txt_path, ts in self._find_tailored_cv_files(company):
            candidates.append((json_path, txt_path, ts or "00000000_000000", "tailored"))

        # Original candidates (timestamped and base)
        for json_path, txt_path, ts in self._find_original_cv_files():
            candidates.append((json_path, txt_path, ts or "00000000_000000", "original"))

        if not candidates:
            raise FileNotFoundError(f"No CV found in tailored or original folders for company: {company}")

        # Sort by timestamp desc
        candidates.sort(key=lambda c: c[2], reverse=True)
        json_path, txt_path, ts, ftype = candidates[0]
        print(f"📄 [UNIFIED] Latest CV resolved → type={ftype}, ts={ts}, json={json_path}, txt={txt_path}")
        return FileContext(
            json_path=json_path,
            txt_path=txt_path,
            exists=True,
            file_type=ftype,
            timestamp=None if ts == "00000000_000000" else ts,
            company=company,
        )

    def get_latest_analysis_file(self, company: str, analysis_type: str) -> FileContext:
        """
        Get the latest analysis file for a company
        analysis_type: "skills_analysis", "cv_jd_match_results", "job_info"
        """
        print(f"🔍 Searching for latest {analysis_type} for company: {company}")

        search_locations = [
            self.base_path / company,
            self.base_path,
        ]

        all_candidates: List[Tuple[Path, str]] = []
        for location in search_locations:
            if location.exists():
                all_candidates.extend(self._find_analysis_files(location, company, analysis_type))

        if not all_candidates:
            print(f"❌ No {analysis_type} files found for {company}")
            return FileContext(exists=False, company=company)

        latest_analysis = self._select_best_analysis_candidate(all_candidates, company, analysis_type)
        print(f"✅ Selected latest {analysis_type}: {latest_analysis.json_path}")
        return latest_analysis

    def get_cv_content_for_analysis(self, company: str) -> str:
        cv_context = self.get_latest_cv_for_company(company)
        for file_path in [cv_context.txt_path, cv_context.json_path]:
            if file_path and file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            return content
                except Exception as e:
                    print(f"⚠️ Error reading {file_path}: {e}")
                    continue
        raise FileNotFoundError(f"No readable tailored CV content found for company: {company}")

    def get_cv_content_across_all(self, company: str) -> str:
        """Get CV content from the latest CV across tailored and original."""
        cv_context = self.get_latest_cv_across_all(company)
        print(f"📄 [UNIFIED] Reading CV content from: txt={cv_context.txt_path}, json={cv_context.json_path}")
        for file_path in [cv_context.txt_path, cv_context.json_path]:
            if file_path and file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        preview = content[:400].replace('\n', ' ') if content else ''
                        print(f"🧪 [UNIFIED] CV content length={len(content) if content else 0}, preview='{preview}'")
                        if content.strip():
                            return content
                except Exception as e:
                    print(f"⚠️ Error reading {file_path}: {e}")
                    continue
        raise FileNotFoundError(f"No readable CV content found (tailored/original) for company: {company}")

    def get_latest_cv_paths_for_services(self, company: str = "") -> Dict[str, str]:
        cv_context = self.get_latest_cv_for_company(company)
        return {
            'json_path': str(cv_context.json_path) if cv_context.json_path else "",
            'txt_path': str(cv_context.txt_path) if cv_context.txt_path else "",
            'file_type': cv_context.file_type,
            'timestamp': cv_context.timestamp or "",
        }

    def _find_tailored_cv_files(self, company: str) -> List[Tuple[Path, Optional[Path], str]]:
        candidates: List[Tuple[Path, Optional[Path], str]] = []
        if not self.tailored_path.exists():
            return candidates
        pattern = f"{company}_tailored_cv_*.json"
        for json_file in self.tailored_path.glob(pattern):
            timestamp = self._extract_timestamp_from_filename(json_file.name) or "00000000_000000"
            txt_file = json_file.with_suffix('.txt')
            if not txt_file.exists():
                txt_file = None
            candidates.append((json_file, txt_file, timestamp))
        return candidates

    def _find_original_cv_files(self) -> List[Tuple[Path, Optional[Path], str]]:
        """Find original CV files (timestamped and base)."""
        candidates: List[Tuple[Path, Optional[Path], str]] = []
        if not self.original_path.exists():
            return candidates
        # Timestamped originals
        for json_file in self.original_path.glob("original_cv_*.json"):
            ts = self._extract_timestamp_from_filename(json_file.name)
            txt_file = json_file.with_suffix('.txt')
            if not txt_file.exists():
                txt_file = None
            if ts:
                candidates.append((json_file, txt_file, ts))
        # Base files as oldest
        base_json = self.original_path / "original_cv.json"
        if base_json.exists():
            base_txt = self.original_path / "original_cv.txt"
            candidates.append((base_json, base_txt if base_txt.exists() else None, "00000000_000000"))
        return candidates

    def _find_analysis_files(self, directory: Path, company: str, analysis_type: str) -> List[Tuple[Path, str]]:
        candidates: List[Tuple[Path, str]] = []
        patterns = [
            f"{company}_{analysis_type}_*.json",
            f"{analysis_type}_*.json",
            f"{company}_{analysis_type}.json",
            f"{analysis_type}.json",
        ]
        for pattern in patterns:
            for file_path in directory.glob(pattern):
                timestamp = self._extract_timestamp_from_filename(file_path.name) or "00000000_000000"
                candidates.append((file_path, timestamp))
        return candidates

    def _select_best_cv_candidate(self, candidates: List[Tuple[Path, Optional[Path], str]], company: str) -> FileContext:
        if not candidates:
            return FileContext(exists=False, company=company)
        candidates.sort(key=lambda c: c[2], reverse=True)
        json_path, txt_path, timestamp = candidates[0]
        return FileContext(
            json_path=json_path,
            txt_path=txt_path,
            exists=True,
            file_type="tailored",
            timestamp=timestamp if timestamp != "00000000_000000" else None,
            company=company,
        )

    def _select_best_analysis_candidate(self, candidates: List[Tuple[Path, str]], company: str, analysis_type: str) -> FileContext:
        candidates.sort(key=lambda x: x[1], reverse=True)
        file_path, timestamp = candidates[0]
        return FileContext(
            json_path=file_path,
            exists=True,
            file_type="analysis",
            timestamp=timestamp if timestamp != "00000000_000000" else None,
            company=company,
        )

    def _extract_timestamp_from_filename(self, filename: str) -> Optional[str]:
        match = re.search(r'(\d{8}_\d{6})', filename)
        return match.group(1) if match else None

    def get_timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")


# Global singleton instance
unified_selector = UnifiedLatestFileSelector()


# Backward-compatible helpers
def get_latest_cv_content_for_analysis(company: str = "") -> str:
    return unified_selector.get_cv_content_for_analysis(company)

def get_latest_cv_paths_for_services(company: str = "") -> Dict[str, str]:
    return unified_selector.get_latest_cv_paths_for_services(company)

def get_cv_for_analysis(company: str, is_rerun: bool = False) -> FileContext:
    return unified_selector.get_latest_cv_for_company(company)


