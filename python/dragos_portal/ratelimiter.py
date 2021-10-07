from datetime import datetime, timedelta
import functools

class RateLimitExceededError(Exception):
    """Exception raised when WorldView API rate limit exceeded"""
    def __init__(self):
        super().__init__('WorldView API rate limit exceeded.')

class RateLimiter:
    """Decorator to rate limit requests to the WorldView API"""
    MAX_REQUESTS_PER_MINUTE = 60

    def __init__(self, func):
        self.func = func
        self.requests_made_in_last_minute = 0
        self.reset_minute_counter_at = None

    def __call__(self, *args, **kwargs):
        self.rate_limit()
        print(f'INFO: {self.requests_made_in_last_minute} / {self.MAX_REQUESTS_PER_MINUTE} requests made in last minute')
        return self.func(*args, **kwargs)

    def __get__(self, instance, _owner):
        return functools.partial(self.__call__, instance)

    def rate_limit(self):
        if (self.reset_minute_counter_at == None) or (datetime.now() >= self.reset_minute_counter_at):
            self.requests_made_in_last_minute = 0
            self.reset_minute_counter_at = datetime.now() + timedelta(minutes=1)

        self.requests_made_in_last_minute += 1

        if self.requests_made_in_last_minute > self.MAX_REQUESTS_PER_MINUTE:
            raise RateLimitExceededError
