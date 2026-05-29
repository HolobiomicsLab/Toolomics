---
name: geospatial-pure-python
description: Pure Python geospatial computation without geopandas or shapely. Provides algorithms for point-in-polygon, distance calculations, GeoJSON reading, spatial joins, and buffer analysis using only numpy, pandas, math, and built-in modules.
license: MIT
metadata:
    skill-author: K-Dense Inc.
---

# Geospatial Pure Python

## Overview

This skill provides pure Python implementations of common geospatial operations when geopandas and shapely are not available due to import restrictions. It uses only whitelisted libraries: numpy, pandas, math, json, and built-in modules.

## Core Capabilities

### 1. Point-in-Polygon Algorithm

Ray casting algorithm for determining if a point is inside a polygon.

```python
import numpy as np

def point_in_polygon(point, polygon):
    """
    Determine if a point is inside a polygon using ray casting algorithm.
    
    Args:
        point: tuple (x, y) or list [x, y]
        polygon: list of tuples [(x1, y1), (x2, y2), ...] forming a closed polygon
                 (first and last points should be the same)
    
    Returns:
        bool: True if point is inside polygon, False otherwise
    """
    x, y = point
    n = len(polygon)
    inside = False
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

# For multiple points
def points_in_polygon(points, polygon):
    """
    Vectorized version for multiple points using numpy.
    
    Args:
        points: numpy array of shape (n, 2) or list of points
        polygon: list of vertices as above
    
    Returns:
        numpy array of bools
    """
    import numpy as np
    points = np.asarray(points)
    x, y = points[:, 0], points[:, 1]
    n = len(polygon)
    inside = np.zeros(len(points), dtype=bool)
    
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        # Find points where y is between p1y and p2y
        idx = (y > min(p1y, p2y)) & (y <= max(p1y, p2y)) & (x <= max(p1x, p2x))
        if idx.any():
            if p1y != p2y:
                xinters = (y[idx] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            if p1x == p2x:
                inside[idx] = ~inside[idx]
            else:
                mask = x[idx] <= xinters
                inside[idx] = np.where(mask, ~inside[idx], inside[idx])
        p1x, p1y = p2x, p2y
    
    return inside
```

### 2. Distance Between Coordinates (Haversine Formula)

Calculate great-circle distance between two latitude/longitude points in meters.

```python
import math

def haversine_distance(lon1, lat1, lon2, lat2, radius=6371000):
    """
    Calculate great-circle distance between two points on Earth.
    
    Args:
        lon1, lat1: longitude and latitude of first point in degrees
        lon2, lat2: longitude and latitude of second point in degrees
        radius: Earth radius in meters (default 6371000)
    
    Returns:
        float: distance in meters
    """
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return radius * c

# Vectorized version for many point pairs
def haversine_distance_vectorized(lons1, lats1, lons2, lats2, radius=6371000):
    """
    Vectorized haversine distance using numpy.
    
    Args:
        lons1, lats1: arrays of longitudes and latitudes for first points
        lons2, lats2: arrays for second points
        radius: Earth radius in meters
    
    Returns:
        numpy array of distances in meters
    """
    import numpy as np
    
    phi1 = np.radians(lats1)
    phi2 = np.radians(lats2)
    delta_phi = np.radians(lats2 - lats1)
    delta_lambda = np.radians(lons2 - lons1)
    
    a = np.sin(delta_phi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return radius * c
```

### 3. Reading GeoJSON Files

Parse GeoJSON files using json module and extract geometries and properties.

```python
import json
import pandas as pd

def read_geojson(filepath):
    """
    Read GeoJSON file and extract features into a pandas DataFrame.
    
    Args:
        filepath: path to GeoJSON file
    
    Returns:
        tuple: (geometries, properties_df)
            geometries: list of geometry objects (dict with type and coordinates)
            properties_df: pandas DataFrame of feature properties
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    if data['type'] == 'FeatureCollection':
        features = data['features']
    elif data['type'] == 'Feature':
        features = [data]
    else:
        raise ValueError(f"Unsupported GeoJSON type: {data['type']}")
    
    geometries = []
    properties = []
    
    for feature in features:
        geometries.append(feature['geometry'])
        properties.append(feature.get('properties', {}))
    
    properties_df = pd.DataFrame(properties)
    return geometries, properties_df

def extract_coordinates_from_geojson(filepath, geometry_type='Point'):
    """
    Extract coordinates from GeoJSON features of specific geometry type.
    
    Args:
        filepath: path to GeoJSON file
        geometry_type: 'Point', 'LineString', 'Polygon', etc.
    
    Returns:
        list of coordinate arrays
    """
    geometries, _ = read_geojson(filepath)
    coords = []
    for geom in geometries:
        if geom['type'] == geometry_type:
            coords.append(geom['coordinates'])
    return coords
```

