import xml.etree.ElementTree as ET
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from models import Flight, Checkpoint

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlightParser:
    @staticmethod
    def validate_flight_number(flight_number: str) -> bool:
        pattern = r'^[A-Za-z]+[0-9]+$'
        return bool(re.match(pattern, flight_number))

    @staticmethod
    def validate_airport_code(code: str) -> bool:
        pattern = r'^[A-Za-z]{4}$'
        return bool(re.match(pattern, code))

    @staticmethod
    def validate_iso_time(time_str: str) -> bool:
        try:
            datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False

    @classmethod
    def parse_checkpoint(cls, airport_elem) -> Optional[Checkpoint]:
        if airport_elem is None:
            return None

        code = airport_elem.findtext('airport')
        time = airport_elem.findtext('time')

        if code is None or time is None:
            missing_fields = []
            if code is None: missing_fields.append('airport')
            if time is None: missing_fields.append('time')

            logger.warning(f"Airport element missing required fields: {', '.join(missing_fields)}")
            return None

        if not cls.validate_airport_code(code):
            logger.warning(f"Invalid airport code: {code}")
            return None

        if not cls.validate_iso_time(time):
            logger.warning(f"Invalid time format: {time}")
            return None

        return Checkpoint(code=code, time=time)

    @classmethod
    def parse_xml(cls, xml_file_path: str) -> List[Flight]:
        path = Path(xml_file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {xml_file_path}")

        flights = []
        try:
            tree = ET.parse(path)
            root = tree.getroot()

            for flight_elem in root.findall('.//flight'):
                try:
                    number = flight_elem.findtext('number')
                    aircraft = flight_elem.findtext('aircraft')

                    departure_elem = flight_elem.find('departure')
                    origin = cls.parse_checkpoint(departure_elem)

                    arrival_elem = flight_elem.find('arrival')
                    destination = cls.parse_checkpoint(arrival_elem)

                    status = flight_elem.findtext('status')

                    if number is None:
                        logger.warning("Flight element missing flight number")
                        continue

                    if origin is None or destination is None:
                        logger.warning(f"Failed to parse origin or destination for flight {number}")
                        continue

                    if not cls.validate_flight_number(number):
                        logger.warning(f"Invalid flight number format: {number}")
                        continue

                    if status is None:
                        logger.warning("Flight element missing status")
                        continue

                    flights.append(Flight(
                        flight_number=number,
                        aircraft=aircraft,
                        status=status,
                        origin=origin,
                        destination=destination
                    ))

                except Exception as e:
                    logger.error(f"Error processing flight element: {e}")

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        return flights

    @classmethod
    def filter_by_status(cls, flights: List[Flight], status: str) -> List[Flight]:
        return [flight for flight in flights if flight.status == status]