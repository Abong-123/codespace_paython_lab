from database import SessionLocal
from models import User, Class

db = SessionLocal()

kelas_list = ["7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B", "9C"]

for nama in kelas_list:
    if not db.query(Class).filter(Class.name == nama).first():
        db.add(Class(name=nama))
db.commit()
db.close()