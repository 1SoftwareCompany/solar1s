"""Coordinator to fetch and manage electricity price data."""

from datetime import datetime, timedelta, timezone
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.storage import Store
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util.dt import parse_datetime
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
            name="electricity_prices",
            update_interval=timedelta(minutes=5),
        )

        self._last_success: datetime | None = None  # Track the last successful update time
        self._store = Store(hass, 1, "custom_energy_price_cache.json")  # Persistent storage
        self._previous_data: dict | None = None  # Cache for the last successful data

        # Schedule the daily test email at 15:00
        async_track_time_change(
            hass,
            self._send_daily_email,
            hour=15,
            minute=0,
            second=0,
        )

    async def _send_daily_email(self, now: datetime) -> None:
        """Send a test email every day at the scheduled time."""
        _LOGGER.info("Sending daily email")

        try:
            await self.hass.services.async_call(
                "notify",
                "email",
                {
                    "title": "Daily Mail From Solaris",
                    "message": "This is your test message sent automatically every afternoon.",
                },
                blocking=True,
            )
            _LOGGER.info("Test email sent successfully")
        except Exception as e:
            _LOGGER.error("Failed to send test email: %s", e)

    async def _async_update_data(self) -> dict:
        """Fetch data from the API and handle errors."""
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
                        self._last_success = datetime.now(timezone.utc)  # Update with timezone-aware datetime
                        await self._store_data(data)  # Save the data to persistent storage
                        self._previous_data = data  # Cache the data in memory
                        return data
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            if self._previous_data:
                _LOGGER.debug("Using cached data due to API failure")
                return self._previous_data  # Use cached data if available
            raise UpdateFailed("No data available and API request failed") from err

    async def _store_data(self, data: dict) -> None:
        """Store data persistently."""
        await self._store.async_save(data)

    async def _load_data(self) -> dict | None:
        """Load data from persistent storage."""
        return await self._store.async_load()

    async def async_config_entry_first_refresh(self) -> None:
        """Load cached data on startup before the first refresh."""
        cached_data = await self._load_data()
        if cached_data:
            _LOGGER.debug("Loaded cached data on startup")
            self._previous_data = cached_data

    @property
    def last_success_time(self) -> datetime | None:
        """Return the datetime of the last successful update."""
        return self._last_success