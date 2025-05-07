from pydantic import BaseModel, field_validator
from typing import List
from sqlalchemy import Boolean, Column, Integer, Float, String, DateTime
from datetime import datetime

from database import Base

class Text:
    body: str

class Message(BaseModel):
    sender_number: str
    id: str
    timestamp: str
    type: str
    text: Text

    @field_validator("timestamp", pre=True)
    def change_timestamp_to_datetime_format(cls, value):
        """
        Changes timestamp to apt datetime format
        """
        if isinstance(value, str):
            datetime.fromtimestamp(int(value))
        return value

class Profile(BaseModel):
    name: str

class Contact(BaseModel):
    profile: Profile
    wa_id: str

class MetaData(BaseModel):
    display_phone_number: str
    phone_number_id: str

class Value(BaseModel):
    messaging_product: str
    metadata: MetaData
    contacts: List[Contact]
    messages: List[Message]

class Change(BaseModel):
    field: str
    value: Value

class Entry(BaseModel):
    id: str
    changes: List[Change]

class WhatsAppPayload(BaseModel):
    object: str
    entry: Entry

class StoredMessage(Base):
    __tablename__ = "WhatsApp Messages"
    id: str = Column(String, primary_key=True)
    sender_name: str = Column(String, nullable=False)
    message_text: str = Column(String, nullable=True)
    timestamp: datetime = Column(DateTime, nullable=False)
    processed_by_llm: bool = Column(Boolean, nullable=False, default=False)