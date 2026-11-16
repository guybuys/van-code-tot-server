import json

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import database

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database.start()


class Meting(BaseModel):
    temp: float
    luchtdruk: float


def komma(getal):
    return f"{getal:.1f}".replace(".", ",")


def voor_tabel(rij):
    return {
        "tijd": rij["tijd"].replace("T", " ").replace("Z", "")[:16],
        "temperatuur": komma(rij["temp"]),
        "luchtdruk": komma(rij["luchtdruk"]),
    }


def voor_grafiek(rij):
    return {"tijd": rij["tijd"][11:16], "temp": rij["temp"]}


@app.get("/")
def home(request: Request):
    station_id = 1
    rijen = database.metingen_van_station(station_id)
    grafiek = [voor_grafiek(rij) for rij in rijen]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "station": database.naam_van_station(station_id),
            "metingen": [voor_tabel(rij) for rij in rijen],
            "grafiek_json": json.dumps(grafiek),
        },
    )


@app.get("/metingen")
def lijst_metingen():
    return database.alle_metingen()


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    return {"ontvangen": database.voeg_meting_toe(1, meting.temp, meting.luchtdruk)}
