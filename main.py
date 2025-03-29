from typing import Optional

from fastapi import FastAPI

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World", "testing": os.getenv("TESTING")}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}