import json
import os

import bcrypt
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

import database

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("WEERSTATION_SLEUTEL", "alleen-op-deze-laptop"),
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database.start()

FOUT_AANMELDEN = "Onbekend e-mailadres of wachtwoord."


class Meting(BaseModel):
    temp: float
    luchtdruk: float


def hash_wachtwoord(wachtwoord):
    return bcrypt.hashpw(wachtwoord.encode(), bcrypt.gensalt()).decode()


def wachtwoord_klopt(wachtwoord, wachtwoord_hash):
    return bcrypt.checkpw(wachtwoord.encode(), wachtwoord_hash.encode())


def huidige_gebruiker(request):
    gebruiker_id = request.session.get("gebruiker_id")
    if gebruiker_id is None:
        return None
    return database.gebruiker_van_id(gebruiker_id)


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


def pagina(request, gebruiker, stations, station, geweigerd, rijen):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "gebruiker": gebruiker,
            "beheerder": gebruiker["rol"] == "beheerder",
            "stations": stations,
            "station": station,
            "geweigerd": geweigerd,
            "metingen": [voor_tabel(rij) for rij in rijen],
            "grafiek_json": json.dumps([voor_grafiek(rij) for rij in rijen]),
        },
    )


@app.get("/login")
def login_pagina(request: Request):
    return templates.TemplateResponse(request, "login.html", {"fout": ""})


@app.post("/login")
def meld_aan(request: Request, email: str = Form(), wachtwoord: str = Form()):
    gebruiker = database.gebruiker_van_email(email)
    klopt = (
        gebruiker is not None
        and wachtwoord_klopt(wachtwoord, gebruiker["wachtwoord_hash"])
    )
    if not klopt:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"fout": FOUT_AANMELDEN},
            status_code=401,
        )
    request.session["gebruiker_id"] = gebruiker["id"]
    return RedirectResponse("/", status_code=303)


@app.get("/registreren")
def registratie_pagina(request: Request):
    return templates.TemplateResponse(request, "registreren.html", {"fout": ""})


@app.post("/registreren")
def registreer(
    request: Request,
    naam: str = Form(),
    email: str = Form(),
    wachtwoord: str = Form(),
):
    if len(wachtwoord) < 8:
        return templates.TemplateResponse(
            request,
            "registreren.html",
            {"fout": "Kies een wachtwoord van minstens 8 tekens."},
            status_code=400,
        )
    gebruiker_id = database.voeg_gebruiker_toe(naam, email, hash_wachtwoord(wachtwoord))
    if gebruiker_id is None:
        return templates.TemplateResponse(
            request,
            "registreren.html",
            {"fout": "Dit e-mailadres bestaat al."},
            status_code=400,
        )
    request.session["gebruiker_id"] = gebruiker_id
    return RedirectResponse("/", status_code=303)


@app.post("/afmelden")
def meld_af(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/")
def home(request: Request, station_id: int = None):
    gebruiker = huidige_gebruiker(request)
    if gebruiker is None:
        return RedirectResponse("/login", status_code=303)

    if gebruiker["rol"] == "beheerder":
        stations = database.alle_stations()
        if station_id is None and stations:
            station_id = stations[0]["id"]
        naam = database.naam_van_station(station_id) if station_id else None
        rijen = database.metingen_van_station(station_id) if naam else []
        return pagina(request, gebruiker, stations, naam, False, rijen)

    stations = database.stations_van_gebruiker(gebruiker["id"])
    if station_id is None and len(stations) == 1:
        station_id = stations[0]["id"]
    if station_id is None:
        return pagina(request, gebruiker, stations, None, False, [])
    eigen = database.station_van_gebruiker(station_id, gebruiker["id"])
    if eigen is None:
        return pagina(request, gebruiker, stations, None, True, [])
    rijen = database.metingen_van_station(station_id)
    return pagina(request, gebruiker, stations, eigen["naam"], False, rijen)


@app.get("/beheer")
def beheer_pagina(request: Request):
    gebruiker = huidige_gebruiker(request)
    if gebruiker is None:
        return RedirectResponse("/login", status_code=303)
    if gebruiker["rol"] != "beheerder":
        raise HTTPException(status_code=403)
    return templates.TemplateResponse(
        request,
        "beheer.html",
        {
            "gebruiker": gebruiker,
            "stations": database.alle_stations(),
            "fout": "",
        },
    )


@app.post("/beheer")
def koppel(request: Request, station_id: int = Form(), email: str = Form()):
    gebruiker = huidige_gebruiker(request)
    if gebruiker is None:
        return RedirectResponse("/login", status_code=303)
    if gebruiker["rol"] != "beheerder":
        raise HTTPException(status_code=403)
    fout = ""
    if not database.koppel_station(station_id, email):
        fout = "Dat station of dat e-mailadres staat niet in de database."
    return templates.TemplateResponse(
        request,
        "beheer.html",
        {
            "gebruiker": gebruiker,
            "stations": database.alle_stations(),
            "fout": fout,
        },
    )


@app.get("/metingen")
def lijst_metingen():
    return database.alle_metingen()


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    return {"ontvangen": database.voeg_meting_toe(1, meting.temp, meting.luchtdruk)}
