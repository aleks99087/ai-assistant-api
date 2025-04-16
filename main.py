from fastapi import FastAPI, Request
from pydantic import BaseModel
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Временное хранилище истории (на потом — Supabase или Redis)
user_histories = {}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        message = data.get("message")

        if not user_id or not message:
            return {"reply": "Ошибка: не передан user_id или message"}

        history = user_histories.get(user_id, [])
        history.append({"role": "user", "content": message})

        messages = [
            {"role": "system", "content": "Ты ассистент по путешествиям. Помогай планировать маршруты."}
        ] + history

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8
        )

        assistant_message = response.choices[0].message.content
        history.append({"role": "assistant", "content": assistant_message})
        user_histories[user_id] = history[-10:]

        return {"reply": assistant_message}
    except Exception as e:
        return {"reply": f"Ошибка сервера: {str(e)}"}