import os
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Annotated
import models
import crud
from models import WhatsAppPayload, StoredMessage
from database import create_table_and_start_db, get_db
from dotenv import load_dotenv

load_dotenv()
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
app = FastAPI()

@app.lifespan("startup")
async def on_startup():
    print("Application startup: Creating database and tables if they don't exist...")
    create_table_and_start_db() 
    print("Database and tables should be ready.")

@app.get("/webhook/whatsapp", response_class=PlainTextResponse)
async def verify_webhook(
    request: Request,
    hub_mode: Annotated[str | None, Query(alias="hub.mode")] = None,
    hub_challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
    hub_verify_token: Annotated[str | None, Query(alias="hub.verify_token")] = None,
):
    print(f"GET /webhook/whatsapp - Query Params: mode='{hub_mode}', challenge='{hub_challenge}', token='{hub_verify_token}'")
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        print("Webhook verification successful.")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        print(f"Webhook verification failed. Mode: {hub_mode}, Token: {hub_verify_token}, Expected Token: {VERIFY_TOKEN}")
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/webhook/whatsapp")
async def receive_whatsapp_message(
    payload: WhatsAppPayload,
    db_session: Session = Depends(get_db)
):
    print("Received POST request on /webhook/whatsapp")
    try:
        for entry in payload.entry:
            for change in entry.changes:
                if change.field == "messages" and change.value.messages:
                    for message_in_payload in change.value.messages:
                        if message_in_payload.type == "text" and message_in_payload.text:
                            print(f"Processing text message: {message_in_payload.id}")
                            try:
                                crud.create_stored_message(
                                    db=db_session,
                                    message_payload=message_in_payload,
                                )
                                print(f"Message {message_in_payload.id} stored successfully.")
                            except ValueError as ve:
                                print(f"Skipping message due to ValueError: {ve}")
                                continue
                            except Exception as e:
                                print(f"Error storing message {message_in_payload.id}: {e}")
                        else:
                            print(f"Skipping non-text message or message without text body: {message_in_payload.id}, type: {message_in_payload.type}")
        return {"success": "true"}
    except Exception as e:
        print(f"Critical error processing webhook payload: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")