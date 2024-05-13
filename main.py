from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins origins,
    allow credentials=True,
    allow_methods=["+"],
    allow_headers=["*"],
)
app.get("/")
def read root():
    return "Welcome to shorten url api"
