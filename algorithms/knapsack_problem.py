import numpy as np
import utilities 

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

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, num_apartments_col):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths)

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
        'building_id', num_apartments_col,
        'garden_id', 'garden_address', 'geometry'
    ]]

    not_allocated_buildings = not_allocated_buildings[[
        'OBJECTID', num_apartments_col, 'geometry'
    ]]

    return allocated_buildings, not_allocated_buildings
