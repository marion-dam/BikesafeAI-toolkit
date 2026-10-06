
"""
nwb_helper_functions.py

Utility functions for working with Dutch NWB (Nationaal Wegenbestand) road data and GPX tracks.
These functions leverage GeoPandas and Folium for spatial analysis and visualization.

Features:
- Filter roads by province or municipality.
- Create interactive Folium maps with roads, max speed, GPX points, and optional markers.
- Convert WKT LineStrings to coordinate tuples and compute distances.
- Interpolate points along a LineString at a given distance.
"""

import geopandas as gpd
import folium
from geopy.distance import geodesic
import re


def load_and_filter_roads(shapefile_path, provinces=None, municipalities=None):
    """
    Load NWB roads shapefile and optionally filter by province codes or municipality names.

    Parameters
    ----------
    shapefile_path: str, path to the NWB roads shapefile.
    provinces : list of str, optional. List of province codes to filter the roads. Default is None.
    municipalities: list of str, optional. List of municipality names to filter the roads. Default is None.

    Returns
    -------
    roads: GeoDataFrame containing the filtered roads.
    """
    roads = gpd.read_file(shapefile_path)
    if provinces:
        roads = roads[roads['PVE_CODE'].isin(provinces)]
    if municipalities:
        roads = roads[roads['GME_NAAM'].isin(municipalities)]
    return roads



def create_map_with_roads_info(center, roads, gpx_points, times, marker_info_name=None, marker_info=None, marker_info_cols=None):
    """
    Create an interactive Folium map with roads colored by speed limits and GPX points.
    Optionally, add extra markers with additional information.

    Parameters
    ----------
    center : tuple, (latitude, longitude) for the initial map center.
    roads : GeoDataFrame, Roads data with geometry and speed limit information.
    gpx_points : GeoDataFrame, GPX points to plot on the map.
    times : list or None, List of timestamps corresponding to GPX points; if None, no time tooltips are shown.
    marker_info_name : str or None, Label prefix for additional markers; default is None.
    marker_info : DataFrame or None, Additional info to display as markers; must include 'WVK_ID' and distance columns ('VAN' and sometimes 'TOT').
    marker_info_cols : list of str or None, Column names in marker_info representing distances along the road geometry (['VAN'] or ['VAN' and 'TOT']).

    Returns
    -------
    folium.Map, Interactive map with roads, GPX points, and optional markers.
    """
    m = folium.Map(location=center, zoom_start=12)

    # Define color mapping for speed limits
    speed_colors = {'30': "green", '50': "blue", '80': "orange", '100': "red", '120': "darkred", '130': "darkred"}
    # Add a legend for speed limits
    legend_html = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        width: 150px;
        height: auto;
        background-color: white;
        border: 2px solid grey;
        z-index: 1000;
        font-size: 14px;
        padding: 10px;
        ">
        <b>Speed Limits</b><br>
        <i style="background:green; width: 10px; height: 10px; display: inline-block;"></i> 30 km/h<br>
        <i style="background:blue; width: 10px; height: 10px; display: inline-block;"></i> 50 km/h<br>
        <i style="background:orange; width: 10px; height: 10px; display: inline-block;"></i> 80 km/h<br>
        <i style="background:red; width: 10px; height: 10px; display: inline-block;"></i> 100 km/h<br>
        <i style="background:darkred; width: 10px; height: 10px; display: inline-block;"></i> 120-130 km/h<br>
        <i style="background:gray; width: 10px; height: 10px; display: inline-block;"></i> Unknown
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))


    # Add roads
    for _, road in roads.iterrows():
        max_speed = str(road.get("MAXSHD", "Unknown"))
        road_color = speed_colors.get(max_speed, "gray")
        geom = road["geometry"]

        if geom.geom_type == "LineString":
            folium.PolyLine(
                locations=[(lat, lon) for lon, lat in geom.coords],
                color=road_color,
                weight=3,
                tooltip=f"Max Speed: {max_speed} km/h"
            ).add_to(m)

    # Add GPX points
    for i, point in gpx_points.iterrows():
        folium.CircleMarker(
            location=[point.geometry.y, point.geometry.x],
            radius=3,
            color="black",
            fill=True,
            fill_opacity=0.8,
            tooltip="" if times is None else f"Time: {times[i]}"
        ).add_to(m)

    # Add extra info if provided
    colors = ["white", "lightblue", "lightgrey", "lightgreen", "lightred"]
    if marker_info is not None:
        marker_info = marker_info.merge(roads[['WVK_ID', 'geometry']], on='WVK_ID', how='left')
        marker_info = marker_info[~marker_info['geometry'].isna()]

        for i in range(len(marker_info_cols)):
            marker_info[f'POINT_{i}'] = [
                point_at_distance(str(geom), dist) for geom, dist in zip(marker_info['geometry'], marker_info[marker_info_cols[i]])
            ]

            marker_info = marker_info[~marker_info[f'POINT_{i}'].isna()]

            for _, row in marker_info.iterrows():
                folium.Marker(
                    location=[row[f'POINT_{i}'][0], row[f'POINT_{i}'][1]],
                    icon=folium.Icon(color=colors[i % len(colors)], icon="remove-road", prefix="fa"),
                    tooltip=f"{marker_info_name} {marker_info_cols[i]} bij WVK_ID: {row['WVK_ID']}<br>Locatie in wegvak: {row[marker_info_cols[i]]} m",
                ).add_to(m)

    return m




