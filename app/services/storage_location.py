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

def get_storage_locations_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data storage location dengan pagination.
    Mengembalikan dict dengan keys: 'storage_locations', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(StorageLocation)
    total = query.count()
    storage_locations = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'storage_locations': storage_locations,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }