from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def read_root():
    return { "msg": "Moro local docker!" }

@app.get("/hello")
def hello():
    return { "msg": "what`s up" }

@app.get("/api/ip")
def ip(request: Request):
    return { "ip": request.client.host }

@app.get("/ip", response_class=HTMLResponse)
def ip(request: Request):
    return f"<h1>Din ip är {request.client.host}</h1>"

@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}
