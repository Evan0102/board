from fastapi import FastAPI
import pandas as pd
from src.schemas import CreateMessageSchema,MessageSchema

app = FastAPI()
def load_message():
    try:
        df = pd.read_json("message.json")
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []
def save_message(message):
    df = pd.Dataframe(message)
    df.to_json("message.json", orinet= "records")

@app.get("/")
async def root():
    return {
        "message": "Hello FastAPI!"
    }

@app.get("/test/{username}")
async def username_test(username):
    return {
        "message": f"Hello {username}"
    }

@app.post("/test/message")
async def message_test(username, message):
    return {
        "message":
            f"Hello {username} YOUR message is {message}"
    }