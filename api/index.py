from fastapi import FastAPI
from backend.app.main import app as scoring_app

app = FastAPI()
app.mount("/api", scoring_app)
