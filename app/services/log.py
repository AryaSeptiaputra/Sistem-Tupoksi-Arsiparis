from sqlalchemy.orm import Session
from app.models.log import log
import datetime

def create_log(db: Session, user_id: int, action: str) -> log:
    new_log = log(
        user_id=user_id,
        action=action,
        timestamp=datetime.datetime.now().isoformat()
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log