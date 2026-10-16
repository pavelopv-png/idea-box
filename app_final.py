import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi import FastAPI

app = FastAPI(title=os.getenv("APP_NAME", "Копилка продуктовых идей"), version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": app.version}


from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
    model_config = {"str_strip_whitespace": True}

    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)


ideas = []


@app.post("/ideas", status_code=201)
def create_idea(data: IdeaCreate):
    idea = {
        "id": len(ideas) + 1,
        "title": data.title,
        "description": data.description,
    }
    ideas.append(idea)
    logger.info("Created idea id=%s", idea["id"])
    return idea


from fastapi.responses import HTMLResponse


@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Копилка идей</title>
</head>
<body>
    <h1>Копилка продуктовых идей</h1>
    <form id="idea-form">
        <p>
            <label for="title">Название</label><br>
            <input id="title" required maxlength="100">
        </p>
        <p>
            <label for="description">Описание</label><br>
            <textarea id="description" rows="5" cols="40"
                      maxlength="1000"></textarea>
        </p>
        <button type="submit">Сохранить</button>
    </form>
    <p id="result" role="status"></p>
    <p>Идеи хранятся до перезапуска приложения.</p>
    <a href="/docs">Документация API</a>

    <script>
        const form = document.getElementById("idea-form");
        const result = document.getElementById("result");

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const button = form.querySelector("button");
            button.disabled = true;
            result.textContent = "Сохранение...";

            try {
                const response = await fetch("/ideas", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        title: document.getElementById("title").value,
                        description: document.getElementById("description").value
                    })
                });

                if (response.ok) {
                    const idea = await response.json();
                    result.textContent = "Идея сохранена. Номер: " + idea.id;
                    form.reset();
                } else if (response.status === 422) {
                    result.textContent = "Проверьте название и длину полей. Название не может состоять из пробелов.";
                } else {
                    result.textContent = "Ошибка сервера: " + response.status;
                }
            } catch {
                result.textContent = "Нет связи с сервером. Проверьте, запущено ли приложение.";
            } finally {
                button.disabled = false;
            }
        });
    </script>
</body>
</html>
"""


from fastapi import HTTPException


@app.get("/ideas")
def list_ideas():
    return ideas


@app.get("/ideas/{idea_id}")
def get_idea(idea_id: int):
    for idea in ideas:
        if idea["id"] == idea_id:
            return idea
    raise HTTPException(status_code=404, detail="Идея не найдена")