### 4. Spatial Joins Without Geopandas

Perform spatial joins using pure Python algorithms.

```python
import numpy as np
import pandas as pd

def spatial_join_points_to_polygons(points_df, polygons_df, 
                                    point_lon_col='lon', point_lat_col='lat',
                                    polygon_coords_col='coordinates'):
    """
    Spatial join of points to polygons using point-in-polygon test.
    
    Args:
        points_df: DataFrame with point coordinates
        polygons_df: DataFrame with polygon coordinates (list of vertices)
        point_lon_col, point_lat_col: column names for point coordinates
        polygon_coords_col: column name containing polygon coordinates
    
    Returns:
        DataFrame: points_df with added polygon index column
    """
    results = []
    
    for _, point_row in points_df.iterrows():
        point = (point_row[point_lon_col], point_row[point_lat_col])
        matched = False
        
        for poly_idx, poly_row in polygons_df.iterrows():
            polygon = poly_row[polygon_coords_col]
            if point_in_polygon(point, polygon):
                results.append({**point_row.to_dict(), 'polygon_index': poly_idx})
                matched = True
                break
        
        if not matched:
            results.append({**point_row.to_dict(), 'polygon_index': None})
    
    return pd.DataFrame(results)

# For many points, use vectorized approach
def spatial_join_points_to_polygons_vectorized(points_df, polygons_df,
                                               point_lon_col='lon', point_lat_col='lat',
                                               polygon_coords_col='coordinates'):
    """
    Vectorized spatial join using numpy broadcasting (faster for many points).
    """
    import numpy as np
    
    points = points_df[[point_lon_col, point_lat_col]].values
    polygons = polygons_df[polygon_coords_col].values
    
    # Precompute bounding boxes for polygons for quick filtering
    bboxes = []
    for poly in polygons:
        poly_arr = np.array(poly)
        bboxes.append([poly_arr[:, 0].min(), poly_arr[:, 1].min(),
                       poly_arr[:, 0].max(), poly_arr[:, 1].max()])
    bboxes = np.array(bboxes)
    
    results = []
    for i, point in enumerate(points):
        # Filter polygons by bounding box first
        mask = (point[0] >= bboxes[:, 0]) & (point[0] <= bboxes[:, 2]) &                (point[1] >= bboxes[:, 1]) & (point[1] <= bboxes[:, 3])
        
        candidate_indices = np.where(mask)[0]
        matched = False
        
        for poly_idx in candidate_indices:
            if point_in_polygon(point, polygons[poly_idx]):
                results.append({**points_df.iloc[i].to_dict(), 
                               'polygon_index': polygons_df.index[poly_idx]})
                matched = True
                break
        
        if not matched:
            results.append({**points_df.iloc[i].to_dict(), 'polygon_index': None})
    
    return pd.DataFrame(results)
```

### 5. Buffer Analysis on Latitude/Longitude Points

Approximate buffer zones using distance thresholds and bounding boxes.

```python
import numpy as np
import pandas as pd

def create_point_buffer(lon, lat, distance_meters, n_points=36):
    """
    Create a circular buffer around a point (approximated as polygon).
    
    Args:
        lon, lat: center point coordinates in degrees
        distance_meters: buffer radius in meters
        n_points: number of points to approximate circle
    
    Returns:
        list of (lon, lat) coordinates forming the buffer polygon
    """
    import math
    
    # Earth radius in meters
    R = 6371000
    
    # Convert distance to angular distance in radians
    angular_distance = distance_meters / R
    
    # Generate circle points
    buffer_points = []
    for i in range(n_points):
        angle = 2 * math.pi * i / n_points
        
        # Calculate new latitude
        lat_rad = math.radians(lat)
        new_lat = math.asin(math.sin(lat_rad) * math.cos(angular_distance) +
                           math.cos(lat_rad) * math.sin(angular_distance) * math.cos(angle))
        
        # Calculate new longitude
        new_lon = math.radians(lon) + math.atan2(
            math.sin(angle) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(new_lat)
        )
        
        buffer_points.append((math.degrees(new_lon), math.degrees(new_lat)))
    
    # Close the polygon
    buffer_points.append(buffer_points[0])
    return buffer_points

def points_within_distance(lon_center, lat_center, points_df, 
                           distance_meters, lon_col='lon', lat_col='lat'):
    """
    Find points within a given distance of a center point.
    
    Args:
        lon_center, lat_center: center coordinates
        points_df: DataFrame with points to test
        distance_meters: search radius in meters
        lon_col, lat_col: column names for coordinates
    
    Returns:
        DataFrame: subset of points within distance
    """
    distances = haversine_distance_vectorized(
        np.full(len(points_df), lon_center),
        np.full(len(points_df), lat_center),
        points_df[lon_col].values,
        points_df[lat_col].values
    )
    
    within_mask = distances <= distance_meters
    return points_df[within_mask].copy()
```

