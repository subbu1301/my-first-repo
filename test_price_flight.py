import asyncio
import json
from amadeus import search_multicity_india, price_flight_offer


async def main():
    print(" Searching flights first...\n")

    search_response = await search_multicity_india()
    offers = search_response.get("data", [])

    if not offers:
        print(" No flight offers found (sandbox limitation).")
        return

    flight_offer = offers[0]

    print(" Flight offer selected")
    print(f"Offer ID: {flight_offer.get('id')}")
    print(
        f"Initial Price: "
        f"{flight_offer['price']['grandTotal']} "
        f"{flight_offer['price']['currency']}"
    )

    print("\n Pricing the selected flight...\n")

    try:
        pricing_response = await price_flight_offer(flight_offer)

        print(" Raw pricing response:")
        print(json.dumps(pricing_response, indent=2))

        priced_offer = pricing_response["data"]["flightOffers"][0]

        print("\n FINAL PRICED RESULT")
        print(f"Currency: {priced_offer['price']['currency']}")
        print(f"Total Price: {priced_offer['price']['grandTotal']}")
        print(f"Base Price: {priced_offer['price']['base']}")
        print(f"Last Ticketing Date: {priced_offer.get('lastTicketingDate')}")
        print(f"Bookable Seats: {priced_offer.get('numberOfBookableSeats')}")

    except Exception as e:
        print(" Pricing failed (this is NORMAL in sandbox)")
        print(str(e))


if __name__ == "__main__":
    asyncio.run(main())
