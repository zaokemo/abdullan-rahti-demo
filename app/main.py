from fastapi import FastAPI, Request

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

@app.get("/items/{id}")
def read_item(item_id: int, q: str = None):
    return {"id": id, "q": q}
