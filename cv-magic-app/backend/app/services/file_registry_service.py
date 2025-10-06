import hashlib
from pathlib import Path
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.models.metadata import Company, CompanyFile, AnalysisRun, CVVersion


class FileRegistryService:
    def __init__(self, db: Session, user_id: str):
        self.db = db
        self.user_id = user_id

    @classmethod
    def from_email(cls, db: Session, user_email: str):
        from app.models.user import User
        user = db.query(User).filter(User.email == user_email).one_or_none()
        if not user:
            raise ValueError(f"User not found for email: {user_email}")
        # Store user_id as string to align with metadata tables
        return cls(db=db, user_id=str(user.id))

    def _sha256(self, file_path: Path) -> Optional[str]:
        try:
            h = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def upsert_company(self, company_name: str, display_name: Optional[str] = None, jd_url: Optional[str] = None) -> int:
        company = (
            self.db.query(Company)
            .filter(Company.user_id == self.user_id, Company.name == company_name)
            .one_or_none()
        )
        if not company:
            company = Company(user_id=self.user_id, name=company_name, display_name=display_name, jd_url=jd_url)
            self.db.add(company)
            self.db.flush()
        else:
            if display_name and not company.display_name:
                company.display_name = display_name
            if jd_url and not company.jd_url:
                company.jd_url = jd_url
        return company.id

    def register_file(
        self,
        company_id: int,
        file_type: str,
        file_path: Path,
        timestamp: Optional[str] = None,
    ) -> int:
        file_path = Path(file_path)
        sha256 = self._sha256(file_path)
        size = file_path.stat().st_size if file_path.exists() else None
        filename = file_path.name
        file_format = file_path.suffix.replace('.', '') if file_path.suffix else None

        company_file = CompanyFile(
            user_id=self.user_id,
            company_id=company_id,
            file_type=file_type,
            file_format=file_format,
            filename=filename,
            file_path=str(file_path),
            file_size=size,
            sha256=sha256,
            timestamp=timestamp,
        )
        self.db.add(company_file)
        self.db.flush()
        return company_file.id

    def set_cv_pointer(self, company_id: int, cv_type: str, file_id: int) -> None:
        pointer = (
            self.db.query(CVVersion)
            .filter(CVVersion.user_id == self.user_id, CVVersion.company_id == company_id, CVVersion.cv_type == cv_type)
            .one_or_none()
        )
        if not pointer:
            pointer = CVVersion(user_id=self.user_id, company_id=company_id, cv_type=cv_type, file_id=file_id, preferred=True)
            self.db.add(pointer)
        else:
            pointer.file_id = file_id

    def record_analysis_run(
        self,
        company_id: int,
        kind: str,
        status: str = "completed",
        model_used: Optional[str] = None,
        source_file_id: Optional[int] = None,
        output_file_id: Optional[int] = None,
        meta_json: Optional[dict] = None,
    ) -> int:
        run = AnalysisRun(
            user_id=self.user_id,
            company_id=company_id,
            kind=kind,
            status=status,
            model_used=model_used,
            source_file_id=source_file_id,
            output_file_id=output_file_id,
            meta_json=meta_json,
        )
        self.db.add(run)
        self.db.flush()
        return run.id


