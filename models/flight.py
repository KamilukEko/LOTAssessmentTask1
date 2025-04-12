from models.checkpoint import Checkpoint


class Flight:
    def __init__(self, flight_number: str, aircraft: str, status: str, origin: Checkpoint, destination: Checkpoint):
        self.flight_number = flight_number
        self.status = status
        self.aircraft = aircraft
        self.origin = origin
        self.destination = destination
