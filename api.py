from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import hashlib
from pydantic import BaseModel
import re


app = FastAPI(root_path="https://acortador-api.onrender")
urls = []

# Permitir todas las solicitudes CORS desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
def recuperar_url_larga(short_url: str):
    """
    Recupera la URL larga correspondiente a una URL corta dada.
    """
    for i in urls:
        if i["short_url"] == short_url:
            return i["long_url"]
    return None  # Retorna None si no se encuentra la URL corta

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
    
    return short_url

@app.post("/shortener")
async def acortar(long_url: Url):
    try:
        if is_valid_url(long_url.url):
            for url in urls:
                if url["long_url"] == long_url.url:
                    return url["short_url"]
            try:
                short_url = generate_short_url(long_url.url)
                urls.append({"long_url": long_url.url, "short_url": short_url})
                return f"https://acortador-api.onrender/{short_url}"
            except:
                raise HTTPException(status_code=404)
    except:
        raise HTTPException(status_code=406, detail="formato de url invalido")

@app.get("/{short_url}")
async def redirigir(short_url: str):
    url_larga = recuperar_url_larga(short_url)
    return RedirectResponse(url_larga)
