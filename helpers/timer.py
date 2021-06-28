"""
Import as:

import helpers.timer as htimer
"""

import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple, cast

import helpers.dbg as dbg

_LOG = logging.getLogger(__name__)

# #############################################################################


class Timer:
    """
    Measure time elapsed in one or more intervals.
    """

    def __init__(self, start_on_creation: bool = True):
        """
        Create a timer.

        If "start_on_creation" is True start automatically the timer.
        """
        self._stop: Optional[float] = None
        # Store the time for the last elapsed interval.
        self._last_elapsed: Optional[float] = None
        # Store the total time for all the measured intervals.
        self._total_elapsed = 0.0
        if start_on_creation:
            # For better accuracy start the timer as last action, after all the
            # bookkeeping.
            self._start: Optional[float] = time.time()
        else:
            self._start = None

    def __repr__(self) -> str:
        """
        Return string with the intervals measured so far.
        """
        measured_time = self._total_elapsed
        if self.is_started() and not self.is_stopped():
            # Timer still running.
            measured_time += time.time() - cast(float, self._start)
        ret = "%.3f secs" % measured_time
        return ret

    def stop(self) -> None:
        """
        Stop the timer and accumulate the interval.
        """
        # Timer must have not been stopped before.
        dbg.dassert(self.is_started() and not self.is_stopped())
        # For better accuracy stop the timer as first action.
        self._stop = time.time()
        # Update the total elapsed time.
        # Sometimes we get numerical error tripping this assertion
        # (e.g., '1619552498.813126' <= '1619552498.805193') so we give
        # a little slack to the assertion.
        # dbg.dassert_lte(self._start, self._stop + 1e-2)
        self._last_elapsed = cast(float, self._stop) - cast(float, self._start)
        self._total_elapsed += self._last_elapsed
        # Stop.
        self._start = None
        self._stop = None

    def get_elapsed(self) -> float:
        """
        Stop if not stopped already, and return the elapsed time.
        """
        if not self.is_stopped():
            self.stop()
        dbg.dassert_is_not(self._last_elapsed, None)
        return cast(float, self._last_elapsed)

    # /////////////////////////////////////////////////////////////////////////

    def resume(self) -> None:
        """
        Resume the timer after a stop.
        """
        # Timer must have been stopped before.
        dbg.dassert(self.is_started() or self.is_stopped())
        self._stop = None
        # Start last for better accuracy.
        self._start = time.time()

    def is_started(self) -> bool:
        return self._start is not None and self._start >= 0 and self._stop is None

    def is_stopped(self) -> bool:
        return self._start is None and self._stop is None

    def get_total_elapsed(self) -> float:
        """
        Stop if not stopped already, and return the total elapsed time.
        """
        if not self.is_stopped():
            self.stop()
        return self._total_elapsed

    def accumulate(self, timer: "Timer") -> None:
        """
        Accumulate the value of a timer to the current object.
        """
        # Both timers must be stopped.
        dbg.dassert(timer.is_stopped())
        dbg.dassert(self.is_stopped())
        dbg.dassert_lte(0.0, timer.get_total_elapsed())
        self._total_elapsed += timer.get_total_elapsed()


# #############################################################################

_DTIMER_INFO: Dict[int, Any] = {}


def dtimer_start(log_level: int, message: str) -> int:
    """
    - return: memento of the timer.
    """
    _LOG.log(log_level, "%s ...", message)
    idx = len(_DTIMER_INFO)
    info = log_level, message, Timer()
    _DTIMER_INFO[idx] = info
    return idx


def stop_timer(timer: Timer) -> str:
    timer.stop()
    elapsed_time = round(timer.get_elapsed(), 3)
    msg = "%.3f s" % elapsed_time
    return msg


def dtimer_stop(idx: int) -> Tuple[str, int]:
    """
    - return:
      - message as as string
      - time in seconds (int)
    """
    dbg.dassert_lte(0, idx)
    dbg.dassert_lt(idx, len(_DTIMER_INFO))
    log_level, message, timer = _DTIMER_INFO[idx]
    timer.stop()
    elapsed_time = round(timer.get_elapsed(), 3)
    msg = "%s done (%.3f s)" % (message, elapsed_time)
    del _DTIMER_INFO[idx]
    _LOG.log(log_level, msg)
    return msg, elapsed_time


# #############################################################################
# Context manager.
# #############################################################################


class TimedScope:
    def __init__(self, log_level: int, message: str):
        self._log_level = log_level
        self._message = message
        self._idx: Optional[int] = None
        self.elapsed_time = None

    def __enter__(self) -> "TimedScope":
        self._idx = dtimer_start(self._log_level, self._message)
        return self

    def __exit__(self, *args: Any) -> None:
        if self._idx is not None:
            self.elapsed_time = dtimer_stop(self._idx)


# #############################################################################
# Decorator.
# #############################################################################


def timed(f: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # if hasattr(f, "__name__"):
        func_name = f.__name__
        # else:
        #    func_name = dbg.get_function_name()
        timer = dtimer_start(0, func_name)
        v = f(*args, **kwargs)
        dtimer_stop(timer)
        return v

    return wrapper
