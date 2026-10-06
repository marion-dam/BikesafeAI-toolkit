"""
helper_functions.py

Utility functions for processing index intervals and converting them into time segments.
These helpers are useful for segmenting time-series data (e.g., video frames, GPS points)
into contiguous intervals and mapping them to human-readable time ranges.

Features:
- Collapse a sorted list of indices into contiguous intervals.
- Convert index intervals into time segments in seconds or formatted as MM:SS.
"""

import numpy as np
from geopy.distance import geodesic
import re

def get_intervals_from_array(array):
    """
    Collapse a sorted sequence of integer indices into contiguous intervals.

    Example:
        [0, 1, 2, 5, 6, 9] -> [(0, 2), (5, 6), (9, 9)]

    Parameters:
        array: Sorted sequence of non-negative integer indices.

    Returns:
        List of (start_index, end_index) tuples representing intervals.
    """
    arr = np.asarray(array, dtype=int)

    if arr.size == 0:
        return []

    # Find positions where contiguity breaks (gap > 1). Duplicates (diff=0) are contiguous.
    breaks = np.where(np.diff(arr) > 1)[0]

    interval_starts = np.insert(arr[breaks + 1], 0, arr[0])
    interval_ends = np.append(arr[breaks], arr[-1])

    intervals = list(zip(interval_starts.tolist(), interval_ends.tolist()))
    return intervals


def intervals_to_time_segments(intervals, times, to_minutes=False, round_seconds=2, include_endpoints=True):
    """
    Convert index intervals into time segments based on the times in cumulative times-list.

    Parameters:
        intervals: Sequence of (start_idx, end_idx) tuples.
        times: Cumulative times in seconds.
        to_minutes: If True, returns 'MM:SS' strings; otherwise seconds (float).
        round_seconds: Decimal rounding for seconds when to_minutes=False.
        include_endpoints: If True, uses [start, end]; if False, maps end -> end-1 for half-open [start, end).

    Returns:
        List of (start_time, end_time) segments as strings (MM:SS) or floats (seconds).
    """

    segments = []
    if to_minutes:
        for start, end in intervals:
            start_time = f"{int(times[start] // 60):02}:{int(times[start] % 60):02}"
            end_time = f"{int(times[end] // 60):02}:{int(times[end] % 60):02}"
            segments.append((start_time, end_time))
    else:
        for start, end in intervals:
            start_time = round(times[start], 2)
            end_time = round(times[end], 2)
            segments.append((start_time, end_time))
    return segments


