from dataclasses import dataclass
from datetime import datetime

from .const import DEFAULT_ICON, TRANSPORT_TYPE_VISUALS

"""     
example input:
[  {'departureDelayInMinutes': 0,
    'departureInMinutes': 8,
    'departurePlanned': '2024-05-05T13:11:00+02:00',
    'departureReal': '2024-05-05T13:11+02:00',
    'departureStation': 'Pasing',
    'destinationDelayInMinutes': 0,
    'destinationPlanned': '2024-05-05T13:23:00+02:00',
    'destinationStation': 'München, Ostbahnhof',
    'icon': 'mdi:subway-variant',
    'line': 'S8',
    'messages': [],
    'type': 'S-Bahn',
    }, ... ]
"""

@dataclass
class Departure:
    """Departure dataclass to store data from API"""

    departure_station: str
    destination_station: str
    line_name: str
    line_type: str
    departure_planned: datetime
    departure_real: datetime
    departure_delay_in_minutes: int
    destination_delay_in_minutes: int
    destination_planned: datetime
    destination_real: datetime
    departure_in_minutes: int
    human_departure_in_minutes: str
    icon: str | None = None
    bg_color: str | None = None

    @classmethod
    def from_dict(cls, source):
        line_visuals = TRANSPORT_TYPE_VISUALS.get(source['type']) or { "code": "ANY", "icon": DEFAULT_ICON, "color": "#666518"}
        return cls(
            departure_station=source['departureStation'],
            destination_station=source['destinationStation'],
            line_name=source['line'],
            line_type=source['type'],
            departure_planned=datetime.fromisoformat(source['departurePlanned']),
            departure_real=datetime.fromisoformat(source['departureReal']),
            departure_delay_in_minutes=source['departureDelayInMinutes'], 
            destination_delay_in_minutes=source['destinationDelayInMinutes'],
            destination_planned=datetime.fromisoformat(source['destinationPlanned']),
            destination_real=datetime.fromisoformat(source['destinationReal']),
            departure_in_minutes=source['departureInMinutes'],
            human_departure_in_minutes=f'{source['departureInMinutes']}' + (f'+{source['departureDelayInMinutes']}' if source['departureDelayInMinutes'] >0 else '') + ' min',
            icon=line_visuals.get("icon"),
            bg_color=line_visuals.get("color"),
        )

    def to_dict(self):
        return {
            "line_name": self.line_name,
            "line_type": self.line_type,
            "departure_station": self.departure_station,
            "destination_station": self.destination_station,
            "human_departure_in_minutes": self.human_departure_in_minutes,
            "departure_real": self.departure_real.astimezone().time(),
            "destination_real": self.destination_real.astimezone().time(),
            "color": self.bg_color,
        }
