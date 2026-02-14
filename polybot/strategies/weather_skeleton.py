"""Weather Mispricing Strategy -- SKELETON / FUTURE PLUGIN.

Concept:
- Integrate with NOAA (or similar) weather data APIs.
- Identify Polymarket weather-related prediction markets.
- Compare implied probability (market price) vs data-derived probability.
- If mispricing exceeds a threshold, place a directional bet.

Data sources (ideas):
- NOAA API: https://www.weather.gov/documentation/services-web-api
- Open-Meteo: https://open-meteo.com/

Risks:
- Weather forecasts are probabilistic; even the best models have
  uncertainty.
- Market may already reflect the same data (efficient market hypothesis).
- Liquidity may be thin on weather markets.

This file provides the interface scaffolding only.
"""

from __future__ import annotations

import logging

from polybot.strategies.base import BaseStrategy, ExecutionResult, Opportunity

logger = logging.getLogger(__name__)


class WeatherStrategy(BaseStrategy):
    """Data-driven weather mispricing. NOT YET IMPLEMENTED."""

    name = "weather"

    def scan(self, limit: int = 20) -> list[Opportunity]:
        """Placeholder: would fetch weather data and compare to market prices."""
        raise NotImplementedError(
            "WeatherStrategy is a skeleton for future development. "
            "See weather_skeleton.py for design notes."
        )

    def execute(self, opportunity: Opportunity) -> ExecutionResult:
        """Placeholder."""
        raise NotImplementedError("WeatherStrategy.execute not implemented.")
