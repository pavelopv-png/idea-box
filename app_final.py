from fastapi import FastAPI

app = FastAPI(title="Копилка продуктовых идей", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": app.version}


from pydantic import BaseModel, Field


class IdeaCreate(BaseModel):
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
    return idea
