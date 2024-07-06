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

def calculate_distance(building, garden):
    # Calculate distance between building and garden centroids
    building_centroid = building.geometry.centroid.coords[0]
    garden_centroid = garden.geometry.centroid.coords[0]
    return geopy.distance.distance(building_centroid, garden_centroid).km