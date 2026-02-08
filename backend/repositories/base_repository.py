"""Base repository class with common CRUD operations."""

from __future__ import annotations

from typing import TypeVar, Generic, Type, List, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import inspect

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations.

    Generic class to avoid code duplication across repositories.
    """

    def __init__(self, db: Session, model: Type[T]):
        """Initialize repository.

        Args:
            db: SQLAlchemy session.
            model: SQLAlchemy model class.
        """
        self.db: Session = db
        self.model: Type[T] = model

    def create(self, **kwargs: Any) -> T:
        """Create and persist a new record.

        Args:
            **kwargs: Model field values.

        Returns:
            Created model instance.
        """
        obj = self.model(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_by_id(self, id: int) -> Optional[T]:
        """Fetch record by primary key.

        Args:
            id: Primary key value.

        Returns:
            Model instance or None.
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Fetch all records with pagination.

        Args:
            limit: Max records to return.
            offset: Number of records to skip.

        Returns:
            List of model instances.
        """
        return self.db.query(self.model).limit(limit).offset(offset).all()

    def update(self, id: int, **kwargs: Any) -> Optional[T]:
        """Update existing record.

        Args:
            id: Primary key value.
            **kwargs: Field values to update.

        Returns:
            Updated model instance or None.
        """
        obj = self.get_by_id(id)
        if not obj:
            return None
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """Delete record by primary key.

        Args:
            id: Primary key value.

        Returns:
            True if deleted, False if not found.
        """
        obj = self.get_by_id(id)
        if not obj:
            return False
        self.db.delete(obj)
        self.db.commit()
        return True
