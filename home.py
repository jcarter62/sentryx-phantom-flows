from fastapi import APIRouter, Path, HTTPException, status, Request, Depends
from fastapi.templating import Jinja2Templates
from data import Data


home_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@home_router.get("/")
async def home_root(request: Request):
    d = Data()
    d.ami_meter_list()
    meters = d.meters
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "meters": meters
         })

