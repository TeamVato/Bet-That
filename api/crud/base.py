"""Base CRUD operations"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        query = db.query(self.model).filter(self.model.id == id)

        # Add soft delete check if model has deleted_at field
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))

        return query.first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering"""
        query = db.query(self.model)

        # Add soft delete check if model has deleted_at field
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        # Apply ordering
        if order_by and hasattr(self.model, order_by):
            query = query.order_by(getattr(self.model, order_by).desc())
        elif hasattr(self.model, "created_at"):
            query = query.order_by(self.model.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filtering"""
        query = db.query(self.model)

        # Add soft delete check if model has deleted_at field
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)

        return query.count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)

        # Set created_by if available in context
        if hasattr(db_obj, "created_by") and hasattr(db, "current_user_id"):
            db_obj.created_by = str(db.current_user_id)

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Update an existing record"""
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        # Update timestamp if available
        if hasattr(db_obj, "updated_at"):
            db_obj.updated_at = datetime.utcnow()

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Database integrity error: {str(e)}")

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Remove a record (soft delete if supported, hard delete otherwise)"""
        obj = self.get(db=db, id=id)
        if not obj:
            return None

        # Use soft delete if model supports it
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.utcnow()
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        else:
            # Hard delete
            db.delete(obj)
            db.commit()
            return obj

    def restore(self, db: Session, *, id: int) -> Optional[ModelType]:
        """Restore a soft-deleted record"""
        if not hasattr(self.model, "deleted_at"):
            raise ValueError("Model does not support soft delete")

        obj = (
            db.query(self.model)
            .filter(self.model.id == id, self.model.deleted_at.isnot(None))
            .first()
        )

        if obj:
            obj.deleted_at = None
            if hasattr(obj, "updated_at"):
                obj.updated_at = datetime.utcnow()
            db.add(obj)
            db.commit()
            db.refresh(obj)

        return obj

    def get_by_field(self, db: Session, *, field: str, value: Any) -> Optional[ModelType]:
        """Get a record by any field"""
        if not hasattr(self.model, field):
            raise ValueError(f"Model {self.model.__name__} does not have field {field}")

        query = db.query(self.model).filter(getattr(self.model, field) == value)

        # Add soft delete check if model has deleted_at field
        if hasattr(self.model, "deleted_at"):
            query = query.filter(self.model.deleted_at.is_(None))

        return query.first()
