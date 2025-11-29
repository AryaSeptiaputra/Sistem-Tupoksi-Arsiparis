from sqlalchemy.orm import Session
from app.models.log import Log
import datetime

def create_log(db: Session, user_id: int, action: str) -> Log:
    """
    Creates a new activity log entry.
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