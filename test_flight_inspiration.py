import asyncio
import json
from amadeus import get_flight_inspiration


async def main():
    print(" Flight Inspiration Search Test\n")

    origin = "DXB"
    max_price = 700
    currency = "EUR"

    print(
        f"Searching destinations from {origin} "
        f"under {max_price} {currency}\n"
    )

    #  Call matches function signature
    response = await get_flight_inspiration(
        origin,
        max_price,
        currency
    )

    print(" Raw API Response:")
    print(json.dumps(response, indent=2))

    data = response.get("data", [])

    if not data:
        print("\n No destinations returned (normal in sandbox)")
        return

    print("\n Cheapest destinations:")
    for item in data[:10]:
        print(
            f"{item.get('destination')} | "
            f"{item.get('price', {}).get('total')} "
            f"{item.get('price', {}).get('currency')}"
        )


if __name__ == "__main__":
    asyncio.run(main())
