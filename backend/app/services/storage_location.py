from sqlalchemy.orm import Session
from app.models.storage_location import StorageLocation
import datetime

def create_storage_location(db: Session, data: dict) -> StorageLocation:
    """Creates a new storage location (e.g., Cupboard/Shelf)."""
    new_location = StorageLocation(
        name=data['name'],
        description=data.get('description'),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_location)
    db.commit()
    db.refresh(new_location)
    return new_location

def update_storage_location(db: Session, location_id: int, update_data: dict) -> StorageLocation | None:
    """Updates an existing storage location."""
    location = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not location:
        return None

    if 'name' in update_data:
        location.name = update_data['name']
    if 'description' in update_data:
        location.description = update_data['description']
    
    location.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(location)
    return location

def delete_storage_location(db: Session, location_id: int) -> StorageLocation | None:
    """Deletes a storage location."""
    location = db.query(StorageLocation).filter(StorageLocation.id == location_id).first()
    if not location:
        return None

    db.delete(location)
    db.commit()
    return location

def get_all_storage_locations(db: Session) -> list[StorageLocation]:
    """Retrieves all storage locations."""
    return db.query(StorageLocation).all()