"""
UserAccount model — stores per-user service account credentials (encrypted)
and Google Sheet configuration.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, Text
from database import Base


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)

    # Fernet-encrypted service account JSON blob
    sa_encrypted = Column(LargeBinary, nullable=True)

    # User's Google Sheet URL (stored in DB so it persists across devices)
    sheet_url = Column(String(512), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserAccount uid={self.firebase_uid} email={self.email}>"
