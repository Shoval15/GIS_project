from import_data import *
from greedy_algorithm import *
from distance_walk import calculate_walk_distance
from shapely.geometry import Point

# Bounding box coordinates
xmin = 216147.29618823092
ymin = 629402.4939445071
xmax = 216769.5974328334
ymax = 630198.3622029102

# Create a Polygon object
polygon = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])
buildings_gdf = import_buildings(polygon)
gardens_gdf = import_land_designations(polygon)
walking_paths = import_walking_paths(polygon)
calculate_walk_distance(walking_paths, Point(35.172, 31.762), Point(35.174, 31.763))

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = allocate_buildings_to_gardens_centroid(buildings_gdf, gardens_gdf)
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = allocate_buildings_to_gardens_min_max(buildings_gdf, gardens_gdf, 'min')
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = allocate_buildings_to_gardens_min_max(buildings_gdf, gardens_gdf, 'max')
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = allocate_buildings_to_gardens_centroid_topo(buildings_gdf, gardens_gdf, walking_paths)
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)