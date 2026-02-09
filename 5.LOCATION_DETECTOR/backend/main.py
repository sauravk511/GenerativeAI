"""
Location Detection API - Hybrid GPS + IP-based Geolocation Backend

Real-world principles:
- Combines GPS (mobile), Wi-Fi positioning, and IP-based geolocation
- Falls back gracefully when GPS is unavailable or denied
- Performs reverse geocoding to convert coordinates to human-readable locations
- Respects user privacy and permissions
- Returns standardized JSON for frontend consumption and learning
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import json
import os
import httpx
import logging
from typing import Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Location Detection API", version="1.0.0")

# Allow CORS for frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory for location output
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATION_FILE = os.path.join(OUTPUT_DIR, "location_output.json")


class GPSCoordinates(BaseModel):
    """Model for GPS coordinates from frontend"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None


class LocationResponse(BaseModel):
    """Standard location response model"""
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    city: Optional[str] = None
    area: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    source: str  # "gps" | "ip" | "manual"
    timestamp: str


async def get_ip_geolocation(client_ip: str) -> dict:
    """
    Perform IP-based geolocation using ip-api.com (free tier, no API key required)
    Falls back to ipinfo.io if needed
    
    Real-world note: Production systems often use MaxMind GeoIP2, but this uses
    free services for proof-of-concept purposes.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Try ip-api.com first (very reliable)
            try:
                response = await client.get(
                    f"http://ip-api.com/json/{client_ip}",
                    params={"fields": "lat,lon,city,regionName,country,status"}
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("status") == "success":
                    logger.info(f"IP geolocation successful for {client_ip}: {data['city']}, {data['regionName']}")
                    return {
                        "latitude": data.get("lat"),
                        "longitude": data.get("lon"),
                        "city": data.get("city"),
                        "region": data.get("regionName"),
                        "country": data.get("country"),
                        "source": "ip"
                    }
            except Exception as e:
                logger.warning(f"ip-api.com failed: {e}, trying ipinfo.io")
            
            # Fallback to ipinfo.io
            try:
                response = await client.get(
                    f"https://ipinfo.io/{client_ip}",
                    params={"token": ""}  # Free tier doesn't require token for basic info
                )
                response.raise_for_status()
                data = response.json()
                
                if "loc" in data:
                    lat, lon = map(float, data["loc"].split(","))
                    logger.info(f"IP geolocation (ipinfo.io) successful for {client_ip}: {data['city']}")
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "country": data.get("country"),
                        "source": "ip"
                    }
            except Exception as e:
                logger.warning(f"ipinfo.io failed: {e}")
    
    except Exception as e:
        logger.error(f"IP geolocation error: {e}")
    
    return {}


async def reverse_geocode(latitude: float, longitude: float) -> dict:
    """
    Perform reverse geocoding using OpenStreetMap Nominatim (free, no API key)
    
    Converts: latitude, longitude → city, area, region
    
    Real-world note: Nominatim is free but rate-limited. Production systems use
    paid services like Google Maps, Mapbox, or commercial GeoIP providers.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "json",
                    "zoom": 10,  # City-level zoom
                    "addressdetails": 1
                },
                headers={"User-Agent": "LocationDemo/1.0"}  # Nominatim requires User-Agent
            )
            response.raise_for_status()
            data = response.json()
            address = data.get("address", {})
            
            # Extract location hierarchy from OSM address
            location_info = {
                "city": address.get("city") or address.get("town") or address.get("village"),
                "area": address.get("suburb") or address.get("neighbourhood"),
                "region": address.get("state") or address.get("province"),
                "country": address.get("country")
            }
            
            logger.info(f"Reverse geocoding successful: {location_info['city']}, {location_info['region']}")
            return location_info
    
    except Exception as e:
        logger.error(f"Reverse geocoding error for ({latitude}, {longitude}): {e}")
        return {}


def save_location_to_file(location_data: dict) -> None:
    """Save resolved location data to JSON file for learning and verification purposes"""
    try:
        with open(LOCATION_FILE, "w") as f:
            json.dump(location_data, f, indent=2)
        logger.info(f"Location data saved to {LOCATION_FILE}")
    except Exception as e:
        logger.error(f"Failed to save location data: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Location Detection API"}


