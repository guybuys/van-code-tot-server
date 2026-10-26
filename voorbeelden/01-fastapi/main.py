from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

metingen = [
    {"temp": 18.2, "luchtdruk": 1013.2},
]


class Meting(BaseModel):
    temp: float
    luchtdruk: float


@app.get("/")
def home():
    return {"status": "ok", "service": "weerstation"}


@app.get("/metingen")
def lijst_metingen():
    return metingen


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    metingen.append(meting.model_dump())
    return {"ontvangen": meting.model_dump()}
