from datetime import datetime, UTC
from sqlalchemy import Column, DateTime, Integer, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name."""
        return cls.__name__.lower()


class BaseModel(Base):
    """Base model class with common fields."""

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


# SQLAlchemy event listeners
@event.listens_for(BaseModel, "before_insert", propagate=True)
def set_created_at(mapper, connection, target):
    """Set created_at timestamp before insert."""
    target.created_at = datetime.now(UTC)
    target.updated_at = datetime.now(UTC)


@event.listens_for(BaseModel, "before_update", propagate=True)
def set_updated_at(mapper, connection, target):
    """Set updated_at timestamp before update."""
    target.updated_at = datetime.now(UTC)
