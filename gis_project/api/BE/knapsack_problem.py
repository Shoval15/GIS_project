import numpy as np
from . import utilities 

def preprocess_data(buildings_gdf, gardens_gdf, G):
    # Calculate garden capacities
    gardens_gdf['capacity'] = (gardens_gdf['Shape_STAr'] / 1000 * 90).fillna(0).astype(int)
    gardens_gdf['remaining_capacity'] = gardens_gdf['capacity']
    # Calculate distances between gardens and buildings
    gardens_gdf['nearby_buildings'] = gardens_gdf.apply(lambda x: utilities.find_nearby_buildings(x, buildings_gdf, G), axis=1)
    # Handle NA and inf values in NUM_APTS_C
    buildings_gdf['NUM_APTS_C'] = buildings_gdf['NUM_APTS_C'].fillna(0).replace([np.inf, -np.inf], 0).astype(int)
    return buildings_gdf, gardens_gdf

# Implements the 0/1 knapsack algorithm to optimally allocate buildings to a garden
def knapsack_garden_allocation(garden, buildings):
    capacity = int(garden['capacity'])
    n = len(buildings)
    
    # Filter out buildings with zero apartments
    valid_buildings = [b for b in buildings if int(b[2]) > 0]
    valid_buildings_amounts = len(valid_buildings)
    
    # Create a 2D array for dynamic programming - dp[i][w] represents the maximum number of apartments that can be allocated
    dp = [[0 for _ in range(capacity + 1)] for _ in range(valid_buildings_amounts + 1)]
    
    # Fill the dp table
    for i in range(1, valid_buildings_amounts + 1):
        for w in range(1, capacity + 1):
            apartments = int(valid_buildings[i-1][2])
            if apartments <= w:
                dp[i][w] = max(apartments + dp[i-1][w-apartments], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    
    # Backtrack to find the selected buildings
    selected = []
    w = capacity
    for i in range(valid_buildings_amounts, 0, -1):
        apartments = int(valid_buildings[i-1][2])
        if dp[i][w] != dp[i-1][w]:
            selected.append(valid_buildings[i-1])
            w -= apartments
    
    return selected

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths):
    buildings_gdf, gardens_gdf = preprocess_data(buildings_gdf, gardens_gdf, walking_paths)

    allocation = {}
    
    # Sort gardens by capacity (descending)
    gardens_sorted = gardens_gdf.sort_values('capacity', ascending=False)
    
    for idx, garden in gardens_sorted.iterrows():
        selected_buildings = knapsack_garden_allocation(garden, garden['nearby_buildings'])
        
        for building in selected_buildings:
            building_ID, _, apartments = building
            if building_ID not in allocation:
                allocation[building_ID] = garden['OBJECTID']
                gardens_gdf.loc[gardens_gdf['OBJECTID'] == garden['OBJECTID'], 'remaining_capacity'] -= apartments

    # Create GeoDataFrames for allocated and not allocated buildings
    allocated_buildings = buildings_gdf[buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()
    allocated_buildings['allocated_garden'] = allocated_buildings['OBJECTID'].map(allocation)

    not_allocated_buildings = buildings_gdf[~buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()

    # Merge allocated buildings with garden information
    allocated_buildings = allocated_buildings.merge(
        gardens_gdf[['OBJECTID', 'ADDRESS']],
        left_on='allocated_garden',
        right_on='OBJECTID',
        suffixes=('_building', '_garden')
    )

    # Rename columns for clarity
    allocated_buildings = allocated_buildings.rename(columns={
        'OBJECTID_building': 'building_id',
        'OBJECTID_garden': 'garden_id',
        'ADDRESS': 'garden_address'
    })

    allocated_buildings = allocated_buildings[[
        'building_id', 'NUM_APTS_C',
        'garden_id', 'garden_address', 'geometry'
    ]]

    not_allocated_buildings = not_allocated_buildings[[
        'OBJECTID', 'NUM_APTS_C', 'geometry'
    ]]

    return allocated_buildings, not_allocated_buildings

def get_utilization(buildings_gdf, allocated_buildings):
    total_apartments = buildings_gdf['NUM_APTS_C'].sum()
    allocated_apartments = allocated_buildings['NUM_APTS_C'].sum()
    utilization = (allocated_apartments / total_apartments) * 100
    print(f"Apartment utilization: {allocated_apartments}/{total_apartments} ({utilization:.2f}%)")
    return f"{utilization:.2f}%"