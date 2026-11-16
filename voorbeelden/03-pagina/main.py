from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

metingen = [
    {"temp": 18.2, "luchtdruk": 1013.2},
]


class Meting(BaseModel):
    temp: float
    luchtdruk: float


@app.get("/")
def home(request: Request):
    laatste = metingen[-1]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "temperatuur": f"{laatste['temp']:.1f}".replace(".", ","),
            "luchtdruk": f"{laatste['luchtdruk']:.1f}".replace(".", ","),
        },
    )


@app.get("/metingen")
def lijst_metingen():
    return metingen


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    metingen.append(meting.model_dump())
    return {"ontvangen": meting.model_dump()}
