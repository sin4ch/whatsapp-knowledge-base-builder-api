from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, String, DateTime
from datetime import datetime

from database import Base

class Text(BaseModel):
    body: str

class Message(BaseModel):
    from_number: str = Field(alias="from")
    id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str
    text: Text

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
    contacts: list[Contact]
    messages: list[Message]

class Change(BaseModel):
    field: str
    value: Value

class Entry(BaseModel):
    id: str
    changes: list[Change]

class WhatsAppPayload(BaseModel):
    object: str
    entry: list[Entry]

class StoredMessage(Base):
    __tablename__ = "WhatsApp Messages"
    id: str = Column(String, primary_key=True)
    sender_phone_number: str = Column(String, nullable=False)
    sender_name: str = Column(String, nullable=False)
    message_text: str = Column(String, nullable=True)
    timestamp: datetime = Column(DateTime(timezone=True), nullable=False)
    processed_by_llm: bool = Column(Boolean, nullable=False, default=False)