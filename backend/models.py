
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

from database import Base


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = mapped_column(Integer, primary_key=True, index=True)
    filename = mapped_column(String(255), nullable=False)
    job_description = mapped_column(Text, nullable=False)
    match_score = mapped_column(Integer, nullable=False)
    result = mapped_column(JSONB, nullable=False)
    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
