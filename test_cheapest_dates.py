import asyncio
import json
from amadeus import get_cheapest_flight_dates


async def main():
    print("📅 Cheapest Date Search Test\n")

    # Sandbox-friendly route
    origin = "DXB"
    destination = "LHR"
    currency = "EUR"

    print(
        f"Searching cheapest dates from {origin} to {destination} "
        f"in {currency}\n"
    )

    response = await get_cheapest_flight_dates(
        origin=origin,
        destination=destination,
        currency=currency
    )

    print("📦 Raw API Response:")
    print(json.dumps(response, indent=2))

    data = response.get("data", [])

    if not data:
        print("\n⚠️ No cheapest dates returned (normal in sandbox)")
        return

    print("\n💸 Cheapest flight dates:")
    for item in data[:10]:
        print(
            f"Departure: {item.get('departureDate')} | "
            f"Return: {item.get('returnDate')} | "
            f"Price: {item.get('price', {}).get('total')} "
            f"{item.get('price', {}).get('currency')}"
        )


if __name__ == "__main__":
    asyncio.run(main())
