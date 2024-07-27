from . import utilities
import pandas as pd
import geopandas as gpd
import pulp
import json

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status, meters_for_resident, residents):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths, apartment_type, project_status, distance, meters_for_resident, residents)
    # buildings with their apartment counts
    buildings = buildings_gdf[['OBJECTID', 'units_e']].set_index('OBJECTID').to_dict()['units_e']
    # gardens with their capacities
    gardens = gardens_gdf[['OBJECTID', 'capacity']].set_index('OBJECTID').to_dict()['capacity']
    # LP problem
    prob = pulp.LpProblem("Garden-Centric Building Allocation", pulp.LpMaximize)

    # binary variables for each building-garden pair
    vars = pulp.LpVariable.dicts("Alloc", 
                            [(b, g) for b in buildings for g in gardens], 
                            cat='Binary')

    # Maximize the number of buildings allocated
    prob += pulp.lpSum([vars[b,g] for b in buildings for g in gardens])
    for b in buildings:
        prob += pulp.lpSum([vars[b,g] for g in gardens]) <= 1
    for g in gardens:
        prob += pulp.lpSum([buildings[b] * vars[b,g] for b in buildings]) <= gardens[g]
    prob.solve()

    allocation = {}
    for b in buildings_gdf['OBJECTID']:
        for g in gardens_gdf['OBJECTID']:
            if vars[b,g].value() > 0.5:  # Binary variable is 1 (allocated)
                allocation[b] = g

    allocated_buildings = buildings_gdf[buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()
    allocated_buildings['allocated_garden'] = allocated_buildings['OBJECTID'].map(allocation)
    not_allocated_buildings = buildings_gdf[~buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()

    merged_data = allocated_buildings.merge(
        gardens_gdf[['OBJECTID', 'Shape.STArea()', 'YEUD', 'Descr', 'capacity', 'remaining_capacity']], 
        left_on='allocated_garden', 
        right_on='OBJECTID', 
        suffixes=('_building', '_garden')
    )

    merged_data = merged_data.rename(columns={
        'OBJECTID_building': 'OBJECTID_building',
        'OBJECTID_garden': 'OBJECTID_garden',
        'Shape.STArea()_building': 'Shape.STArea()_building',
        'Shape.STArea()_garden': 'Shape.STArea()_garden',
    })

    # Update remaining capacity for gardens
    for garden_id in gardens_gdf['OBJECTID']:
        allocated_units = merged_data[merged_data['OBJECTID_garden'] == garden_id]['units_e'].sum()
        gardens_gdf.loc[gardens_gdf['OBJECTID'] == garden_id, 'remaining_capacity'] -= allocated_units

    allocation_stats = utilities.calculate_stats(buildings_gdf, merged_data)

    # Write to JSON file
    with open('allocated_buildings_with_gardens.json', 'w', encoding='utf-8') as f:
        geojson_data = json.loads(merged_data.to_json())
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    # Write to JSON file
    with open('gardens_after_allocation.json', 'w', encoding='utf-8') as f:
        geojson_data_gardens = gardens_gdf.to_json()
        f.write(geojson_data_gardens)

    # Write to JSON file
    with open('not_allocated_buildings.json', 'w', encoding='utf-8') as f:
        geojson_data_not_allocated_buildings = not_allocated_buildings.to_json()
        f.write(geojson_data_not_allocated_buildings)
        
    return merged_data, not_allocated_buildings, allocation_stats, gardens_gdf