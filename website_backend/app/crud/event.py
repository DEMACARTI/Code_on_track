"""
CRUD operations for Event model.
"""
from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session

from app import models, schemas

def create_event(
    db: Session, 
    event_in: schemas.EventCreate,
    created_by_id: int
) -> models.Event:
    """
    Create a new event.
    """
    # Convert Pydantic model to dict and exclude unset values
    event_data = event_in.model_dump(exclude_unset=True)
    
    # Handle the metadata field
    if 'metadata' in event_data:
        event_data['event_metadata'] = event_data.pop('metadata')
    
    db_event = models.Event(
        **event_data,
        created_by_id=created_by_id,
        created_at=datetime.utcnow()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_event(db: Session, event_id: int) -> Optional[models.Event]:
    """
    Get an event by ID.
    """
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    item_uid: Optional[str] = None
) -> list[models.Event]:
    """
    Get a list of events, with optional filtering.
    """
    query = db.query(models.Event)
    
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
    if item_uid:
        query = query.filter(models.Event.item_uid == item_uid)
        
    return query.offset(skip).limit(limit).all()

def update_event(
    db: Session,
    db_event: models.Event,
    event_in: schemas.EventUpdate
) -> models.Event:
    """
    Update an existing event.
    """
    update_data = event_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_event, field, value)
        
    db_event.updated_at = datetime.utcnow()
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int) -> bool:
    """
    Delete an event by ID.
    Returns True if the event was deleted, False otherwise.
    """
    db_event = get_event(db, event_id)
    if not db_event:
        return False
        
    db.delete(db_event)
    db.commit()
    return True
