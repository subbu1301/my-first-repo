from fastmcp import FastMCP
from amadeus import (
    search_multicity_india,
    price_flight_offer,
    get_seatmap_from_flight_offer,
    get_seatmap_from_order,
    create_flight_order,
    retrieve_flight_order,
    cancel_flight_order,
    get_flight_inspiration,
    get_cheapest_flight_dates,
    get_flight_availability,
    get_flight_status,
    get_flight_checkin_links,
    get_airline_name,
    get_airline_routes,
    search_activities,
    search_activities_by_square,
    get_activity_by_id,
    search_cities
)


mcp = FastMCP("amadeus-flight-mcp")

# -------------------------
# Search: Multi-city India
# -------------------------
@mcp.tool()
async def search_india_multicity_flights():
    data = await search_multicity_india()
    results = []

    for offer in data.get("data", []):
        results.append({
            "summary": {
                "price": offer["price"]["grandTotal"],
                "currency": offer["price"]["currency"],
                "airlines": list({
                    seg["carrierCode"]
                    for itin in offer["itineraries"]
                    for seg in itin["segments"]
                }),
            },
            "flight_offer": offer
        })

    return results


# -------------------------
# Flight Inspiration
# -------------------------
@mcp.tool()
async def flight_inspiration_search(
    origin: str,
    max_price: int = 10000,
    currency: str = "INR",
    departure_date: str | None = None
):
    response = await get_flight_inspiration(
        origin, max_price, currency, departure_date
    )

    return [
        {
            "destination": item.get("destination"),
            "price": item.get("price", {}).get("total"),
            "currency": item.get("price", {}).get("currency"),
            "departure_date": item.get("departureDate"),
            "return_date": item.get("returnDate")
        }
        for item in response.get("data", [])
    ]


# -------------------------
# Cheapest Dates
# -------------------------
@mcp.tool()
async def flight_cheapest_date_search(
    origin: str,
    destination: str,
    currency: str = "INR"
):
    response = await get_cheapest_flight_dates(
        origin, destination, currency
    )

    return [
        {
            "departure_date": item.get("departureDate"),
            "return_date": item.get("returnDate"),
            "price": item.get("price", {}).get("total"),
            "currency": item.get("price", {}).get("currency")
        }
        for item in response.get("data", [])
    ]


# -------------------------
# Flight Availability
# -------------------------
@mcp.tool()
async def check_flight_availability(
    origin: str,
    destination: str,
    departure_date: str,
    airline: str | None = None
):
    data = await get_flight_availability(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        airline=airline
    )

    results = []

    for item in data.get("data", []):
        for segment in item.get("segments", []):
            results.append({
                "airline": segment.get("carrierCode"),
                "flight_number": segment.get("number"),
                "aircraft": segment.get("aircraft", {}).get("code"),
                "departure": segment.get("departure", {}).get("iataCode"),
                "arrival": segment.get("arrival", {}).get("iataCode"),
                "cabin": segment.get("cabin"),
                "fare_class": segment.get("class"),
                "seats_available": segment.get("availability", {}).get("seats")
            })

    return results


# -------------------------
# Pricing
# -------------------------
@mcp.tool()
async def price_selected_flight(flight_offer: dict):
    pricing = await price_flight_offer(flight_offer)
    priced = pricing["data"]["flightOffers"][0]

    return {
        "priced_flight_offer": priced,
        "currency": priced["price"]["currency"],
        "total_price": priced["price"]["grandTotal"],
        "base_price": priced["price"]["base"],
        "last_ticketing_date": priced.get("lastTicketingDate"),
        "bookable_seats": priced.get("numberOfBookableSeats"),
    }


# -------------------------
# SeatMap (pre-booking)
# -------------------------
@mcp.tool()
async def show_seatmap_for_flight(flight_offer: dict):
    response = await get_seatmap_from_flight_offer(flight_offer)
    return response.get("data", [])


# -------------------------
# Booking
# -------------------------
@mcp.tool()
async def create_flight_booking(priced_flight_offer: dict):
    order = (await create_flight_order(priced_flight_offer))["data"]
    records = order.get("associatedRecords", [])
    pnr = records[0]["reference"] if records else None

    return {
        "order_id": order.get("id"),
        "status": order.get("status"),
        "pnr": pnr,
    }


# -------------------------
# Retrieve Booking
# -------------------------
@mcp.tool()
async def retrieve_flight_booking(order_id: str):
    order = (await retrieve_flight_order(order_id))["data"]
    records = order.get("associatedRecords", [])
    pnr = records[0]["reference"] if records else None

    return {
        "order_id": order.get("id"),
        "status": order.get("status"),
        "pnr": pnr,
        "travelers": order.get("travelers"),
    }


# -------------------------
# SeatMap (post-booking)
# -------------------------
@mcp.tool()
async def show_seatmap_for_booking(order_id: str):
    return (await get_seatmap_from_order(order_id)).get("data", [])


# -------------------------
# Cancel Booking
# -------------------------
@mcp.tool()
async def cancel_flight_booking(order_id: str):
    order = (await cancel_flight_order(order_id))["data"]
    return {
        "order_id": order.get("id"),
        "status": order.get("status")
    }

