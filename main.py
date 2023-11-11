from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from os import getenv, path
import threading
import time
from src.app import (
    getAirportData,
    getMultipleStationsMetar,
    getMultipleMetarWithTaf,
    getPirepsNearStation,
    getPirepsWithinDistance,
    getSigmets,
    getWinds,
    getDiscussion,
)


from src.advisory_circulars import ask_question
from src.airplane_FH_chat import ask_airplane

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI()

# Configure CORS options
ORIGINS = ["https://chat.openai.com"]  # Add other origins if needed

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request models
class AirportRequest(BaseModel):
    city: str


class StationsRequest(BaseModel):
    stations: list[str]


class StationRequest(BaseModel):
    station: str


class DiscussionRequest(BaseModel):
    code: str


class PirepsRequest(BaseModel):
    station: str
    range: str


class ac_list_request(BaseModel):
    query: str


# Route to serve the plugin manifest
@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    try:
        return FileResponse(
            path.join(path.dirname(__file__), ".well-known/ai-plugin.json"),
            media_type="application/json",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Route to serve the OpenAPI schema
@app.get("/openapi.yaml")
async def openapi_spec() -> Response:
    with open("openapi.yaml") as f:
        return Response(f.read(), media_type="text/yaml")


# Route to serve the logo image
@app.get("/logo.jpg")
async def get_logo():
    try:
        return FileResponse(
            path.join(path.abspath(""), "logo.png"), media_type="image/png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Define endpoints
@app.post("/airport-data")
async def airport_data_endpoint(request: AirportRequest):
    try:
        data = getAirportData(request.city)
        # await log_data("/generate_notes", video.dict(), result, header_info)
        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/multiple-stations-metar")
async def multiple_stations_metar_endpoint(request: StationsRequest):
    try:
        data = getMultipleStationsMetar(request.stations)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/metar-with-taf")
async def metar_with_taf_endpoint(request: StationsRequest):
    try:
        data = getMultipleMetarWithTaf(request.stations)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-pireps-standard")
async def pireps_standard_endpoint(request: StationRequest):
    try:
        data = getPirepsNearStation(request.station)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-pireps-within-range")
async def pireps_within_range_endpoint(request: PirepsRequest):
    try:
        data = getPirepsWithinDistance(request.station, request.range)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-sigmet-airmet")
async def sigmet_endpoint():
    try:
        data = getSigmets()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-winds-aloft")
async def sigmet_endpoint():
    try:
        data = getWinds()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/forecast-discussion")
async def forecast_discussion_endpoint(request: DiscussionRequest):
    try:
        data = getDiscussion(request.code)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to ask something from the AC list
@app.post("/advisory_circulars_list")
async def ask_endpoint(request: ac_list_request):
    print("Calling AC")
    print(request)
    try:
        data = ask_question(request.query)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to ask something from the Airplane Flying Handbook
@app.post("/ask_airplane_flying_handbook")
async def ask_endpoint(request: ac_list_request):
    print("Calling Airplane")
    print(request)
    try:
        data = ask_airplane(request.query)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Start the server
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
