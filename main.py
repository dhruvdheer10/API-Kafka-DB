from fastapi import FastAPI
from app.api.routes import router
from app.db import init_db
from dotenv import load_dotenv


load_dotenv() 

app = FastAPI()

app.include_router(router)

init_db()
