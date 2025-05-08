from sqlalchemy.orm import Session
import models

def create_stored_db(db_session: Session, message_payload: models.Message, value_payload: models.Value) -> models.StoredMessage:
    """
    Creates and stores a new message in the database.
    """
    sender_wa_id = message_payload.from_number
    sender_name = None
    if value_payload.contacts and value_payload.contacts[0].profile:
        sender_name = value_payload.contacts[0].profile.name
    if message_payload.text is None:
        raise ValueError("Message does not contain text body.")

    db_message = models.StoredMessage(
        sender_phone_number=sender_wa_id,
        sender_name=sender_name,
        message_text=message_payload.text.body,
        timestamp=message_payload.timestamp,
        processed_by_llm=False
    )
    db_session.add(db_message)
    db_session.commit()
    db_session.refresh(db_message)
    return db_message
    
def get_unprocessed_messages(db_session: Session) -> list[models.StoredMessage]:
    """
    Retrieves all messages that have not yet been processed by the LLM.
    """
    return db_session.query(models.StoredMessage).filter(models.StoredMessage.processed_by_llm == False).all()

def mark_messages_as_processed(db: Session, message_ids: list[int]) -> None:
    """
    Marks a list of messages as processed by the LLM.
    """
    if not message_ids:
        return
    db.query(models.StoredMessage).filter(models.StoredMessage.id.in_(message_ids)).\
        update({models.StoredMessage.processed_by_llm: True}, synchronize_session=False)
    db.commit()
