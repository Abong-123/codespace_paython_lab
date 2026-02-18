from fastapi import FastAPI
from hash import hash_password, verify_password

app = FastAPI()

@app.get("/hash")
def test_hash():
    return {"hashed": hash_password("password123")}