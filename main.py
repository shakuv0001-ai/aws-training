from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register
@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed = auth.hash_password(password)
    user = models.User(username=username, password=hashed)
    db.add(user)
    db.commit()
    return {"message": "user created"}

# Login
@app.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user or not auth.verify_password(password, user.password):
        return {"error": "invalid login"}

    token = auth.create_token({"user_id": user.id})

    return {"token": token}

@app.get("/Ulist")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.User).all()

# Create Task
@app.post("/tasks")
def create_task(title: str, db: Session = Depends(get_db)):
    task = models.Task(title=title, owner_id=1)
    db.add(task)
    db.commit()
    return {"message": "task added"}

# Get Tasks
@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

# Update Task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    task.title = title
    db.commit()
    return {"message": "updated"}

# Delete Task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    db.delete(task)
    db.commit()
    return {"message": "deleted"}