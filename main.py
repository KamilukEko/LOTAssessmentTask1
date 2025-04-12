import argparse

from services import FlightParser

def cli():
    parser = argparse.ArgumentParser(description="Flight Parser CLI")
    parser.add_argument('file', help='Path to the file')
    parser.add_argument("--status", nargs=1, metavar='STATUS', help="Status code to filter by")

    args = parser.parse_args()

    try:
        flights = FlightParser.parse_xml(args.file)
        header = f"Found {len(flights)} valid flights:"

        if args.status:
            flights = FlightParser.filter_by_status(flights, args.status[0])
            header = f"Found {len(flights)} valid flights with status {args.status[0]}:"

        print(header + "\n")
        for flight in flights:
            print(f"Flight {flight.flight_number}, Status: {flight.status}, Aircraft: {flight.aircraft}")
            print(f"  Departure: {flight.origin.code} at {flight.origin.time}")
            print(f"  Arrival: {flight.destination.code} at {flight.destination.time}")
            print("\n")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    cli()