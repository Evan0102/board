from fastapi import FastAPI,HTTPException
import pandas as pd
from src.schemas import CreateMessageSchema,MessageSchema,UpdateMessageSchema

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


@app.get(
    "/message/{message_id}",
    response_model=MessageSchema
)
def get_message(message_id: int):
    messages = load_message()
    for index in messages:
        if index["id"] == message_id:
            return index
    raise HTTPException(status_code=404, detail="找不到訊息")


@app.get(
    "/messages",
    response_model=list[MessageSchema]
)
def get_all_messages():
    # 1. 讀取現有的留言(get or not)
    messages = load_message()
    # 2. 回傳留言
    return messages


@app.delete(
    "/message/{message_id}",
)
def delete_message(message_id: int):
    messages = load_message()
    for index, message in enumerate(messages):
        if message["id"] == message_id:
            del messages[index]
            save_message(messages)
            return HTTPException(status_code=204, detail="刪除成功")


@app.patch(
    "/message/{message_id}",
    response_model=MessageSchema
)
def update_message(message_id: int, body: UpdateMessageSchema):
    messages = load_message()
    for index, message in enumerate(messages):
        if message["id"] == message_id:
            if body.username:
                messages[index]["username"] = body.username
            if body.message:
                messages[index]["message"] = body.message
            save_message(messages)
            return messages[index]
            raise HTTPException(status_code=404, detail="找不到訊息")