### 6. Working with MultiPolygons and Complex Geometries

Handle complex GeoJSON geometries.

```python
def flatten_geojson_geometry(geometry):
    """
    Flatten GeoJSON geometry to list of coordinate arrays.
    
    Args:
        geometry: GeoJSON geometry dict
    
    Returns:
        list of coordinate arrays
    """
    geom_type = geometry['type']
    coords = geometry['coordinates']
    
    if geom_type == 'Point':
        return [coords]
    elif geom_type == 'LineString':
        return [coords]
    elif geom_type == 'Polygon':
        # Polygon can have holes, return exterior ring only
        return [coords[0]]
    elif geom_type == 'MultiPolygon':
        # Extract exterior rings from all polygons
        rings = []
        for polygon in coords:
            rings.append(polygon[0])
        return rings
    elif geom_type == 'MultiPoint':
        return coords
    elif geom_type == 'MultiLineString':
        return coords
    else:
        raise ValueError(f"Unsupported geometry type: {geom_type}")
```

## Common Workflows

### 1. Fire Station Coverage Analysis

```python
import json
import pandas as pd
import numpy as np

# Load fire stations (points) and district boundary (polygon)
with open('fire_stations.geojson', 'r') as f:
    stations_data = json.load(f)

with open('etobicoke_boundary.geojson', 'r') as f:
    boundary_data = json.load(f)

# Extract coordinates
stations_coords = []
stations_props = []
for feature in stations_data['features']:
    if feature['geometry']['type'] == 'Point':
        stations_coords.append(feature['geometry']['coordinates'])
        stations_props.append(feature.get('properties', {}))

# Extract boundary polygon (assuming single polygon)
boundary_polygon = boundary_data['features'][0]['geometry']['coordinates'][0]

# Check which stations are inside boundary
inside_mask = points_in_polygon(np.array(stations_coords), boundary_polygon)
stations_inside = [stations_coords[i] for i in range(len(stations_coords)) if inside_mask[i]]

print(f"Total stations: {len(stations_coords)}")
print(f"Stations inside boundary: {len(stations_inside)}")
```

### 2. Distance-Based Analysis

```python
# Calculate distances between all station pairs
n = len(stations_coords)
distances = np.zeros((n, n))
for i in range(n):
    for j in range(i+1, n):
        lon1, lat1 = stations_coords[i]
        lon2, lat2 = stations_coords[j]
        dist = haversine_distance(lon1, lat1, lon2, lat2)
        distances[i, j] = dist
        distances[j, i] = dist

# Find stations within 5km of each other
threshold = 5000  # meters
within_5km = distances <= threshold
np.fill_diagonal(within_5km, False)  # exclude self
```

## Performance Tips

1. **Use numpy vectorization** for operations on many points
2. **Pre-filter with bounding boxes** before expensive point-in-polygon tests
3. **Cache distance calculations** when repeated
4. **Use approximate algorithms** when exact precision isn't critical
5. **Consider using spatial indexing** (grid-based or quadtree) for large datasets

## Limitations

- Not as performant as compiled libraries (geopandas, shapely)
- Limited to 2D operations
- Earth curvature approximations may have small errors over large distances
- Complex geometry operations (union, intersection, difference) not implemented

## Additional Resources

- GeoJSON specification: https://geojson.org/
- Haversine formula: https://en.wikipedia.org/wiki/Haversine_formula
- Point-in-polygon algorithms: https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
