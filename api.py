from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import hashlib
from pydantic import BaseModel
import re
import os

# Database connection (using an external service)
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your actual database connection details
DATABASE_URL = f"sqlite:///{os.path.join(os.getcwd(), 'urls.db')}"  # Ruta local de SQLite3

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Url(Base):
    id: int = Column(Integer, primary_key=True)
    long_url: str = Column(String, unique=True, nullable=False)
    short_url: str = Column(String, nullable=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(root_path="https://acortador-api.onrender.com")

# Permitir todas las solicitudes CORS desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

def recuperar_url_larga(short_url: str, db):
    """
    Recupera la URL larga correspondiente a una URL corta dada.
    """
    url = db.query(Url).filter(Url.short_url == short_url).first()
    return url.long_url if url else None

def is_valid_url(url):
    """
    Expresión regular mejorada para validar formatos de URL más complejos y esquemas.
    """
    regex = r"""((http|https)://)(www.)?([a-zA-Z0-9@:%._\+~#?&//=]*)\.[a-zA-Z]+"""
    match = re.search(regex, url)
    return bool(match)


@app.get("/shortener")
async def comprobrar():
    return "Holaaaaaaaaa"


@app.post("/shortener")
async def acortar(long_url: Url, db):
    try:
        if is_valid_url(long_url.url):
            existing_url = db.query(Url).filter(Url.long_url == long_url.url).first()
            if existing_url:
                return existing_url.short_url

            short_url = generate_short_url(long_url.url)
            new_url = Url(long_url=long_url.url, short_url=short_url)
            db.add(new_url)
            db.commit()
            return f"https://{short_url}.com"
        else:
            raise HTTPException(status_code=406, detail="formato de url invalido")
    except:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/{short_url}")
async def redirigir(short_url: str, db):
    url_larga = recuperar_url_larga(short_url, db)
    if url_larga:
        return RedirectResponse(url_larga)
    else:
        return HTTPException(status_code=404, detail="URL not found")

def generate_short_url(long_url):
    # Convert the long URL to a SHA-256 hash
    hash_object = hashlib.sha256(long_url.encode("utf-8")).hexdigest()

    short_url = hash_object[:6]

    return short_url
