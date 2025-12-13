from sqlalchemy.orm import Session
from app.models.teacher import Teacher
import datetime

def create_teacher(db: Session, data: dict) -> Teacher:
    """
    Creates a new teacher/employee record.
    """
    new_teacher = Teacher(
        identity_number=data['identity_number'],
        full_name=data['full_name'],
        gender=data['gender'],
        employment_status=data['employment_status'],
        rank=data.get('rank'),      # Opsional
        status=data['status'],      # Aktif, Pensiun, dll
        address=data.get('address'),
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher

def update_teacher(db: Session, teacher_id: int, update_data: dict) -> Teacher | None:
    """
    Updates teacher details.
    """
    existing_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    
    if not existing_teacher:
        return None

    for key, value in update_data.items():
        if key == 'id':
            continue
        
        if hasattr(existing_teacher, key):
            setattr(existing_teacher, key, value)
    
    existing_teacher.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_teacher)
    return existing_teacher

def delete_teacher(db: Session, teacher_id: int) -> Teacher | None:
    """
    Deletes a teacher record.
    Warning: This might cascade delete the associated User account.
    """
    existing_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    
    if not existing_teacher:
        return None

    db.delete(existing_teacher)
    db.commit()
    return existing_teacher

def get_all_teachers(db: Session) -> list[Teacher]:
    return db.query(Teacher).all()

def get_teachers_by_keys(db: Session, filters: dict) -> list[Teacher]:
    query = db.query(Teacher)
    
    for key, value in filters.items():
        if hasattr(Teacher, key):
            column_to_filter = getattr(Teacher, key)
            query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    return query.all()