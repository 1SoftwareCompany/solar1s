"""Coordinator to fetch and manage electricity price data."""

from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util  # Correctly import dt_util for date and time utilities
import aiohttp
import async_timeout
import logging

_LOGGER = logging.getLogger(__name__)

API_URL = "http://10.1.1.85:9200/metrics-ibex/_search"
USERNAME = "elastic"
PASSWORD = "123qwe123qwe##asd"


class IbexCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch and manage electricity price data."""

    def __init__(self, hass: HomeAssistant):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Solaris Coordinator",
            update_interval=timedelta(minutes=5),
        )
        self._last_success = None

    async def _async_update_data(self) -> dict:
        """Fetch data from the API."""
        payload = {
            "size": 48,
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "now/d",
                        "lte": "now+1d/d",
                        "time_zone": "+03:00",
                    }
                }
            },
            "sort": [{"@timestamp": {"order": "asc"}}],
        }
        headers = {"Content-Type": "application/json"}

        try:
            _LOGGER.debug("Sending request to API with payload: %s", payload)
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        API_URL,
                        json=payload,
                        headers=headers,
                        auth=aiohttp.BasicAuth(USERNAME, PASSWORD),
                    ) as response:
                        if response.status != 200:
                            raise UpdateFailed(f"HTTP error: {response.status}")
                        data = await response.json()
                        _LOGGER.debug("Received data from API: %s", data)
                        self._last_success = dt_util.utcnow()  # Use dt_util for the current UTC time
                        return data
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    @property
    def last_success_time(self):
        """Return the last successful update time."""
        return self._last_success