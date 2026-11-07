
from fastapi import FastAPI

# Create FastAPI application
app = FastAPI()

# Root endpoint
@app.get("/")
def home():
    return {"message": "Hello, FastAPI"}
