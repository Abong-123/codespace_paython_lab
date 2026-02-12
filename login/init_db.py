from database import engine, Base
import models

def init():
    print("membuat tabel")
    models.Base.metadata.create_all(bind=engine)
    print("tabel berhasil dibuat")

if __name__ == "__main__":
    init()