from . import utilities

def preprocess_data(buildings_gdf, gardens_gdf, G):
    # Calculate garden capacities
    gardens_gdf['capacity'] = (gardens_gdf['Shape_STAr'] / 1000 * 90).astype(int)
    gardens_gdf['remaining_capacity'] = gardens_gdf['capacity']
    
    # Calculate distances between gardens and buildings
    gardens_gdf['nearby_buildings'] = gardens_gdf.apply(lambda x: utilities.find_nearby_buildings(x, buildings_gdf, G), axis=1)
    
    return buildings_gdf, gardens_gdf

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths):
    buildings_gdf, gardens_gdf = preprocess_data(buildings_gdf, gardens_gdf, walking_paths)

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
        'building_id', 'NUM_APTS_C',
        'garden_id', 'garden_address', 'geometry'
    ]]

    not_allocated_buildings = not_allocated_buildings[[
        'OBJECTID', 'NUM_APTS_C', 'geometry'
    ]]

    return allocated_buildings, not_allocated_buildings, gardens_gdf

def get_utilization(buildings_gdf, allocated_buildings):
    total_apartments = buildings_gdf['NUM_APTS_C'].sum()
    allocated_apartments = allocated_buildings['NUM_APTS_C'].sum()
    utilization = (allocated_apartments / total_apartments) * 100
    print(f"Apartment utilization: {allocated_apartments}/{total_apartments} ({utilization:.2f}%)")
    return f"{utilization:.2f}%"