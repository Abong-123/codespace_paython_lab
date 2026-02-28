#----------------------------------- main.py -----------------------------------#
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session, joinedload
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from starlette.middleware.sessions import SessionMiddleware
#------------------------------- import models and schemas -----------------------------------#
import models
import schemas
from database import SessionLocal, engine, get_db
from datetime import datetime, date
from typing import List
from security import hash_password, verify_password

#------------------------------- settings -----------------------------------#
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key="SECRET_YANG_RAHASIA_BANGET",
)

#------------------------------- Jinja -----------------------------------#
@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(
    request: Request,
    nama: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    existing = db.query(models.Player).filter(
        models.Player.nama == nama
    ).first()

    if existing: 
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "nama sudah digunakan"}
        )
    
    hashed_password = hash_password(password)
    new_player = models.Player(
        nama=nama,
        email=email,
        password=hashed_password
    )

    db.add(new_player)
    db.commit()

    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.Player).filter(
        models.Player.email == email
    ).first()

    if not user or not verify_password(user.password, password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "email atau password salah"}
        )
    request.session["user_id"] = user.id
    request.session["user_name"] = user.nama
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    user_id = request.session["user_id"]
    
    books = db.query(models.Book).all()

    active_loans = db.query(models.Loan).options(joinedload(models.Loan.book)).filter(
        models.Loan.player_id == user_id,
        models.Loan.tanggal_kembali.is_(None)
    ).all()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "nama": request.session["user_name"],
            "books": books,
            "active_loans": active_loans
        }
    )

@app.get("/borrow/{book_id}", response_class=HTMLResponse)
def borrow_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or book.status != "available":
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "nama": request.session["user_name"],
                "books": db.query(models.Book).all(),
                "error": "Buku tidak tersedia"
            }
        )
    return templates.TemplateResponse(
        "borrow.html",
        {
            "request": request,
            "nama": request.session["user_name"],
            "book": book
        }
    )

@app.post("/borrow/{book_id}")
def borrow_book(
    book_id: int,
    request: Request,
    tanggal_kembali: str = Form(...),
    db: Session = Depends(get_db)
):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    book = db.query(models.Book).filter(models.Book.id == book_id).first()

    if not book or book.status != "available":
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "nama": request.session["user_name"],
                "books": db.query(models.Book).all(),
                "error": "Buku tidak tersedia"
            }
        )
    
    try:
        tanggal_kembali_dt = datetime.strptime(tanggal_kembali, "%Y-%m-%d")
    except ValueError:
        return templates.TemplateResponse(
            "borrow.html",
            {
                "request": request,
                "nama": request.session["user_name"],
                "book": book,
                "error": "Format tanggal kembali salah, gunakan YYYY-MM-DD"
            }
        )
    
    new_loan = models.Loan(
        player_id=request.session["user_id"],
        book_id=book.id,
        tanggal_pinjam=datetime.utcnow(),
        rencana_kembali=tanggal_kembali_dt,  # ← input user masuk sini
        tanggal_kembali=None                 # ← ini None dulu
    )

    book.status = "borrowed"

    db.add(new_loan)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/return/{book_id}")
def return_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    if "user_id" not in request.session:
        return RedirectResponse(url="/login", status_code=303)
    
    user_id = request.session["user_id"]

    loan = db.query(models.Loan).options(joinedload(models.Loan.book)).filter(
        models.Loan.player_id == user_id,
        models.Loan.book_id == book_id,
        models.Loan.tanggal_kembali.is_(None)
    ).first()

    if not loan:
        return RedirectResponse(url="/dashboard", status_code=303)
    
    loan.tanggal_kembali = datetime.utcnow()
    loan.book.status = "available"
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

#----------------------------------- swagger -----------------------------------#
@app.post("/players")
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Player).filter(
        models.Player.nama == player.nama
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nama sudah digunakan")
    
    existing = db.query(models.Player).filter(
        models.Player.email == player.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email sudah digunakan")
    
    hashed_password = hash_password(player.password)
    new_player = models.Player(
        nama=player.nama,
        email=player.email,
        password=hashed_password
    )

    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return {"message": "Player berhasil didaftarkan", "player_id": new_player.id}

@app.post("/books")
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Book).filter(
        models.Book.nomer_buku == book.nomer_buku
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nomor buku sudah digunakan")
    
    new_book = models.Book(
        nomer_buku=book.nomer_buku,
        judul=book.judul,
        penulis=book.penulis,
        tahun_terbit=book.tahun_terbit
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "Buku berhasil ditambahkan", "book_id": new_book.id}

@app.get("/players")
def get_players(db: Session = Depends(get_db)):
    players = db.query(models.Player).all()
    return players

@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books