def linestring_to_tuple(wkt_linestring):
    """
    Convert a LINESTRING WKT to a list of (latitude, longitude) tuples.

    Parameters
    ----------
    wkt_linestring : str, WKT representation of a LINESTRING.

    Returns
    -------
    list of tuple, List of (latitude, longitude) coordinate pairs.
    """
    coordinates = re.findall(r'(\-?\d+\.\d+)\s+(\-?\d+\.\d+)', wkt_linestring)
    return [(float(lat), float(lon)) for lon, lat in coordinates]


def calculate_linestring_length(wkt_linestring):
    """
    Calculate the total length of a LINESTRING from WKT format.

    Parameters
    ----------
    wkt_linestring : str, WKT representation of a LINESTRING.

    Returns
    -------
    tuple, (total_distance : float, distances : list of float, coords : list of tuple)
        total_distance : Total length in meters.
        distances : Length of each segment in meters.
        coords : List of (latitude, longitude) tuples.
    """
    coords = linestring_to_tuple(wkt_linestring)
    total_distance = 0.0
    distances = []
    
    for i in range(len(coords) - 1):
        dist = geodesic(coords[i], coords[i+1]).meters
        distances.append(dist)
        total_distance += dist
    
    return total_distance, distances, coords


def point_at_distance(wkt_linestring, target_distance, print_errors=False):
    """
    Find the coordinate at a given distance along the LINESTRING.

    Parameters
    ----------
    wkt_linestring : str, WKT representation of a LINESTRING.
    target_distance : float, Distance in meters from the start of the LINESTRING.
    print_errors : bool, If True, prints an error when target_distance exceeds total length.

    Returns
    -------
    tuple or None, (latitude, longitude) at the specified distance, or None if out of range.
    """
    total_length, segment_lengths, coords = calculate_linestring_length(wkt_linestring)
    
    if target_distance > round(total_length, 2) + 0.1:
        if print_errors:
            print('Target distance exceeds total linestring length:', wkt_linestring, total_length, target_distance)
        return None

    # Find the segment where the target distance lies
    current_distance = 0.0
    for i in range(len(segment_lengths)):
        segment_start = coords[i]
        segment_end = coords[i + 1]
        segment_length = segment_lengths[i]
        
        if current_distance + segment_length >= target_distance:
            remaining_distance = target_distance - current_distance
            fraction = remaining_distance / segment_length
            
            lat1, lon1 = segment_start
            lat2, lon2 = segment_end
            
            lat_interp = lat1 + fraction * (lat2 - lat1)
            lon_interp = lon1 + fraction * (lon2 - lon1)
            
            return (lat_interp, lon_interp)
        
        current_distance += segment_length
