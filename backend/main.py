from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Base, User, Note
from schemas import UserCreate, UserLogin, NoteCreate, NoteUpdate # type: ignore
from database import engine, get_db  # type: ignore
from auth import ACCESS_TOKEN_EXPIRE_MINUTES, hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

@app.post("/auth/register", response_model=dict)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

@app.post("/auth/login", response_model=dict)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/notes", response_model=list[dict])
def read_notes(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = db.query(User.id).filter(User.email == current_user).scalar()
    notes = (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.is_pinned.desc(), Note.created_at.desc())
        .all()
    )
    return [{"id": note.id, "title": note.title, "content": note.content, "is_pinned": note.is_pinned} for note in notes]

@app.post("/notes", response_model=dict)
def create_note(note: NoteCreate, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = db.query(User.id).filter(User.email == current_user).scalar()
    db_note = Note(user_id=user_id, title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return {"id": db_note.id, "title": db_note.title, "content": db_note.content}

@app.put("/notes/{note_id}", response_model=dict)
def update_note(note_id: int, note: NoteUpdate, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = db.query(User.id).filter(User.email == current_user).scalar()
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    return {"id": db_note.id, "title": db_note.title, "content": db_note.content}

@app.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = db.query(User.id).filter(User.email == current_user).scalar()
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return {"message": "Note deleted successfully"}

@app.patch("/notes/{note_id}/toggle-pin", response_model=dict)
def toggle_pin(note_id: int, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = db.query(User.id).filter(User.email == current_user).scalar()
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.is_pinned = not db_note.is_pinned
    db.commit()
    db.refresh(db_note)
    return {"id": db_note.id, "is_pinned": db_note.is_pinned}

