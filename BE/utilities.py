import pyproj
from shapely.geometry import Point, Polygon
import geopy.distance

# Define the transformer from Israel TM to WGS84 (latitude and longitude)
transformer = pyproj.Transformer.from_proj(
    pyproj.Proj('epsg:2039'),  # Israel Transverse Mercator
    pyproj.Proj('epsg:4326'))   # WGS84 (latitude and longitude)

# Function to convert a Point or Polygon to WGS84
def convert_to_wgs84(geometry):
    if isinstance(geometry, Point):
        lon, lat = transformer.transform(geometry.x, geometry.y)
        return Point(lon, lat)
    elif isinstance(geometry, Polygon):
        exterior_ring = []
        for x, y in geometry.exterior.coords:
            lon, lat = transformer.transform(x, y)
            exterior_ring.append((lon, lat))
        return Polygon(exterior_ring)
    
# Function to convert a string "(x, y)" to a Point object
def str_to_point(s):
    x, y = map(float, s.strip("()").split(","))
    return Point(x, y)

def calculate_max_distance(building_geom, garden_geom):
    if isinstance(building_geom, Point):
        # Calculate distance from the building point to all garden vertices
        return max(building_geom.distance(garden_geom.exterior))
    
    # Calculate distance from the building's bounding box to the garden's bounding box
    building_bbox = building_geom.bounds
    garden_bbox = garden_geom.bounds
    
    # Calculate distances from each corner of the building bbox to each corner of the garden bbox
    distances = [
        building_geom.distance(Point(gx, gy))
        for gx in [garden_bbox[0], garden_bbox[2]]  # xmin, xmax
        for gy in [garden_bbox[1], garden_bbox[3]]  # ymin, ymax
    ]
    
    return max(distances)

def calculate_distance(building, garden):
    return building.distance(garden)

def calculate_min_distance(building_geom, garden_geom):
    if isinstance(building_geom, Point):
        # Calculate distance from the building point to the garden centroid
        return building_geom.distance(garden_geom.centroid)
    else:
        # Calculate distance from the building centroid to the garden centroid
        return building_geom.centroid.distance(garden_geom.centroid)
