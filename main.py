import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from data import Data
from home import home_router
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(home_router, prefix='/home')

@app.get("/")
async def root():
    return RedirectResponse(url="/home")

@app.get("/meter-reads/{meter_id}")
async def meter_reads(meter_id: str):
    data = Data()
    data.ami_meter_reads(meter_id)
    readings = data.meter_readings
    phantom_flows = data.phantom_flows
    phantom_flows_30 = data.phantom_flows_30
    comm_issue = data.comm_issue
    disconnected = data.disconnected

    return {
        "phantom_flows": phantom_flows, 
        "phantom_flows_30": phantom_flows_30, 
        "meter_reads": readings,
        "comm_issue": comm_issue,
        "disconnected": disconnected,
    }

@app.get("/meter-list")
async def meter_list():
    data = Data()
    data.ami_meter_list()
    meters = data.meters
    return {"meters": meters}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

