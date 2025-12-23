from sqlalchemy.orm import Session
from app.models.log import Log
import datetime

def create_log(db: Session, user_id: int, action: str) -> Log:
    """
    Creates a new activity log entry for audit trails.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user performing the action.
        action (str): A description of the action performed (e.g., "LOGIN", 
            "CREATED_LETTER").

    Returns:
        Log: The newly created log entry.
    """
    new_log = Log(
        user_id=user_id,
        action=action,
        timestamp=datetime.datetime.now()
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_all_logs(db: Session) -> list[Log]:
    """
    Retrieves all activity log entries.

    Args:
        db (Session): The database session.

    Returns:
        list[Log]: A list of all activity logs recorded in the system.
    """
    return db.query(Log).all()

def get_logs_paginated(db: Session, page: int = 1, per_page: int = 10) -> dict:
    """
    Mengambil data log dengan pagination, diurutkan berdasarkan waktu terbaru.
    Mengembalikan dict dengan keys: 'logs', 'total', 'page', 'per_page', 'total_pages'
    """
    query = db.query(Log).order_by(Log.created_at.desc())
    total = query.count()
    logs = query.offset((page - 1) * per_page).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'logs': logs,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    }

def get_logs_by_keys(db: Session, filters: dict) -> list[Log]:
    """
    Retrieves activity logs filtered by specific attributes.

    Args:
        db (Session): The database session.
        filters (dict): Dictionary of filters (e.g., {"user_id": 5, "action": "LOGIN"}).

    Returns:
        list[Log]: A list of log entries matching the criteria.

    Raises:
        ValueError: If a provided filter key is not a valid column attribute
            of the Log model.
    """
    query = db.query(Log)
    
    for key, value in filters.items():
        if not hasattr(Log, key):
            raise ValueError(f"Invalid column '{key}' for Log.")
        
        column_to_filter = getattr(Log, key)
        query = query.filter(column_to_filter.ilike(f"%{value}%"))
        
    return query.all()