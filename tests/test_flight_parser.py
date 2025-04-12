import pytest
from models.flight import Flight
from models.checkpoint import Checkpoint
from services import FlightParser


@pytest.fixture
def sample_xml(tmp_path):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <flights>
        <flight>
            <number>LH456</number>
            <aircraft>A320</aircraft>
            <departure>
                <airport>EDDF</airport>
                <time>2025-04-05T09:30:00Z</time>
            </departure>
            <arrival>
                <airport>LFPG</airport>
                <time>2025-04-05T11:10:00Z</time>
            </arrival>
            <status>delayed</status>
        </flight>
        <flight>
            <number>AF789</number>
            <aircraft>A319</aircraft>
            <departure>
                <airport>LFPG</airport>
                <time>2025-04-05T14:45:00Z</time>
            </departure>
            <arrival>
                <airport>LEMD</airport>
                <time>2025-04-05T17:00:00Z</time>
            </arrival>
            <status>scheduled</status>
        </flight>
    </flights>'''
    xml_file = tmp_path / "test_flights.xml"
    xml_file.write_text(xml_content)
    return str(xml_file)

@pytest.fixture
def xml_missing_status(tmp_path):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <flights>
        <flight>
            <number>LH456</number>
            <aircraft>A320</aircraft>
            <departure>
                <airport>EDDF</airport>
                <time>2025-04-05T09:30:00Z</time>
            </departure>
            <arrival>
                <airport>LFPG</airport>
                <time>2025-04-05T11:10:00Z</time>
            </arrival>
        </flight>
        <flight>
            <number>AF789</number>
            <aircraft>A319</aircraft>
            <departure>
                <airport>LFPG</airport>
                <time>2025-04-05T14:45:00Z</time>
            </departure>
            <arrival>
                <airport>LEMD</airport>
                <time>2025-04-05T17:00:00Z</time>
            </arrival>
            <status>scheduled</status>
        </flight>
    </flights>'''
    xml_file = tmp_path / "test_flights_no_status.xml"
    xml_file.write_text(xml_content)
    return str(xml_file)

@pytest.fixture
def xml_invalid_airport_code(tmp_path):
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <flights>
        <flight>
            <number>LH456</number>
            <aircraft>A320</aircraft>
            <departure>
                <airport>ED1F</airport>
                <time>2025-04-05T09:30:00Z</time>
            </departure>
            <arrival>
                <airport>LPG</airport>
                <time>2025-04-05T11:10:00Z</time>
            </arrival>
            <status>delayed</status>
        </flight>
    </flights>'''
    xml_file = tmp_path / "test_flights_invalid_status.xml"
    xml_file.write_text(xml_content)
    return str(xml_file)

def test_parse_xml_missing_status(xml_missing_status, caplog):
    flights = FlightParser.parse_xml(xml_missing_status)
    assert len(flights) == 1
    assert "Flight element missing status" in caplog.text

def test_parse_xml_airport_code(xml_invalid_airport_code):
    flights = FlightParser.parse_xml(xml_invalid_airport_code)
    assert len(flights) == 0

def test_parse_xml_valid_file(sample_xml):
    flights = FlightParser.parse_xml(sample_xml)
    assert len(flights) == 2

    assert flights[0].flight_number == "LH456"
    assert flights[0].aircraft == "A320"
    assert flights[0].status == "delayed"
    assert flights[0].origin.code == "EDDF"
    assert flights[0].origin.time == "2025-04-05T09:30:00Z"
    assert flights[0].destination.code == "LFPG"
    assert flights[0].destination.time == "2025-04-05T11:10:00Z"

    assert flights[1].flight_number == "AF789"
    assert flights[1].aircraft == "A319"
    assert flights[1].status == "scheduled"
    assert flights[1].origin.code == "LFPG"
    assert flights[1].origin.time == "2025-04-05T14:45:00Z"
    assert flights[1].destination.code == "LEMD"
    assert flights[1].destination.time == "2025-04-05T17:00:00Z"


def test_filter_by_status():
    flights = [
        Flight("FL123", "Boeing 737", "delayed",
               Checkpoint("LAX", "2024-02-20T10:00:00"),
               Checkpoint("JFK", "2024-02-20T18:00:00")),
        Flight("FL456", "Airbus A320", "on-time",
               Checkpoint("SFO", "2024-02-20T11:00:00"),
               Checkpoint("ORD", "2024-02-20T17:00:00"))
    ]
    filtered = FlightParser.filter_by_status(flights, "delayed")
    assert len(filtered) == 1
    assert filtered[0].flight_number == "FL123"


def test_parse_xml_invalid_file():
    with pytest.raises(Exception):
        FlightParser.parse_xml("nonexistent.xml")


def test_flight_creation():
    origin = Checkpoint("LAX", "2024-02-20T10:00:00")
    destination = Checkpoint("JFK", "2024-02-20T18:00:00")
    flight = Flight("FL123", "Boeing 737", "delayed", origin, destination)

    assert flight.flight_number == "FL123"
    assert flight.aircraft == "Boeing 737"
    assert flight.status == "delayed"
    assert flight.origin.code == "LAX"
    assert flight.origin.time == "2024-02-20T10:00:00"
    assert flight.destination.code == "JFK"
    assert flight.destination.time == "2024-02-20T18:00:00"