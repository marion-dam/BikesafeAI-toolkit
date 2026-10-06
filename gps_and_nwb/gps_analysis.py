"""
gpx_analysis.py

Utility functions and classes for analyzing speed and acceleration from GPS coordinates and time data.
Includes smoothing techniques and visualization tools.

Features:
- KalmanFilter class for smoothing noisy measurements.
- Moving average smoothing for speed data.
- Compute speeds (m/s or km/h) from GPS coordinates and cumulative times.
- Compute acceleration from speed and time series.
- Plot speed and acceleration on a dual-axis chart using Matplotlib and Seaborn.

Assumptions:
- Distances are computed on a flat surface (ascent/descent ignored).
- Coordinates are in (latitude, longitude) format.
- Times are cumulative and monotonic non-decreasing.
"""

import numpy as np
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class KalmanFilter:
    """
    Simple Kalman Filter for smoothing measurements.
    """
    def __init__(self, process_variance, measurement_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def update(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        return self.posteri_estimate

def moving_average(data, window_size):
    """
    Smooth data using a moving average.

    Parameters:
        data (list or np.array): Input data.
        window_size (int): Size of the moving window.

    Returns:
        np.array: Smoothed data.
    """
    if window_size < 1:
        raise ValueError("Window size must be at least 1")
    if window_size > len(data):
        raise ValueError("Window size must be less than or equal to the length of the data")

    averaged_data = np.convolve(data, np.ones(window_size) / window_size, mode='valid')
    pad_size = (len(data) - len(averaged_data)) // 2
    padded_data = np.pad(averaged_data, (pad_size, len(data) - len(averaged_data) - pad_size), mode='edge')
    return padded_data

def compute_speeds(coordinates, times, smoothing_method='moving_average', window_size=7):
    """
    Compute speeds (km/h) from coordinates and cumulative times, then smooth them.

    Parameters:
        coordinates (list of tuple): (latitude, longitude) pairs.
        times (list of float): Cumulative time in seconds.
        method (str): Smoothing method ('moving_average' or 'kalman').
        window_size (int): Window size for moving average.

    Returns:
        speeds_kmh (list): Raw speeds in km/h.
        smoothed_speeds (list): Smoothed speeds in km/h.
    """
    if len(coordinates) != len(times):
        raise ValueError("Coordinates and times must have the same length.")


    speeds = [0.0]
    time_diffs = [0.0]

    for i in range(1, len(coordinates)):
        point1 = coordinates[i - 1]
        point2 = coordinates[i]

        # Calculate distance in meters
        distance = geodesic(point1, point2).meters

        # Calculate time difference in seconds
        time_diff = times[i] - times[i - 1]

        # Compute speed in m/s
        speed = distance / time_diff if time_diff > 0 else 0.0

        speeds.append(speed)
        time_diffs.append(time_diff)


    # Apply smoothing
    if smoothing_method == 'kalman':
        kf = KalmanFilter(process_variance=1e-5, measurement_variance=1e-2, estimated_measurement_variance=1e-1)
        smoothed_speeds = [kf.update(speed) for speed in speeds]
    elif smoothing_method == 'moving_average':
        smoothed_speeds = moving_average(speeds, window_size=window_size)
    else:
        raise ValueError("Unknown method! Choose 'moving_average' or 'kalman'.")

    return speeds, smoothed_speeds


def compute_acceleration(speeds, times, fill_first=0.0):
    """
    Calculate acceleration from speeds and cumulative times.

    Parameters:
        speeds (list[float]): Speeds (m/s).
        times (list[float]): Cumulative times in seconds (monotonic non-decreasing).
        fill_first (float or None): Value to place for the first acceleration entry.
            Use 0.0 (default) to match common plotting practice; use None to skip it.

    Returns:
        list[float or None]: Accelerations in m/s². Same length as `speeds`.
    """
    if len(speeds) != len(times):
        raise ValueError("speeds and times must have the same length.")

    if len(speeds) < 2:
        return [fill_first] if fill_first is not None else [None]

    accelerations = [fill_first] if fill_first is not None else [None]

    for i in range(1, len(speeds)):
        dt = times[i] - times[i - 1]
        dv = speeds[i] - speeds[i - 1]

        if dt is None or dt <= 0:
            # Non-increasing or missing time -> undefined acceleration for this step
            accelerations.append(0.0 if fill_first is not None else None)
        else:
            accelerations.append(dv / dt)

    return accelerations


def plot_speed(times_string, smoothed_speeds, accelerations = None, in_kmh = False):
    """
    Plot speed and acceleration on a dual-axis line chart.

    Parameters:
        times_string (list[str]): Time labels (e.g., MM:SS).
        smoothed_speeds (list[float]): Speeds in km/h.
        accelerations (list[float]): Accelerations in m/s². Optional.
    """
    sns.set_style('whitegrid')
    fig, ax1 = plt.subplots(figsize=(12, 4))

    # Primary axis for speed
    color_speed = 'tab:blue'
    ax1.set_xlabel('Time in video')

    ax1.plot(times_string, smoothed_speeds, color=color_speed)    
    ax1.tick_params(axis='y', labelcolor=color_speed)

    if in_kmh:
        label_unit = 'km/h'
    else:
        label_unit = 'm/s'
    
    ax1.set_ylabel(f'Speed ({label_unit})', color=color_speed)

    if accelerations is not None:
        if in_kmh:
            print('Acceleration plot requires speeds in m/s. Skipping acceleration plot.')
        else:
            # Secondary axis for acceleration
            ax2 = ax1.twinx()
            color_accel = 'tab:red'
            ax2.set_ylabel('Acceleration (m/s²)', color=color_accel)
            ax2.plot(times_string, accelerations, color=color_accel, linestyle='-', label='Acceleration')
            ax2.tick_params(axis='y', labelcolor=color_accel)

            # Title
            plt.title('Speed and Acceleration During Ride')
    else: 
        plt.title(f'Speed During Ride')

    # X-axis ticks every 120 points
    ax1.set_xticks(np.arange(0, len(times_string), 120))
    ax1.set_xticklabels(np.array(times_string)[::120])

    fig.tight_layout()
    plt.show()
