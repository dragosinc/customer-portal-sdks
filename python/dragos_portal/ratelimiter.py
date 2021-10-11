from datetime import datetime, timedelta
import functools

class RateLimitExceededError(Exception):
    """Exception raised when WorldView API rate limit exceeded"""
    def __init__(self):
        super().__init__('WorldView API rate limit exceeded.')

class RateLimiter:
    """Decorator to rate limit requests to the WorldView API"""
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_REQUESTS_PER_WEEK = 1_000

    def __init__(self, func):
        self.func = func
        self.requests_in_last_minute = 0
        self.reset_minute_counter_at = None

        self.requests_in_last_week = 0
        self.reset_week_counter_at = None

    def __call__(self, *args, **kwargs):
        self.rate_limit()
        print(f'INFO: {self.requests_in_last_minute} / {self.MAX_REQUESTS_PER_MINUTE} requests made in last minute')
        print(f'INFO: {self.requests_in_last_week} / {self.MAX_REQUESTS_PER_WEEK} requests made in last week')
        return self.func(*args, **kwargs)

    def __get__(self, instance, _owner):
        return functools.partial(self.__call__, instance)

    def rate_limit(self):
        current_time = datetime.now()
        if (self.reset_minute_counter_at == None) or (current_time >= self.reset_minute_counter_at):
            self.requests_in_last_minute = 0
            self.reset_minute_counter_at = current_time + timedelta(minutes=1)

        if (self.reset_week_counter_at == None) or (current_time >= self.reset_week_counter_at):
            self.requests_in_last_week = 0
            self.reset_week_counter_at = current_time + timedelta(weeks=1)

        self.requests_in_last_minute += 1
        self.requests_in_last_week += 1

        if (self.requests_in_last_minute > self.MAX_REQUESTS_PER_MINUTE) or (self.requests_in_last_week > self.MAX_REQUESTS_PER_WEEK):
            raise RateLimitExceededError
