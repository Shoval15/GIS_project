from import_data import *
import greedy_algorithm
import greedy_algorithm_topo
import knapsack_problem
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



allocated_gdf, not_allocated_gdf, updated_gardens_gdf = greedy_algorithm_topo.garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths)
print("Allocated buildings:")
print(allocated_gdf)
print("\nNot allocated buildings:")
print(not_allocated_gdf)
utilization = greedy_algorithm_topo.get_utilization(buildings_gdf, allocated_gdf)

allocated_gdf, not_allocated_gdf = knapsack_problem.garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths)
# Print results
print("Allocated buildings:")
print(allocated_gdf)
print("\nNot allocated buildings:")
print(not_allocated_gdf)
knapsack_problem.get_utilization(buildings_gdf, allocated_gdf)
quit()

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = greedy_algorithm.allocate_buildings_to_gardens_centroid(buildings_gdf, gardens_gdf)
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = greedy_algorithm.allocate_buildings_to_gardens_min_max(buildings_gdf, gardens_gdf, 'min')
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = greedy_algorithm.allocate_buildings_to_gardens_min_max(buildings_gdf, gardens_gdf, 'max')
print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)

# Allocate buildings to gardens
buildings_gdf, gardens_gdf = greedy_algorithm.allocate_buildings_to_gardens_centroid_topo(buildings_gdf, gardens_gdf, walking_paths)

print("Buildings DataFrame:")
print(buildings_gdf)
print("\nGardens DataFrame:")
print(gardens_gdf)