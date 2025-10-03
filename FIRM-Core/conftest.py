"""Test configuration: provide a minimal benchmark fixture if plugin is missing.

This ensures tests marked with @pytest.mark.benchmark can run without the
pytest-benchmark plugin installed, aligning with no-hidden-dependency policy.
"""
import os
import pytest
import time


@pytest.fixture
def benchmark():
    """Simple timing wrapper returning the function result.

    Usage: result = benchmark(func, *args, **kwargs)
    Provides .elapsed attribute in seconds on the returned object when possible.
    """
    class _Result:
        def __init__(self, value, elapsed):
            self.value = value
            self.elapsed = elapsed

        def __iter__(self):
            # allow unpacking if caller expects the direct value
            yield self.value

    def _bench(fn, *args, **kwargs):
        t0 = time.perf_counter()
        value = fn(*args, **kwargs)
        t1 = time.perf_counter()
        return value

    return _bench


