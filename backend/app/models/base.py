"""
Base mixin for all models.
Provides common fields: id, created_at, updated_at.
"""

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func


class TimestampMixin:
    """
    Mixin to add timestamp fields to models.
    Used for conflict resolution during synchronization.
    """
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class BaseModelMixin(TimestampMixin):
    """
    Base mixin with id and timestamps.
    All models should inherit from this.
    """
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
