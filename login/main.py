from fastapi import FastAPI, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from database import SessionLocal, engine, get_db
from hash import hash_password, verify_password
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
import models
import schemas
from typing import Optional
from typing import List
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from schemas import UserCreate, UserUpdate
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse



app = FastAPI()

templates = Jinja2Templates(directory="templates")


app.add_middleware(
    SessionMiddleware,
    secret_key = "SECRET_YANG_RAHASIA_BANGET"
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    existing_user = db.query(models.User)\
    .filter(models.User.username == user.username)\
    .first()

    if existing_user:
        raise HTTPException(
            status_code = 400,
            detail = "username sudah terdaftar"
        )
    existing_user = db.query(models.User)\
    .filter(models.User.email == user.email)\
    .first()

    if existing_user:
        raise HTTPException(
            status_code = 400,
            detail = "email sudah terdaftar"
        )
    
    hashed_pwd = hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    hashed_pw = hash_password(password)

    new_user = models.User(
        username=username, 
        email=email,
        password=hashed_pw
    )

    db.add(new_user)
    db.commit()

    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user or not verify_password(password, user.password):
        return RedirectResponse("/login", status_code =303)
    
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse("/login", status_code=302)
    
    payments = db.query(models.WaterPayment).filter(
        models.WaterPayment.user_id == user_id
    ).all()
    
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "payments": payments}
    )
@app.post("/add-payment")
def add_payment(
    request: Request,
    amount: int = Form(...),
    bulan: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=302)

    new_payment = models.WaterPayment(
        bulan=bulan,
        amount=amount,
        user_id=user_id
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return RedirectResponse("/dashboard", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

@app.post("/users/{user_id}/payments/")
def create_payment(user_id: int, payment: schemas.PaymentCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code = 404, detail = "user tidak ditemukan")
    
    new_payment = models.WaterPayment(
        bulan=payment.bulan,
        amount=payment.amount,
        user_id=user_id
    )

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    new_payment.create_at = new_payment.create_at.astimezone(
        ZoneInfo("Asia/Jakarta")
    )
    return new_payment

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="user tidak ditemukan")

    db.delete(user)
    db.commit()

    return{"mesage": "user dan semua payment berhasil dihapus"}

@app.delete("/payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(models.WaterPayment).filter(
        models.WaterPayment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="payment tidak ditemukan")
    
    db.delete(payment)
    db.commit()
    return{"message": "payment berhasil dihapus"}

@app.put("/users/{user_id}")
def update_user_put(user_id: int, user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="user tidak ditemukan")

    user.username = user_data.username
    user.email = user_data.email
    user.password = hash_password(user_data.password)

    db.commit()
    db.refresh(user)

    return{"message": "user berhasil diupdate"}

@app.patch("/users/{user_id}")
def update_user_patch(user_id: int, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="user tidak ditemukan")
    
    if user_data.username is not None:
        user.username = user_data.username
    
    if user_data.email is not None:
        user.email = user_data.email
    
    if user_data.password is not None:
        user.password = hash_password(user_data.password)
    
    db.commit()
    db.refresh(user)

    return{"message": "user berhasil diupdate (PATCH)"}
