import utilities

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, num_apartments_col):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths)
    allocation = {}
    # Sort gardens by capacity (descending)
    gardens_sorted = gardens_gdf.sort_values('capacity', ascending=False)
    
    for idx, garden in gardens_sorted.iterrows():
        for building_ID, _, apartments in garden['nearby_buildings']:
            if building_ID not in allocation and garden['remaining_capacity'] >= apartments:
                allocation[building_ID] = garden['OBJECTID']
                gardens_gdf.loc[gardens_gdf['OBJECTID'] == garden['OBJECTID'], 'remaining_capacity'] -= apartments
                if garden['remaining_capacity'] <= 0:
                    break  # Move to next garden if this one is full

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

    return allocated_buildings, not_allocated_buildings, gardens_gdf