# -------------------------------
# Flight Status
# -------------------------------

@mcp.tool()
async def flight_status(
    carrier_code: str,
    flight_number: str,
    departure_date: str
):
    """
    Get real-time flight status.

    Example:
    carrier_code: "AI"
    flight_number: "101"
    departure_date: "2025-01-10"
    """

    data = await get_flight_status(
        carrier_code,
        flight_number,
        departure_date
    )

    results = []

    for flight in data.get("data", []):
        results.append({
            "flight": f'{flight["carrierCode"]}{flight["flightNumber"]}',
            "status": flight.get("status"),
            "departure": {
                "airport": flight["departure"]["iataCode"],
                "terminal": flight["departure"].get("terminal"),
                "gate": flight["departure"].get("gate"),
                "time": flight["departure"]["scheduledTimeLocal"]
            },
            "arrival": {
                "airport": flight["arrival"]["iataCode"],
                "terminal": flight["arrival"].get("terminal"),
                "gate": flight["arrival"].get("gate"),
                "time": flight["arrival"]["scheduledTimeLocal"]
            },
            "aircraft": flight.get("aircraft", {}).get("code")
        })

    return results

# -------------------------------------------------
# Check-in Links
# -------------------------------------------------

@mcp.tool()
async def get_airline_checkin_link(
    airline_code: str,
    language: str = "EN"
):
    """
    Get online check-in link for an airline.

    Example:
    airline_code = "AI"
    language = "EN"
    """

    data = await get_flight_checkin_links(
        airline_code=airline_code,
        language=language
    )

    results = []

    for item in data.get("data", []):
        results.append({
            "airline": item.get("airlineCode"),
            "url": item.get("url"),
            "language": item.get("language")
        })

    return results


@mcp.tool()
async def airline_code_lookup(codes: list[str]):
    """
    Get airline names from IATA or ICAO codes.
    Example: ["EK", "AI"]
    """

    data = await get_airline_name(codes)

    results = []

    for airline in data.get("data", []):
        results.append({
            "name": airline.get("businessName"),
            "iata_code": airline.get("iataCode"),
            "icao_code": airline.get("icaoCode")
        })

    return results

# -------------------------------------------------
# Airline Routes MCP Tool
# -------------------------------------------------
@mcp.tool()
async def airline_routes(airline_code: str):
    """
    Returns all destinations served by an airline.
    Example: airline_code = 'EK'
    """
    data = await get_airline_routes(airline_code)

    results = []
    for item in data.get("data", []):
        results.append({
            "city_name": item.get("name"),
            "iata_code": item.get("iataCode"),
            "country": item.get("address", {}).get("countryName"),
        })

    return {
        "airline_code": airline_code,
        "destinations": results
    }

# ---------------------------------------------------------
# Tours & Activities MCP Tools
# ---------------------------------------------------------

@mcp.tool()
async def find_activities_nearby(
    latitude: float,
    longitude: float,
    radius_km: int = 5
):
    """
    Find tours & activities near a location.
    """
    data = await search_activities(latitude, longitude, radius_km)

    results = []
    for act in data.get("data", []):
        results.append({
            "id": act.get("id"),
            "name": act.get("name"),
            "shortDescription": act.get("shortDescription"),
            "rating": act.get("rating"),
            "price": act.get("price", {}).get("amount"),
            "currency": act.get("price", {}).get("currencyCode"),
            "bookingLink": act.get("bookingLink")
        })

    return results


@mcp.tool()
async def find_activities_by_area(
    north: float,
    south: float,
    east: float,
    west: float
):
    """
    Find tours & activities inside a square area.
    """
    data = await search_activities_by_square(north, south, east, west)

    return [
        {
            "id": act.get("id"),
            "name": act.get("name"),
            "rating": act.get("rating"),
            "bookingLink": act.get("bookingLink")
        }
        for act in data.get("data", [])
    ]


@mcp.tool()
async def get_activity_details(activity_id: str):
    """
    Get full details of one activity.
    """
    data = await get_activity_by_id(activity_id)
    return data.get("data")

# ---------------------------------------------------------
# City Search MCP Tool
# ---------------------------------------------------------

@mcp.tool()
async def city_search(keyword: str):
    """
    Find cities matching a keyword (autocomplete).
    Example: "Dub" → Dubai, Dublin, etc.
    """
    data = await search_cities(keyword)

    results = []
    for city in data.get("data", []):
        results.append({
            "name": city.get("name"),
            "cityCode": city.get("iataCode"),
            "country": city.get("address", {}).get("countryName"),
            "countryCode": city.get("address", {}).get("countryCode"),
            "timezone": city.get("timeZone"),
            "latitude": city.get("geoCode", {}).get("latitude"),
            "longitude": city.get("geoCode", {}).get("longitude"),
            "nearestAirport": city.get("relatedLocations", [{}])[0].get("iataCode")
        })

    return results

if __name__ == "__main__":
    try:
        mcp.run()
    except KeyboardInterrupt:
        pass

