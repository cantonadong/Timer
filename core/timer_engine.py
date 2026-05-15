import time
from enum import Enum


class TimerMode(Enum):
    COUNTUP = "countup"
    COUNTDOWN = "countdown"


class TimerState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


class TimerEngine:
    def __init__(self):
        self._start_time = None
        self._accumulated_s = 0.0
        self.state = TimerState.IDLE
        self.mode = TimerMode.COUNTUP
        self.target_ms = 0

    @property
    def current_elapsed_ms(self):
        base = self._accumulated_s
        if self.state == TimerState.RUNNING and self._start_time is not None:
            base += time.perf_counter() - self._start_time
        return int(base * 1000)

    @property
    def remaining_ms(self):
        return max(0, self.target_ms - self.current_elapsed_ms)

    @property
    def is_finished(self):
        return (
            self.mode == TimerMode.COUNTDOWN
            and self.state == TimerState.RUNNING
            and self.remaining_ms == 0
        )

    def start(self):
        if self.state == TimerState.IDLE:
            self._accumulated_s = 0.0
            self._start_time = time.perf_counter()
            self.state = TimerState.RUNNING

    def pause(self):
        if self.state == TimerState.RUNNING:
            self._accumulated_s += time.perf_counter() - self._start_time
            self._start_time = None
            self.state = TimerState.PAUSED

    def resume(self):
        if self.state == TimerState.PAUSED:
            self._start_time = time.perf_counter()
            self.state = TimerState.RUNNING

    def reset(self):
        self._accumulated_s = 0.0
        self._start_time = None
        self.state = TimerState.IDLE
