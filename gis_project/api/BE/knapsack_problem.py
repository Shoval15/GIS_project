from . import utilities
import json
import geopandas as gpd
import numpy as np

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths, apartment_type, project_status, distance)
    
    # Create a list of gardens with their capacities
    gardens = [(garden['OBJECTID'], garden['capacity']) for _, garden in gardens_gdf.iterrows()]
    
    # Create a list of buildings with their apartment counts
    buildings = [(building['OBJECTID'], building['apartments']) for _, building in buildings_gdf.iterrows()]
    
    # Sort buildings by apartment count (descending)
    buildings.sort(key=lambda x: x[1], reverse=True)
    
    def knapsack(gardens, buildings):
        n = len(buildings)
        m = sum(garden[1] for garden in gardens)
        
        # Initialize the dynamic programming table
        dp = [[0 for _ in range(m + 1)] for _ in range(n + 1)]
        
        # Fill the dp table
        for i in range(1, n + 1):
            for w in range(1, m + 1):
                if buildings[i-1][1] <= w:
                    dp[i][w] = max(buildings[i-1][1] + dp[i-1][w-buildings[i-1][1]], dp[i-1][w])
                else:
                    dp[i][w] = dp[i-1][w]
        
        # Backtrack to find the solution
        allocation = {}
        i, w = n, m
        while i > 0 and w > 0:
            if dp[i][w] != dp[i-1][w]:
                building_id = buildings[i-1][0]
                # Find the first garden with enough capacity
                for garden_id, capacity in gardens:
                    if capacity >= buildings[i-1][1]:
                        allocation[building_id] = garden_id
                        gardens = [(g_id, cap - buildings[i-1][1]) if g_id == garden_id else (g_id, cap) for g_id, cap in gardens]
                        break
                w -= buildings[i-1][1]
            i -= 1
        
        return allocation

    # Run the knapsack algorithm
    allocation = knapsack(gardens, buildings)

    # Create GeoDataFrames for allocated and not allocated buildings
    allocated_buildings = buildings_gdf[buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()
    allocated_buildings['allocated_garden'] = allocated_buildings['OBJECTID'].map(allocation)
    not_allocated_buildings = buildings_gdf[~buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()

    # Merge allocated buildings with garden details
    merged_data = allocated_buildings.merge(
        gardens_gdf[['OBJECTID', 'Shape.STArea()', 'YEUD', 'Descr', 'capacity']], 
        left_on='allocated_garden', 
        right_on='OBJECTID', 
        suffixes=('_building', '_garden')
    )

    # Rename columns to avoid confusion
    merged_data = merged_data.rename(columns={
        'OBJECTID_building': 'OBJECTID_building',
        'OBJECTID_garden': 'OBJECTID_garden',
        'Shape.STArea()_building': 'Shape.STArea()_building',
        'Shape.STArea()_garden': 'Shape.STArea()_garden',
    })

    # Convert to GeoJSON
    geojson_data = json.loads(merged_data.to_json())

    # Write to JSON file
    with open('allocated_buildings_with_gardens.json', 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    # Calculate allocation statistics
    total_apartments = buildings_gdf['apartments'].sum()
    allocated_apartments = allocated_buildings['apartments'].sum()
    not_allocated_apartments = total_apartments - allocated_apartments
    allocation_stats = {
        "total_apartments": int(total_apartments),
        "allocated_apartments": int(allocated_apartments),
        "not_allocated_apartments": int(not_allocated_apartments),
        "allocation_percentage": (allocated_apartments / total_apartments) * 100 if total_apartments > 0 else 0
    }

    # Update remaining capacity for gardens
    for garden_id, capacity in gardens:
        gardens_gdf.loc[gardens_gdf['OBJECTID'] == garden_id, 'remaining_capacity'] = capacity

    return merged_data, not_allocated_buildings, geojson_data, allocation_stats, gardens_gdf