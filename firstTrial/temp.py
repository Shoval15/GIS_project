import pyproj
from shapely.geometry import Polygon

# Define the transformer from WGS84 (EPSG:4326) to Israel TM (EPSG:2039)
transformer = pyproj.Transformer.from_proj(
    pyproj.Proj('epsg:4326'),   # WGS84 (latitude and longitude)
    pyproj.Proj('epsg:2039'))   # Israel Transverse Mercator

# Define the polygon in WGS84 (latitude and longitude)
polygon_wgs84 = Polygon([
    (35.191127300213346, 31.73825933330569),
    (35.19473218912936, 31.73825933330569),
    (35.19473218912936, 31.7415440757295),
    (35.191127300213346, 31.7415440757295),
    (35.191127300213346, 31.73825933330569)
])

# Function to convert a Polygon from WGS84 to Israel TM
def convert_polygon_to_israel_tm(polygon):
    exterior_ring = [
        transformer.transform(y, x) for x, y in polygon.exterior.coords
    ]
    return Polygon(exterior_ring)

# Convert the polygon
polygon_israel_tm = convert_polygon_to_israel_tm(polygon_wgs84)

# Print the converted polygon coordinates
print("Polygon in Israel TM (EPSG:2039):")
print(polygon_israel_tm)
