from datetime import datetime
from typing import Optional
from database import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import JSON, DateTime, Integer, String, func

class WordFeature(Base):
    __tablename__ = "word features"

    phrase: Mapped[str] = mapped_column(String, nullable=False)
    length: Mapped[int] = mapped_column(Integer, nullable=False)
    palindrome: Mapped[bool] = mapped_column(default=False)
    num_words: Mapped[int] = mapped_column(Integer, nullable=False)
    num_unique_cha: Mapped[int] = mapped_column(Integer, nullable=False)
    freq_cha: Mapped[dict] = mapped_column(JSON,nullable=False)
    hashed: Mapped[str] = mapped_column(String, primary_key=True,  nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
