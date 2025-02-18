from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore
from sqlalchemy import create_engine, Column, Integer, String  # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Note model
class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for request body
class NoteSchema(BaseModel):
    title: str
    content: str

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD endpoints
@app.post("/notes/")
async def create_note(note: NoteSchema, db=Depends(get_db)): # type: ignore
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/notes/")
async def read_notes(skip: int = 0, limit: int = 10, db=Depends(get_db)): # type: ignore
    notes = db.query(Note).offset(skip).limit(limit).all()
    return notes

@app.get("/notes/{note_id}")
async def read_note(note_id: int, db=Depends(get_db)): # type: ignore
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}")
async def update_note(note_id: int, note: NoteSchema, db=Depends(get_db)): # type: ignore
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, db=Depends(get_db)): # type: ignore
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return {"detail": "Note deleted"}