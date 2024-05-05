"""Munich public transport (MVG) integration."""

from __future__ import annotations

import logging
from typing import Optional

import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from mvg import MvgApi, MvgApiError

from .const import (
    CONF_DEPARTURE_STATION_ID,
    CONF_DEPARTURES,
    CONF_DEPARTURES_LINES,
    CONF_DEPARTURES_WALKING_TIME,
    CONF_DESTINATION_STATION_ID,
    CONF_TRIP_NAME,
    CONF_TYPE_BUS,
    CONF_TYPE_SUBURBAN,
    CONF_TYPE_SUBWAY,
    CONF_TYPE_TRAM,
    DEFAULT_ICON,
    DOMAIN,  # noqa
    SCAN_INTERVAL,  # noqa
)
from .departure import Departure

_LOGGER = logging.getLogger(__name__)

TRANSPORT_TYPES_SCHEMA = {
    vol.Optional(CONF_TYPE_SUBURBAN, default=True): bool,
    vol.Optional(CONF_TYPE_SUBWAY, default=True): bool,
    vol.Optional(CONF_TYPE_TRAM, default=True): bool,
    vol.Optional(CONF_TYPE_BUS, default=True): bool,
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_DEPARTURES): [
            {
                vol.Required(CONF_TRIP_NAME): str,
                vol.Required(CONF_DEPARTURE_STATION_ID): str,
                vol.Required(CONF_DESTINATION_STATION_ID): str,
                vol.Optional(CONF_DEPARTURES_WALKING_TIME, default=1): int,
                vol.Optional(CONF_DEPARTURES_LINES, default=[]): [str],
                **TRANSPORT_TYPES_SCHEMA,
            }
        ]
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    _: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    if CONF_DEPARTURES in config:
        for departure in config[CONF_DEPARTURES]:
            add_entities([TransportSensor(hass, departure)])


class TransportSensor(SensorEntity):
    departures: list[Departure] = []

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        self.hass: HomeAssistant = hass
        self.config: dict = config
        self.trip_name: str = config.get(CONF_TRIP_NAME)
        self.departure_station: str = config.get(CONF_DEPARTURE_STATION_ID)
        self.destination_station: str = config.get(CONF_DESTINATION_STATION_ID)
        # we add +1 minute anyway to delete the "just gone" transport
        self.walking_time: int = config.get(CONF_DEPARTURES_WALKING_TIME) or 1
        # If configured allow only the specified line, else allow all lines
        self.lines: str = config.get(CONF_DEPARTURES_LINES) or []

    @property
    def name(self) -> str:
        return self.trip_name

    @property
    def icon(self) -> str:
        next_departure = self.next_departure()
        if next_departure:
            return next_departure.icon
        return DEFAULT_ICON

    @property
    def unique_id(self) -> str:
        return f"stop_{self.trip_name}_departures"

    @property
    def state(self) -> str:
        next_departure = self.next_departure()
        if next_departure:
            return f"Next {next_departure.line_name}, {next_departure.destination_station} in {next_departure.human_departure_in_minutes}"
        return "N/A"

    @property
    def extra_state_attributes(self):
        return {
            "departures": [departure.to_dict() for departure in self.departures or []]
        }

    def update(self):
        self.departures = self.fetch_departures()

    def fetch_departures(self) -> Optional[list[Departure]]:
        try:
            departures = MvgApi.connection(
                origin_station_id=self.departure_station,
                destination_station_id=self.destination_station,
                offset=self.walking_time,
            )
        except MvgApiError as e:
            _LOGGER.error(
                f"Could not determine departures for trip '{self.trip_name}': {e}"
            )
            return None

        _LOGGER.debug(f"OK: departures for {self.trip_name}: {departures}")

        # Convert API data into objects
        unsorted = [Departure.from_dict(departure) for departure in departures]

        # Filter departures based on line and direction
        filtered_departures = []
        for departure in unsorted:
            if not self.lines or departure.line_name in self.lines:
                filtered_departures.append(departure)

        return sorted(filtered_departures, key=lambda d: d.departure_in_minutes)

    def next_departure(self):
        if self.departures and isinstance(self.departures, list):
            return self.departures[0]
        return None


# run in docker: 
# export PYTHONPATH=/config/custom_components/; 
# python3 -i -m munich_transport_trip.sensor
# _LOGGER.setLevel(logging.DEBUG)
if __name__ == "__main__":
    testconfig = {
        CONF_TRIP_NAME: "Test",
        CONF_DEPARTURE_STATION_ID: "Pasing",
        CONF_DESTINATION_STATION_ID: "Ostbahnhof",
        CONF_DEPARTURES_WALKING_TIME: 1,
    }
    sensor = TransportSensor(None, testconfig)
    print(f"{sensor.name}")
    print(sensor.fetch_departures())
