from database import engine, Base
import models

Base.metadata.create_all(bind=engine, checkfirst=True)

print("tabel perpustakaan berhasil dibuat")