import time
import logging
import pytest
from pymace.test.perftest import performance_time

def dummy_func():
    # A quick function that does very little.
    return 42

def slow_func():
    # A function that sleeps for a short time to simulate workload.
    time.sleep(0.01)
    return "done"

def test_performance_time_returns_average():
    repetitions = 10
    avg_time = performance_time(repetitions, dummy_func)
    # Check that the returned value is a float and not negative.
    assert isinstance(avg_time, float)
    assert avg_time >= 0

def test_performance_time_logging_mode(caplog):
    repetitions = 5
    with caplog.at_level(logging.DEBUG):
        ret = performance_time(repetitions, dummy_func, output="toConsole")
    # In logging mode, the function should return None.
    assert ret is None
    # Also check that some debug log was created.
    assert any("took" in record.message for record in caplog.records)

def test_performance_time_with_slow_func():
    repetitions = 3
    avg_time = performance_time(repetitions, slow_func)
    # Since slow_func sleeps 0.01 seconds, avg_time should be at least 0.01
    assert avg_time >= 0.01