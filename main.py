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
    df = pd.DataFrame(message)
    df.to_json("message.json", orient= "records")

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
@app.post(
    "/message",
    response_model=MessageSchema
)
async def create_message(body: CreateMessageSchema):

    messages = load_message()

    new_id = max([message['id']for message in messages], default=0) +1

    new_message = MessageSchema(
        id = new_id,
        username = body.username,
        message = body.message

    ).dict()
    messages.append(new_message)

    save_message(messages)
    return new_message

    