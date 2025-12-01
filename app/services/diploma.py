from sqlalchemy.orm import Session
from app.models.diploma import Diploma
import datetime

def create_diploma(db: Session, diploma_data: dict, user_id: int) -> Diploma:
    """
    Creates a new diploma record in the database for SMK students.

    Args:
        db (Session): The database session.
        diploma_data (dict): A dictionary containing the diploma fields.
        user_id (int): The ID of the user (admin/staff) creating the record.

    Returns:
        Diploma: The newly created and committed diploma record.
    """
    new_diploma = Diploma(
        number=diploma_data['number'],
        student_name=diploma_data['student_name'],
        major=diploma_data['major'],  # Menggantikan class_name
        academic_year=diploma_data['academic_year'],
        
        # Atribut baru untuk status pengambilan
        is_collected=diploma_data.get('is_collected', False),
        collected_at=diploma_data.get('collected_at'),
        
        attachment_path=diploma_data.get('attachment_path'),
        user_id=user_id,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_diploma)
    db.commit()
    db.refresh(new_diploma)
    return new_diploma

def update_diploma(db: Session, diploma_id: int, update_data: dict) -> Diploma | None:
    """
    Updates an existing diploma record identified by its ID.
    
    Useful for updating typos, changing attachment paths, or 
    updating the collection status (is_collected).

    Args:
        db (Session): The database session.
        diploma_id (int): The ID of the diploma to update.
        update_data (dict): A dictionary of fields to update.

    Returns:
        Diploma | None: The updated record, or None if the record was not found.
    """
    existing_diploma = db.query(Diploma).filter(Diploma.id == diploma_id).first()
    if not existing_diploma:
        return None

    for key, value in update_data.items():
        # Mencegah perubahan ID atau user_id pembuat asli
        if key in ['id', 'user_id']:
            continue
        
        # Khusus logika jika user mengupdate status pengambilan menjadi True
        # Jika is_collected diubah jadi True dan collected_at belum ada, isi otomatis
        if key == 'is_collected' and value is True and not update_data.get('collected_at'):
             if not existing_diploma.collected_at:
                 existing_diploma.collected_at = datetime.datetime.now()

        if hasattr(existing_diploma, key):
            setattr(existing_diploma, key, value)

    existing_diploma.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_diploma)
    return existing_diploma

def delete_diploma(db: Session, diploma_id: int) -> Diploma | None:
    """
    Deletes a diploma record from the database by its ID.

    Args:
        db (Session): The database session.
        diploma_id (int): The ID of the diploma to delete.

    Returns:
        Diploma | None: The deleted record instance, or None if not found.
    """
    existing_diploma = db.query(Diploma).filter(Diploma.id == diploma_id).first()
    if not existing_diploma:
        return None

    db.delete(existing_diploma)
    db.commit()
    return existing_diploma

def get_all_diplomas(db: Session) -> list[Diploma]:
    """
    Retrieves all diploma records available in the database.

    Args:
        db (Session): The database session.

    Returns:
        list[Diploma]: A list of all Diploma instances.
    """
    return db.query(Diploma).all()

def get_diplomas_by_keys(db: Session, filters: dict) -> list[Diploma]:
    """
    Retrieves diploma records filtered by specific column values.
    
    Supports filtering by major, student name, academic year, etc.

    Args:
        db (Session): The database session.
        filters (dict): A dictionary of key-value pairs to filter the query.
            Keys must match valid column names in the Diploma model.

    Returns:
        list[Diploma]: A list of diplomas that match the filter criteria.

    Raises:
        ValueError: If a key in the filters dictionary is not a valid attribute.
    """
    query = db.query(Diploma)
    
    for key, value in filters.items():
        if not hasattr(Diploma, key):
            raise ValueError(f"Invalid column '{key}' for Diploma.")
        
        column_to_filter = getattr(Diploma, key)
        
        # Logika khusus: Boolean tidak bisa menggunakan ILIKE
        if isinstance(value, bool):
            query = query.filter(column_to_filter == value)
        else:
            # Menggunakan ilike untuk pencarian teks yang fleksibel (case-insensitive)
            query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    return query.all()