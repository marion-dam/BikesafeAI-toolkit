"""
gpx_basics.py

Utility functions for parsing GPX files and visualizing GPS tracks using Folium.

Features:
- Parse GPX files into gpxpy objects.
- Extract coordinates and cumulative times from GPX tracks.
- Create interactive Folium maps with GPX tracks, optional tooltips, and color-coded markers.
"""

import gpxpy
import folium
import branca.colormap as cm

def parse_gpx(file_path):
    """
    Load and parse a GPX file.

    Parameters:
        file_path (str): Path to the GPX file.

    Returns:
        gpx (gpxpy.gpx.GPX): Parsed GPX object.
    """
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    return gpx


def get_coordinates_and_times(gpx):
    """
    Extract coordinates and cumulative times from a parsed GPX object.

    Parameters:
        gpx (gpxpy.gpx.GPX): Parsed GPX object.

    Returns:
        coordinates (list of tuple): List of (latitude, longitude) pairs.
        cumul_time (list of float): Cumulative time in seconds.
        cumul_time_string (list of str): Cumulative time formatted as MM:SS.
    """
    # Extract coordinates and timestamps
    coordinates = []
    times = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append((point.latitude, point.longitude))
                times.append(point.time)

    # Compute time differences
    time_differences = [None]
    for i in range(1, len(times)):
        if times[i] and times[i - 1]:
            time_diff = (times[i] - times[i - 1]).total_seconds()
        else:
            time_diff = None
        time_differences.append(time_diff)

    # Compute cumulative time
    cumul_time = []
    cumulative_sum = 0
    for time_diff in time_differences:
        if time_diff is not None:
            cumulative_sum += time_diff
        cumul_time.append(cumulative_sum)

    # Ensure first point is zero
    cumul_time[0] = 0

    # Format cumulative time as MM:SS
    cumul_time_string = [f"{int(t // 60):02}:{int(t % 60):02}" for t in cumul_time]

    return coordinates, cumul_time, cumul_time_string


def create_gps_map(coordinates, zoom_start=14, tooltip_list = None, color_list = None, color_list_name = ''):
    """
    Create a Folium map centered on the middle coordinate and plot the GPX track.

    Parameters:
        coordinates (list of tuple): List of (latitude, longitude) pairs.
        zoom_start (int): Initial zoom level for the map. Default is 14.
        line_color (str): Color of the GPX track line. Default is 'blue'.
        tooltip_list (list of str or float): Optional list to be displayed in tooltips.
        color_list (list of float): Optional list to determine color of markers.
        color_list_name (str): Optional name for color_list (displayed in tooltip).

    Returns:
        folium.Map: A Folium map object with the GPX track.
    """
    if not coordinates:
        raise ValueError("Coordinates list is empty.")

    # Center map on the middle coordinate
    map_center = coordinates[len(coordinates) // 2]
    m = folium.Map(location=map_center, zoom_start=zoom_start)

    # Add GPX track as a polyline
    folium.PolyLine(coordinates, color='blue').add_to(m)

    if color_list:
        colormap = cm.LinearColormap(['green', 'yellow', 'red'], vmin=min(color_list), vmax=max(color_list))
        # Add the colormap to the map
        colormap.add_to(m)
    else:
        color_list = [1] * len(coordinates)
        colormap = cm.LinearColormap(['blue', 'blue'], vmin=0, vmax=1)

    # If tooltip_list is provided, add tooltips to markers
    if tooltip_list:
        # Add circle markers with tooltip showing index and time
        for i, (coord, t) in enumerate(zip(coordinates, tooltip_list)):
            folium.CircleMarker(
                location=coord,
                radius=1,
                color= colormap(color_list[i - 1]),
                fill=True,
                fill_opacity=0.8,
                tooltip=f"Time: {t}" if color_list_name == '' else f"Time: {t}<br>{color_list_name}: {color_list[i - 1]:.2f}"
            ).add_to(m)

    return m
