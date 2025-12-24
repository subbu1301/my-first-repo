import os
import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

BASE_V1 = "https://test.api.amadeus.com/v1"
BASE_V2 = "https://test.api.amadeus.com/v2"
BASE_V3 = "https://test.api.amadeus.com/v3"

mcp: FastMCP = FastMCP("Amadeus Hotels MCP")

# -----------------------
# AUTH
# -----------------------
async def get_token():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": os.getenv("AMADEUS_CLIENT_ID"),
                "client_secret": os.getenv("AMADEUS_CLIENT_SECRET"),
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        return r.json()["access_token"]


# =======================
# HOTEL LIST APIs
# =======================
async def hotels_by_city(city_code: str):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"cityCode": city_code}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/reference-data/locations/hotels/by-city",
            headers=headers,
            params=params,
        )
        return r.json()


async def hotels_by_geocode(latitude: float, longitude: float):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"latitude": latitude, "longitude": longitude}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/reference-data/locations/hotels/by-geocode",
            headers=headers,
            params=params,
        )
        return r.json()


async def hotels_by_ids(hotel_ids: str):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"hotelIds": hotel_ids}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/reference-data/locations/hotels/by-hotels",
            headers=headers,
            params=params,
        )
        return r.json()


# =======================
# HOTEL SEARCH APIs
# =======================
async def hotel_offers(city_code: str):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"cityCode": city_code}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V3}/shopping/hotel-offers",
            headers=headers,
            params=params,
        )
        return r.json()


async def hotel_offer_pricing(offer_id: str):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V3}/shopping/hotel-offers/{offer_id}",
            headers=headers,
        )
        return r.json()


# =======================
# HOTEL BOOKING
# =======================
async def book_hotel(offer_id: str, guest_first_name: str, guest_last_name: str):
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    body = {
        "data": {
            "offerId": offer_id,
            "guests": [
                {
                    "name": {
                        "firstName": guest_first_name,
                        "lastName": guest_last_name,
                    }
                }
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_V2}/booking/hotel-orders",
            headers=headers,
            json=body,
        )
        return r.json()


# =======================
# HOTEL RATINGS
# =======================
async def hotel_ratings(hotel_ids: str):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"hotelIds": hotel_ids}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V2}/e-reputation/hotel-sentiments",
            headers=headers,
            params=params,
        )
        return r.json()


# =======================
# HOTEL NAME AUTOCOMPLETE
# =======================
async def hotel_name_autocomplete(keyword: str):
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"keyword": keyword}

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/reference-data/locations/hotel",
            headers=headers,
            params=params,
        )
        return r.json()

# =======================
# CARS & TRANSFERS APIs
# =======================

# Transfer Search (Get transfer offers)
async def transfer_search(
    start_latitude: float,
    start_longitude: float,
    end_latitude: float,
    end_longitude: float
):
    """
    Search transfer offers between two locations
    """
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "startLocationCode": f"{start_latitude},{start_longitude}",
        "endLocationCode": f"{end_latitude},{end_longitude}",
        "transferType": "PRIVATE"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_V1}/shopping/transfer-offers",
            headers=headers,
            json=body
        )
        return r.json()


# Transfer Booking (Create transfer order)
async def transfer_booking(
    offer_id: str,
    first_name: str,
    last_name: str,
    email: str
):
    """
    Book a transfer using an offerId
    """
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "data": {
            "offerId": offer_id,
            "passengers": [
                {
                    "firstName": first_name,
                    "lastName": last_name,
                    "contacts": {
                        "email": email
                    }
                }
            ]
        }
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_V1}/ordering/transfer-orders",
            headers=headers,
            json=body
        )
        return r.json()


# Transfer Management (Cancel transfer)
async def cancel_transfer(
    order_id: str,
    transfer_id: str
):
    """
    Cancel a transfer in an existing order
    """
    token = await get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BASE_V1}/ordering/transfer-orders/{order_id}/transfers/{transfer_id}/cancellation",
            headers=headers
        )
        return r.json()

# =======================
# MARKET INSIGHTS APIs
# =======================

# Flight Most Traveled Destinations
async def flight_most_traveled_destinations(origin_city_code: str, period: str = "2023-01"):
    """
    Returns the most traveled destinations from a city
    """
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originCityCode": origin_city_code,
        "period": period
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/travel/analytics/air-traffic/traveled",
            headers=headers,
            params=params
        )
        return r.json()


# Flight Most Booked Destinations
async def flight_most_booked_destinations(origin_city_code: str, period: str = "2023-01"):
    """
    Returns the most booked destinations from a city
    """
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originCityCode": origin_city_code,
        "period": period
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/travel/analytics/air-traffic/booked",
            headers=headers,
            params=params
        )
        return r.json()


# Flight Busiest Traveling Period
async def flight_busiest_traveling_period(origin_city_code: str, destination_city_code: str):
    """
    Returns busiest traveling period between two cities
    """
    token = await get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originCityCode": origin_city_code,
        "destinationCityCode": destination_city_code
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BASE_V1}/travel/analytics/air-traffic/busiest-period",
            headers=headers,
            params=params
        )
        return r.json()


# =======================
# REGISTER ALL TOOLS
# =======================
mcp.tool(hotels_by_city)
mcp.tool(hotels_by_geocode)
mcp.tool(hotels_by_ids)

mcp.tool(hotel_offers)
mcp.tool(hotel_offer_pricing)

mcp.tool(book_hotel)

mcp.tool(hotel_ratings)

mcp.tool(hotel_name_autocomplete)

mcp.tool(transfer_search)
mcp.tool(transfer_booking)
mcp.tool(cancel_transfer)

mcp.tool(flight_most_traveled_destinations)
mcp.tool(flight_most_booked_destinations)
mcp.tool(flight_busiest_traveling_period)

if __name__ == "__main__":
    mcp.run()
