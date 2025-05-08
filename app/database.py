import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

DB_URL = os.environ["DB_URL"]
Base = declarative_base()

if DB_URL:
    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_table_and_start_db():
    if DB_URL:
        Base.metadata.create_all(bind=engine)
    else:
        print("Database tables not created. DATABASE_URL not found.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

