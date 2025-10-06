from typing import Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.metadata import Company, CompanyFile


class DBLatestSelector:
    """DB-first selector for latest files per user/company/file_type."""

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    @classmethod
    def from_email(cls, db: Session, user_email: str):
        from app.models.user import User
        user = db.query(User).filter(User.email == user_email).one_or_none()
        if not user:
            raise ValueError("User not found")
        return cls(db=db, user_id=user.id)

    def _get_company_id(self, company_name: str) -> Optional[int]:
        company = (
            self.db.query(Company)
            .filter(Company.user_id == self.user_id, Company.name == company_name)
            .one_or_none()
        )
        return company.id if company else None

    def get_latest_file(self, company_name: str, file_type: str) -> Optional[Path]:
        company_id = self._get_company_id(company_name)
        if not company_id:
            return None
        rec = (
            self.db.query(CompanyFile)
            .filter(
                CompanyFile.user_id == self.user_id,
                CompanyFile.company_id == company_id,
                CompanyFile.file_type == file_type,
            )
            .order_by(CompanyFile.timestamp.desc().nullslast(), CompanyFile.id.desc())
            .first()
        )
        return Path(rec.file_path) if rec and rec.file_path else None


