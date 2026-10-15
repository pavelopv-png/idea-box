from fastapi import FastAPI

app = FastAPI(title="Копилка продуктовых идей", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": app.version}
