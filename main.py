from services import FlightParser

if __name__ == "__main__":
    flights = FlightParser.parse_xml("flights.xml")

    print(f"Found {len(flights)} valid flights:")
    for flight in flights:
        print(f"Flight {flight.flight_number}, Status: {flight.status}, Aircraft: {flight.aircraft}")
        print(f"  Departure: {flight.origin.code} at {flight.origin.time}")
        print(f"  Arrival: {flight.destination.code} at {flight.destination.time}")
        print()
