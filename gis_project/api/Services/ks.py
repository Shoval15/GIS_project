from . import utilities
import pandas as pd
import geopandas as gpd
import pulp
import json

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status, meters_for_resident, residents):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths, apartment_type, project_status, distance, meters_for_resident, residents)

    # Create the LP problem
    prob = pulp.LpProblem("Garden-Centric Building Allocation", pulp.LpMaximize)

    # Decision variables
    x = pulp.LpVariable.dicts("allocate", 
                              ((b, g) for b in buildings_gdf.index for g in gardens_gdf.index),
                              cat='Binary')

    # Objective function: Maximize the number of buildings and apartments allocated
    prob += pulp.lpSum(x[b, g] for b in buildings_gdf.index for g in gardens_gdf.index) + \
            0.01 * pulp.lpSum(buildings_gdf.loc[b, 'units_e'] * x[b, g] for b in buildings_gdf.index for g in gardens_gdf.index)

    # Constraints
    # Each building can be allocated to at most one garden
    for b in buildings_gdf.index:
        prob += pulp.lpSum(x[b, g] for g in gardens_gdf.index) <= 1

    # The total number of apartments allocated to each garden must not exceed its capacity
    for g in gardens_gdf.index:
        prob += pulp.lpSum(buildings_gdf.loc[b, 'units_e'] * x[b, g] for b in buildings_gdf.index) <= gardens_gdf.loc[g, 'capacity']

    # Solve the problem
    prob.solve()

    # Process results
    allocation = {}
    for b in buildings_gdf.index:
        for g in gardens_gdf.index:
            if pulp.value(x[b, g]) == 1:
                allocation[b] = g

    allocated_buildings = buildings_gdf[buildings_gdf.index.isin(allocation.keys())].copy()
    allocated_buildings['allocated_garden'] = allocated_buildings.index.map(allocation)
    not_allocated_buildings = buildings_gdf[~buildings_gdf.index.isin(allocation.keys())].copy()

    merged_data = allocated_buildings.merge(
        gardens_gdf[['Shape.STArea()', 'YEUD', 'Descr', 'capacity', 'remaining_capacity']], 
        left_on='allocated_garden', 
        right_index=True,
        suffixes=('_building', '_garden')
    )

    # Update remaining capacity for gardens
    for garden_id in gardens_gdf.index:
        allocated_units = merged_data[merged_data['allocated_garden'] == garden_id]['units_e'].sum()
        gardens_gdf.loc[garden_id, 'remaining_capacity'] -= allocated_units

    allocation_stats = utilities.calculate_stats(buildings_gdf, merged_data)

    # Write results to JSON files
    with open('allocated_buildings_with_gardens.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(merged_data.to_json()), f, ensure_ascii=False, indent=4)

    with open('gardens_after_allocation.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(gardens_gdf.to_json()), f, ensure_ascii=False, indent=4)

    with open('not_allocated_buildings.json', 'w', encoding='utf-8') as f:
        json.dump(json.loads(not_allocated_buildings.to_json()), f, ensure_ascii=False, indent=4)
        
    return merged_data, not_allocated_buildings, allocation_stats, gardens_gdf