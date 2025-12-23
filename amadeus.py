import os
import httpx
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional, List

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)

CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"

# -------------------------------------------------
# API URLs
# -------------------------------------------------
FLIGHT_OFFERS_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"
FLIGHT_PRICING_URL = "https://test.api.amadeus.com/v1/shopping/flight-offers/pricing"
SEATMAP_URL = "https://test.api.amadeus.com/v1/shopping/seatmaps"
FLIGHT_ORDER_URL = "https://test.api.amadeus.com/v1/booking/flight-orders"

FLIGHT_INSPIRATION_URL = "https://test.api.amadeus.com/v1/shopping/flight-destinations"
CHEAPEST_DATE_URL = "https://test.api.amadeus.com/v1/shopping/flight-dates"
AVAILABILITY_URL = "https://test.api.amadeus.com/v1/shopping/availability/flight-availabilities"

FLIGHT_STATUS_URL = "https://test.api.amadeus.com/v2/schedule/flights"
CHECKIN_LINKS_URL = "https://test.api.amadeus.com/v2/reference-data/urls/checkin-links"
AIRLINE_LOOKUP_URL = "https://test.api.amadeus.com/v1/reference-data/airlines"

# -------------------------------------------------
# OAuth
# -------------------------------------------------
async def get_access_token() -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        res.raise_for_status()
        return res.json()["access_token"]

# -------------------------------------------------
# Multi-city Search
# -------------------------------------------------
async def search_multicity_india() -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    body = {
        "currencyCode": "INR",
        "originDestinations": [
            {"id": "1", "originLocationCode": "DEL", "destinationLocationCode": "BOM", "departureDateTimeRange": {"date": "2026-10-03"}},
            {"id": "2", "originLocationCode": "BOM", "destinationLocationCode": "BLR", "departureDateTimeRange": {"date": "2026-10-05"}},
            {"id": "3", "originLocationCode": "BLR", "destinationLocationCode": "MAA", "departureDateTimeRange": {"date": "2026-10-08"}},
            {"id": "4", "originLocationCode": "MAA", "destinationLocationCode": "DEL", "departureDateTimeRange": {"date": "2026-10-11"}},
        ],
        "travelers": [{"id": "1", "travelerType": "ADULT"}],
        "sources": ["GDS"],
        "searchCriteria": {"maxFlightOffers": 5},
    }

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(FLIGHT_OFFERS_URL, headers=headers, json=body)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Pricing
# -------------------------------------------------
async def price_flight_offer(flight_offer: dict) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    body = {"data": {"type": "flight-offers-pricing", "flightOffers": [flight_offer]}}

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(FLIGHT_PRICING_URL, headers=headers, json=body)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Seatmaps
# -------------------------------------------------
async def get_seatmap_from_flight_offer(flight_offer: dict) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(SEATMAP_URL, headers=headers, json={"data": [flight_offer]})
        res.raise_for_status()
        return res.json()

async def get_seatmap_from_order(order_id: str) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(f"{SEATMAP_URL}?flightOrderId={order_id}", headers=headers)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Flight Orders
# -------------------------------------------------
async def create_flight_order(priced_flight_offer: dict) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    body = {
        "data": {
            "type": "flight-order",
            "flightOffers": [priced_flight_offer],
            "travelers": [{
                "id": "1",
                "dateOfBirth": "1990-01-01",
                "name": {"firstName": "Test", "lastName": "User"},
                "gender": "MALE",
                "contact": {
                    "emailAddress": "test@example.com",
                    "phones": [{"deviceType": "MOBILE", "countryCallingCode": "91", "number": "9999999999"}],
                },
            }],
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(FLIGHT_ORDER_URL, headers=headers, json=body)
        res.raise_for_status()
        return res.json()

async def retrieve_flight_order(order_id: str) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(f"{FLIGHT_ORDER_URL}/{order_id}", headers=headers)
        res.raise_for_status()
        return res.json()

async def cancel_flight_order(order_id: str) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.delete(f"{FLIGHT_ORDER_URL}/{order_id}", headers=headers)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Inspiration / Cheapest Dates / Availability
# -------------------------------------------------
async def get_flight_inspiration(origin: str, max_price: int = 10000, currency: str = "INR") -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"origin": origin, "maxPrice": max_price, "currency": currency}
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(FLIGHT_INSPIRATION_URL, headers=headers, params=params)
        res.raise_for_status()
        return res.json()

async def get_cheapest_flight_dates(origin: str, destination: str, currency: str = "INR") -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"origin": origin, "destination": destination, "currency": currency}
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(CHEAPEST_DATE_URL, headers=headers, params=params)
        res.raise_for_status()
        return res.json()

async def get_flight_availability(origin: str, destination: str, departure_date: str) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    body = {
        "originDestinations": [{
            "id": "1",
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDateTime": {"date": departure_date},
        }],
        "travelers": [{"id": "1", "travelerType": "ADULT"}],
        "sources": ["GDS"],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.post(AVAILABILITY_URL, headers=headers, json=body)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Flight Status
# -------------------------------------------------
async def get_flight_status(carrier_code: str, flight_number: str, departure_date: str) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "carrierCode": carrier_code,
        "flightNumber": flight_number,
        "scheduledDepartureDate": departure_date,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(FLIGHT_STATUS_URL, headers=headers, params=params)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Check-in Links
# -------------------------------------------------
async def get_flight_checkin_links(airline_code: str, language: str = "EN") -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"airlineCode": airline_code, "language": language}
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(CHECKIN_LINKS_URL, headers=headers, params=params)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Airline Code Lookup
# -------------------------------------------------
async def get_airline_name(airline_codes: List[str]) -> dict:
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"airlineCodes": ",".join(airline_codes)}
    async with httpx.AsyncClient(timeout=30) as client:
        res = await client.get(AIRLINE_LOOKUP_URL, headers=headers, params=params)
        res.raise_for_status()
        return res.json()

# -------------------------------------------------
# Airline Routes (Destinations served by airline)
# -------------------------------------------------
AIRLINE_ROUTES_URL = "https://test.api.amadeus.com/v1/airline/destinations"

async def get_airline_routes(airline_code: str) -> dict:
    """
    Returns all destinations served by a given airline.
    Example: airline_code = 'EK'
    """
    token = await get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"airlineCode": airline_code}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            AIRLINE_ROUTES_URL,
            headers=headers,
            params=params,
        )
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------
# Tours & Activities (Amadeus Discover)
# ---------------------------------------------------------

ACTIVITIES_URL = "https://test.api.amadeus.com/v1/shopping/activities"


async def search_activities(
    latitude: float,
    longitude: float,
    radius: int = 5
):
    """
    Search tours & activities around a point
    """
    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            ACTIVITIES_URL,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()


async def search_activities_by_square(
    north: float,
    south: float,
    east: float,
    west: float
):
    """
    Search tours & activities inside a square area
    """
    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "north": north,
        "south": south,
        "east": east,
        "west": west
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{ACTIVITIES_URL}/by-square",
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()


async def get_activity_by_id(activity_id: str):
    """
    Retrieve one activity by ID
    """
    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{ACTIVITIES_URL}/{activity_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

# ---------------------------------------------------------
# City Search
# ---------------------------------------------------------

CITY_SEARCH_URL = "https://test.api.amadeus.com/v1/reference-data/locations/cities"


async def search_cities(keyword: str, max_results: int = 10):
    """
    Search cities by keyword (autocomplete)
    """
    token = await get_access_token()

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "keyword": keyword,
        "max": max_results
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            CITY_SEARCH_URL,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
