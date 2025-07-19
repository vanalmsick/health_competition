# myapp/monitor.py
from collections import deque
from datetime import datetime, timedelta, timezone

class RateLimitExceeded(Exception):
    """Raised when the API rate limit is exceeded."""
    pass

class APIRequestMonitor:
    """ API request rate limiter"""
    def __init__(self, limit_15min: int, limit_day: int):
        self.limit_15min = limit_15min
        self.limit_day = limit_day
        self.current_15min_slot = self._get_15min_slot()
        self.current_day = self._get_day()
        self.count_15min = 0
        self.count_day = 0

    def _get_15min_slot(self):
        now = datetime.now(timezone.utc)
        return now.replace(minute=(now.minute // 15) * 15, second=0, microsecond=0)

    def _get_day(self):
        return datetime.now(timezone.utc).date()

    def _maybe_reset_counters(self):
        now_slot = self._get_15min_slot()
        today = self._get_day()

        if now_slot != self.current_15min_slot:
            self.current_15min_slot = now_slot
            self.count_15min = 0

        if today != self.current_day:
            self.current_day = today
            self.count_day = 0

    def log_request(self, response) -> bool:
        self._maybe_reset_counters()
        self.count_day += 1

        if response.status_code == 429:
            self.count_15min = self.limit_15min
            raise RateLimitExceeded("API rate limit exceeded")

        if self.count_15min >= self.limit_15min or self.count_day >= self.limit_day:
            raise RateLimitExceeded("API rate limit probably exceeded")

        self.count_15min += 1
        print(f'Strava API Request (15min: {self.count_15min} / {self.limit_15min}, day: {self.count_day} / {self.limit_day})')
        return True

    def count_requests(self):
        self._maybe_reset_counters()
        return {
            "requests_15min": self.count_15min,
            "requests_today": self.count_day
        }

    def ok_workout_requests(self):
        stats = self.count_requests()
        return ((stats["requests_today"] <= self.limit_day * 0.8) & (stats["requests_15min"] <= self.limit_15min * 0.66))

    def ok_linkage_requests(self):
        stats = self.count_requests()
        return ((stats["requests_today"] <= self.limit_day) & (stats["requests_15min"] <= self.limit_15min))


# Singleton instance
strava_api_monitor = APIRequestMonitor(limit_15min=100, limit_day=1_000)