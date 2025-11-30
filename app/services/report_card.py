from sqlalchemy.orm import Session
from app.models.report_card import ReportCard
import datetime

def create_report_card(db: Session, report_data: dict, user_id: int) -> ReportCard:
    """
    Creates a new report card record in the database.

    Args:
        db (Session): The database session.
        report_data (dict): A dictionary containing the report card fields.
        user_id (int): The ID of the user creating the record.

    Returns:
        ReportCard: The newly created and committed report card record.
    """
    new_report = ReportCard(
        number=report_data['number'],
        student_name=report_data['student_name'],
        class_name=report_data['class_name'],
        academic_year=report_data['academic_year'],
        attachment_path=report_data.get('attachment_path'),
        user_id=user_id,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

def update_report_card(db: Session, report_id: int, update_data: dict) -> ReportCard | None:
    """
    Updates an existing report card record identified by its ID.

    Args:
        db (Session): The database session.
        report_id (int): The ID of the report card to update.
        update_data (dict): A dictionary of fields to update.

    Returns:
        ReportCard | None: The updated record, or None if the record was not found.
    """
    existing_report = db.query(ReportCard).filter(ReportCard.id == report_id).first()
    if not existing_report:
        return None

    for key, value in update_data.items():
        if key == 'id' or key == 'user_id':
            continue
        if hasattr(existing_report, key):
            setattr(existing_report, key, value)

    existing_report.updated_at = datetime.datetime.now()
    
    db.commit()
    db.refresh(existing_report)
    return existing_report

def delete_report_card(db: Session, report_id: int) -> ReportCard | None:
    """
    Deletes a report card record from the database by its ID.

    Args:
        db (Session): The database session.
        report_id (int): The ID of the report card to delete.

    Returns:
        ReportCard | None: The deleted record instance, or None if not found.
    """
    existing_report = db.query(ReportCard).filter(ReportCard.id == report_id).first()
    if not existing_report:
        return None

    db.delete(existing_report)
    db.commit()
    return existing_report

def get_all_report_cards(db: Session) -> list[ReportCard]:
    """
    Retrieves all report card records available in the database.

    Args:
        db (Session): The database session.

    Returns:
        list[ReportCard]: A list of all ReportCard instances.
    """
    return db.query(ReportCard).all()

def get_report_cards_by_keys(db: Session, filters: dict) -> list[ReportCard]:
    """
    Retrieves report card records filtered by specific column values.

    Args:
        db (Session): The database session.
        filters (dict): A dictionary of key-value pairs to filter the query.
            Keys must match valid column names in the ReportCard model
            (e.g., {"student_name": "Budi", "class_name": "XA"}).

    Returns:
        list[ReportCard]: A list of report cards that match the filter criteria.

    Raises:
        ValueError: If a key in the filters dictionary is not a valid attribute
            of the ReportCard model.
    """
    query = db.query(ReportCard)
    
    for key, value in filters.items():
        if not hasattr(ReportCard, key):
            raise ValueError(f"Invalid column '{key}' for ReportCard.")
        
        column_to_filter = getattr(ReportCard, key)
        query = query.filter(column_to_filter == value)
        
    return query.all()

