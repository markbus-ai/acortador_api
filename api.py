from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import hashlib
from pydantic import BaseModel
import re
import apsw
import os



app = FastAPI()
urls = []

database_url = "sqlitecloud://cqkzchjlsk.sqlite.cloud:8860?apikey=TJcaW1eojOJOwitNKvdXmUxG9JMFnluQi5V26yv42Dk"  # **Do not use this in production!**

conn = apsw.Connection(database_url)
cursor = conn.cursor()

# Create a table to store shortened URLs (if it doesn't exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  long_url TEXT NOT NULL UNIQUE,
  short_url TEXT NOT NULL UNIQUE
);
""")
conn.commit()


# Permitir todas las solicitudes CORS desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
def recuperar_url_larga(short_url):
    """
    Recupera la URL larga correspondiente a una URL corta dada.
    """
    cursor.execute("SELECT long_url FROM urls WHERE short_url = ?", (short_url,))
    long_url = cursor.fetchone()
    if long_url:
        return long_url[0]
    return None  # Return None if short URL not found

def is_valid_url(url):
    """
    Expresión regular mejorada para validar formatos de URL más complejos y esquemas.
    """
    regex = r"""((http|https)://)(www.)?([a-zA-Z0-9@:%._\+~#?&//=]*)\.[a-zA-Z]+"""
    match = re.search(regex, url)
    return bool(match)

class Url(BaseModel):
    url: str

def generate_short_url(long_url):
    # Convert the long URL to a SHA-256 hash
    hash_object = hashlib.sha256(long_url.encode("utf-8")).hexdigest()
    short_url = hash_object[:6]

    cursor.execute("INSERT INTO urls (long_url, short_url) VALUES (?, ?)", (long_url, short_url))
    conn.commit()
    return f"https://{short_url}.com"  # Assuming a custom domain


@app.post("/shortener")
async def acortar(long_url: Url):
    try:
        if is_valid_url(long_url.url):
            # Check if URL already exists in database
            cursor.execute("SELECT * FROM urls WHERE long_url = ?", (long_url.url,))
            existing_url = cursor.fetchone()
            if existing_url:
                return existing_url[2]  # Return existing short URL

            short_url = generate_short_url(long_url.url)
            return short_url
        else:
            raise HTTPException(status_code=406, detail="formato de url invalido")
    except Exception as e:
        print(f"Error shortening URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{short_url}")
async def redirigir(short_url: str):
    url_larga = recuperar_url_larga(short_url)
    return RedirectResponse(url_larga)
