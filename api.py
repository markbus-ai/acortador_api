from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import hashlib
from pydantic import BaseModel
import re
import os
import asyncpg

app = FastAPI(root_path="https://acortador-api.onrender")
urls = []

async def connect_to_database(user, password, database, host):
    return await asyncpg.connect(
        user=user,
        password=password,
        database=database,
        host=host
    )
async def some_function():
    # Llamada a la función connect_to_database() con los valores adecuados
    connection = await connect_to_database(
        user="default",
        password="AUk8be4noEuD",
        database="verceldb",
        host="ep-crimson-feather-a4c6mujc-pooler.us-east-1.aws.neon.tech"
    )

    # Resto del código que utiliza la conexión a la base de datos


# Permitir todas las solicitudes CORS desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
async def recuperar_url_larga(short_url: str, connection):
    """
    Recupera la URL larga correspondiente a una URL corta dada.
    """
    query = "SELECT long_url FROM urls WHERE short_url = $1"
    url_larga = await connection.fetchval(query, short_url)
    return url_larga

def is_valid_url(url):
    """
    Expresión regular mejorada para validar formatos de URL más complejos y esquemas.
    """
    regex = r"""((http|https)://)(www.)?([a-zA-Z0-9@:%._\+~#?&//=]*)\.[a-zA-Z]+"""
    match = re.search(regex, url)
    return bool(match)

class Url(BaseModel):
    url: str

async def generate_short_url(long_url, connection):
    # Convert the long URL to a SHA-256 hash
    hash_object = hashlib.sha256(long_url.encode("utf-8")).hexdigest()
    
    short_url = hash_object[:6]

    query = "INSERT INTO urls (long_url, short_url) VALUES ($1, $2) RETURNING short_url"
    return await connection.fetchval(query, long_url, short_url)

@app.post("/shortener")
async def acortar(long_url: Url):
    try:
        if is_valid_url(long_url.url):
            async with connect_to_database(
                user="default",
                password="AUk8be4noEuD",
                database="verceldb",
                host="ep-crimson-feather-a4c6mujc-pooler.us-east-1.aws.neon.tech"
            ) as connection:
                query = "SELECT short_url FROM urls WHERE long_url = $1"
                existing_short_url = await connection.fetchval(query, long_url.url)
                if existing_short_url:
                    return existing_short_url
                else:
                    short_url = await generate_short_url(long_url.url, connection)
                    return f"https://acortador-api.onrender.com/{short_url}"
    except:
        raise HTTPException(status_code=406, detail="formato de url invalido")

@app.get("/{short_url}")
async def redirigir(short_url: str):
    async with connect_to_database(
        user="default",
        password="AUk8be4noEuD",
        database="verceldb",
        host="ep-crimson-feather-a4c6mujc-pooler.us-east-1.aws.neon.tech"
    ) as connection:
        url_larga = await recuperar_url_larga(short_url, connection)
        if url_larga:
            return RedirectResponse(url_larga)
        else:
            raise HTTPException(status_code=404)