@app.post("/api/location/detect")
async def detect_location(
    coordinates: GPSCoordinates,
    request: Request
) -> JSONResponse:
    """
    Primary endpoint: Accept GPS coordinates from frontend
    
    Workflow:
    1. If GPS coordinates provided: Use them + reverse geocode
    2. If GPS denied/missing: Fall back to IP-based geolocation
    3. Always return structured location data
    
    Real-world: This demonstrates the hybrid approach used by platforms like
    Google Maps, Uber, Lyft, and social media apps.
    """
    client_ip = request.client.host
    
    logger.info(f"Location detection request from IP: {client_ip}")
    
    # PRIMARY: GPS-based location (mobile + browser Geolocation API)
    if coordinates.latitude is not None and coordinates.longitude is not None:
        logger.info(f"GPS coordinates provided: ({coordinates.latitude}, {coordinates.longitude})")
        
        # Reverse geocode GPS coordinates to get city/region
        geocoded = await reverse_geocode(coordinates.latitude, coordinates.longitude)
        
        location_data = {
            "latitude": coordinates.latitude,
            "longitude": coordinates.longitude,
            "accuracy": coordinates.accuracy,
            "city": geocoded.get("city"),
            "area": geocoded.get("area"),
            "region": geocoded.get("region"),
            "country": geocoded.get("country"),
            "source": "gps",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        save_location_to_file(location_data)
        return JSONResponse(content=location_data)
    
    # FALLBACK: IP-based geolocation (when GPS unavailable/denied)
    logger.info(f"GPS not available, falling back to IP-based geolocation")
    ip_location = await get_ip_geolocation(client_ip)
    
    if ip_location:
        location_data = {
            "latitude": ip_location.get("latitude"),
            "longitude": ip_location.get("longitude"),
            "accuracy": None,  # IP geolocation is less accurate
            "city": ip_location.get("city"),
            "area": None,  # Not typically available from IP services
            "region": ip_location.get("region"),
            "country": ip_location.get("country"),
            "source": "ip",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        save_location_to_file(location_data)
        return JSONResponse(content=location_data)
    
    # FINAL FALLBACK: No location detected
    logger.warning(f"No location available for IP: {client_ip}")
    return JSONResponse(
        status_code=202,  # Accepted (user needs to provide manual input)
        content={
            "error": "Location could not be detected automatically",
            "message": "Please provide your city manually",
            "source": "none",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )


@app.post("/api/location/manual")
async def set_manual_location(
    city: str,
    region: Optional[str] = None,
    country: Optional[str] = None,
    request: Request = None
) -> JSONResponse:
    """
    Manual fallback endpoint: Allow user to manually input location
    
    This is the final safety net ensuring no user is blocked due to
    permission denial or technical issues.
    """
    logger.info(f"Manual location input: {city}, {region}, {country}")
    
    location_data = {
        "latitude": None,
        "longitude": None,
        "accuracy": None,
        "city": city,
        "area": None,
        "region": region,
        "country": country,
        "source": "manual",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    save_location_to_file(location_data)
    return JSONResponse(content=location_data)


@app.get("/api/location/last")
async def get_last_location() -> JSONResponse:
    """Retrieve the last detected location from file (for learning purposes)"""
    try:
        if os.path.exists(LOCATION_FILE):
            with open(LOCATION_FILE, "r") as f:
                data = json.load(f)
            return JSONResponse(content=data)
        else:
            return JSONResponse(
                status_code=404,
                content={"error": "No location data available yet"}
            )
    except Exception as e:
        logger.error(f"Error reading location file: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to read location data: {str(e)}"}
        )


@app.get("/")
async def root():
    """API documentation"""
    return {
        "service": "Location Detection API",
        "version": "1.0.0",
        "description": "Hybrid GPS + IP-based location detection with reverse geocoding",
        "endpoints": {
            "POST /api/location/detect": "Submit GPS coordinates (or leave empty for IP fallback)",
            "POST /api/location/manual": "Manually set location when automatic detection fails",
            "GET /api/location/last": "Retrieve last detected location",
            "GET /health": "Health check"
        },
        "real_world_principles": [
            "Combines GPS, Wi-Fi positioning, and IP-based geolocation",
            "Respects user privacy and permissions",
            "Gracefully falls back when GPS is unavailable",
            "Performs reverse geocoding for human-readable locations",
            "Saves location data for verification and learning"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
