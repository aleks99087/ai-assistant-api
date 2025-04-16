from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    user_id: str
    message: str

# временно: история в памяти (можно позже перенести в Supabase/Redis)
user_histories = {}

@app.post("/chat")
async def chat(req: ChatRequest):
    history = user_histories.get(req.user_id, [])
    
    # Добавляем новое сообщение
    history.append({"role": "user", "content": req.message})
    
    # Строим полный prompt
    messages = [{"role": "system", "content": "Ты ассистент по путешествиям. Помогай планировать маршруты."}] + history

    # Запрос в OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8
    )
    
    assistant_message = response.choices[0].message.content
    history.append({"role": "assistant", "content": assistant_message})
    
    # Сохраняем обновлённую историю
    user_histories[req.user_id] = history[-10:]  # ограничим историю 10 сообщениями

    return {"reply": assistant_message}
