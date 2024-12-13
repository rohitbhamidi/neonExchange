import threading
import time
from contextlib import contextmanager

class RateLimiter:
    def __init__(self, max_calls_per_sec):
        self.lock = threading.Lock()
        self.calls = 0
        self.max_calls = max_calls_per_sec
        self.period = 1
        self.start_time = time.time()

    @contextmanager
    def __call__(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            if elapsed >= self.period:
                self.calls = 0
                self.start_time = time.time()
            if self.calls >= self.max_calls:
                sleep_time = self.period - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                self.calls = 0
                self.start_time = time.time()
            self.calls += 1
        yield
