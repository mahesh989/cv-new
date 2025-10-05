"""
Unified Latest File Selector (App Module)
Selects appropriate CV based on JD usage history.
Uses original CV for first-time JD usage, tailored CV for subsequent uses.
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
    Unified file selector that picks CV based on JD usage history.
    Uses original CV for first-time JD usage, tailored CV for subsequent uses.
    """

    def __init__(self, user_email: Optional[str] = None):
        """
        Initialize file selector with user-specific paths
        
        Args:
            user_email: User's email address. Required for actual operations.
        """
        self.user_email = user_email.strip().lower() if user_email else None
        
        if user_email:
            from app.utils.user_path_utils import get_user_base_path
            self.base_path = get_user_base_path(self.user_email)
            self.cvs_path = self.base_path / "cvs"
            self.tailored_path = self.cvs_path / "tailored"
            self.original_path = self.cvs_path / "original"
        else:
            # For global instance - paths will be set when user_email is provided
            self.base_path = None
            self.cvs_path = None
            self.tailored_path = None
            self.original_path = None
        
        # Ensure paths exist (only if user_email is provided)
        if self.user_email:
            from app.utils.user_path_utils import ensure_user_directories
            ensure_user_directories(self.user_email)

    def get_latest_cv_for_company(self, company: str, jd_url: str = "", jd_text: str = "") -> FileContext:
        """
        Get the latest CV file for a company by timestamp, regardless of type.
        Always selects the most recent CV file (original or tailored) based on timestamp.
        
        Args:
            company: Company name
            jd_url: Job description URL (optional) - used for company uniqueness if provided
            jd_text: Job description text (optional)
        """
        if not self.user_email:
            raise ValueError("user_email must be provided for file selection operations")
        
        # Use JD URL for company uniqueness if provided, otherwise use company name
        effective_company = self._get_effective_company_name(company, jd_url)
        print(f"🔍 Searching for latest CV for company: {company} (effective: {effective_company})")
        
        # Always get the latest CV across all types (original and tailored)
        print("📄 Selecting latest CV by timestamp (original or tailored)")
        return self.get_latest_cv_across_all(effective_company)
    
    def _get_original_cv_for_company(self, company: str) -> FileContext:
        """Get original CV for a company"""
        print(f"🔍 Searching for original CV for company: {company}")
        
        candidates = self._find_original_cv_files(company)
        print(f"📁 Found {len(candidates)} original CV candidates")
        
        if not candidates:
            print("❌ No original CV candidates found")
            raise FileNotFoundError(f"No original CV found for company: {company}")
        
        # Select the latest original CV
        candidates.sort(key=lambda c: c[2], reverse=True)
        json_path, txt_path, timestamp = candidates[0]
        
        print(f"✅ Selected original CV: {json_path}")
        return FileContext(
            json_path=json_path,
            txt_path=txt_path,
            exists=True,
            file_type="original",
            timestamp=timestamp if timestamp != "00000000_000000" else None,
            company=company,
        )
    
    def _get_tailored_cv_for_company(self, company: str) -> FileContext:
        """Get tailored CV for a company"""
        print(f"🔍 Searching for tailored CV for company: {company}")
        
        candidates = self._find_tailored_cv_files(company)
        print(f"📁 Found {len(candidates)} tailored CV candidates")
        
        if not candidates:
            print("❌ No tailored CV candidates found")
            raise FileNotFoundError(f"No tailored CV found for company: {company}")
        
        latest_cv = self._select_best_cv_candidate(candidates, company)
        print(f"✅ Selected tailored CV: {latest_cv.file_type} - {latest_cv.json_path}")
        return latest_cv

    def get_latest_cv_across_all(self, company: str) -> FileContext:
        """
        Get the latest CV across tailored and original folders by timestamp.
        If both exist, whichever has the newest timestamp wins.
        Base files without timestamp are treated as oldest.
        """
        if not self.user_email:
            raise ValueError("user_email must be provided for file selection operations")
            
        print(f"🔍 Searching for latest CV across tailored+original for company: {company}")
        candidates: List[Tuple[Path, Optional[Path], str, str]] = []  # (json, txt, ts, type)

        # Tailored candidates (per-user cvs/tailored folder)
        for json_path, txt_path, ts in self._find_tailored_cv_files(company):
            candidates.append((json_path, txt_path, ts or "00000000_000000", "tailored"))

        # Original candidates (timestamped and base)
        for json_path, txt_path, ts in self._find_original_cv_files(company):
            candidates.append((json_path, txt_path, ts or "00000000_000000", "original"))

        if not candidates:
            raise FileNotFoundError(f"No CV found in tailored or original folders for company: {company}")

        # Sort by (timestamp desc, mtime desc) to always pick the freshest file
        def _candidate_key(c):
            json_path, _txt_path, ts, _ftype = c
            try:
                mtime = json_path.stat().st_mtime if json_path and json_path.exists() else 0
            except Exception:
                mtime = 0
            return (ts, mtime)
        candidates.sort(key=_candidate_key, reverse=True)
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
        if not self.user_email:
            raise ValueError("user_email must be provided for file selection operations")
            
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
        pattern = f"{company}_tailored_cv_*.json"

        # 1) Look in per-user global tailored folder: cv-analysis/cvs/tailored
        if self.tailored_path.exists():
            for json_file in self.tailored_path.glob(pattern):
                timestamp = self._extract_timestamp_from_filename(json_file.name) or "00000000_000000"
                txt_file = json_file.with_suffix('.txt')
                if not txt_file.exists():
                    txt_file = None
                candidates.append((json_file, txt_file, timestamp))

        # 2) Look in company-specific tailored folder: cv-analysis/applied_companies/<company>/cvs/tailored
        company_tailored = self.base_path / "applied_companies" / company / "cvs" / "tailored"
        if company_tailored.exists():
            for json_file in company_tailored.glob(pattern):
                timestamp = self._extract_timestamp_from_filename(json_file.name) or "00000000_000000"
                txt_file = json_file.with_suffix('.txt')
                if not txt_file.exists():
                    txt_file = None
                candidates.append((json_file, txt_file, timestamp))

        return candidates

    def _find_original_cv_files(self, company: str = "") -> List[Tuple[Path, Optional[Path], str]]:
        """Find original CV files (timestamped and base)."""
        candidates: List[Tuple[Path, Optional[Path], str]] = []
        
        # First try company-specific original CV folder
        if company:
            company_original_path = self.base_path / "applied_companies" / company / "cvs" / "original"
            if company_original_path.exists():
                # Timestamped originals
                for json_file in company_original_path.glob("original_cv_*.json"):
                    ts = self._extract_timestamp_from_filename(json_file.name)
                    txt_file = json_file.with_suffix('.txt')
                    if not txt_file.exists():
                        txt_file = None
                    if ts:
                        candidates.append((json_file, txt_file, ts))
                # Base files as oldest
                base_json = company_original_path / "original_cv.json"
                if base_json.exists():
                    base_txt = company_original_path / "original_cv.txt"
                    candidates.append((base_json, base_txt if base_txt.exists() else None, "00000000_000000"))
        
        # Fallback to global original CV folder
        if not candidates and self.original_path.exists():
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
        # Sort by (timestamp desc, mtime desc)
        def _cv_key(c):
            json_path, _txt_path, ts = c
            try:
                mtime = json_path.stat().st_mtime if json_path and json_path.exists() else 0
            except Exception:
                mtime = 0
            return (ts, mtime)
        candidates.sort(key=_cv_key, reverse=True)
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
        # Sort by (timestamp desc, mtime desc)
        def _analysis_key(x):
            file_path, ts = x
            try:
                mtime = file_path.stat().st_mtime if file_path and file_path.exists() else 0
            except Exception:
                mtime = 0
            return (ts, mtime)
        candidates.sort(key=_analysis_key, reverse=True)
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
    
    def _get_effective_company_name(self, company: str, jd_url: str = "") -> str:
        """
        Get the effective company name for file operations.
        Uses JD URL for uniqueness if provided, otherwise uses company name.
        
        Args:
            company: Company name
            jd_url: Job description URL (optional)
            
        Returns:
            Effective company name for file operations
        """
        if jd_url and jd_url.strip():
            # Use JD URL for company uniqueness
            # Extract domain or use full URL as company identifier
            try:
                from urllib.parse import urlparse
                parsed_url = urlparse(jd_url)
                if parsed_url.netloc:
                    # Use domain as company identifier
                    domain = parsed_url.netloc.replace('www.', '')
                    effective_company = f"{company}_for_{domain}"
                else:
                    # Fallback to full URL hash for uniqueness
                    import hashlib
                    url_hash = hashlib.md5(jd_url.encode()).hexdigest()[:8]
                    effective_company = f"{company}_for_{url_hash}"
            except Exception as e:
                print(f"⚠️ Error parsing JD URL {jd_url}: {e}, using company name")
                effective_company = company
        else:
            effective_company = company
            
        return effective_company


# DEPRECATED: Global singleton instance - DO NOT USE
# This instance has no user context and will fail for actual operations
# Always use get_selector_for_user(user_email) instead
unified_selector = UnifiedLatestFileSelector()

def get_selector_for_user(user_email: str) -> UnifiedLatestFileSelector:
    """
    Get a file selector instance for a specific user
    
    Args:
        user_email: User's email address
        
    Returns:
        UnifiedLatestFileSelector instance scoped to the user
    """
    return UnifiedLatestFileSelector(user_email=user_email)


# Backward-compatible helpers - these now require user_email
def get_latest_cv_content_for_analysis(company: str, user_email: str) -> str:
    selector = get_selector_for_user(user_email)
    return selector.get_cv_content_for_analysis(company)

def get_latest_cv_paths_for_services(company: str, user_email: str) -> Dict[str, str]:
    selector = get_selector_for_user(user_email)
    return selector.get_latest_cv_paths_for_services(company)

def get_cv_for_analysis(company: str, user_email: str, is_rerun: bool = False) -> FileContext:
    selector = get_selector_for_user(user_email)
    return selector.get_latest_cv_for_company(company)


