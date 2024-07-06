from import_data import *
from greedy_algorithm import allocate_buildings_to_gardens
#TODO: for debugging

# Bounding box coordinates
xmin = 216147.29618823092
ymin = 629402.4939445071
xmax = 216769.5974328334
ymax = 630198.3622029102

# Create a Polygon object
polygon = Polygon([(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)])
buildings_gdf = import_buildings(polygon)
gardens_gdf = import_land_designations(polygon)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = allocate_buildings_to_gardens(buildings_gdf, gardens_gdf)
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)