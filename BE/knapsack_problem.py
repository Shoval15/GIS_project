
from distance_walk import calculate_walk_distance

def preprocess_data(buildings_gdf, gardens_gdf, walking_paths):
    # Calculate garden capacities
    gardens_gdf['capacity'] = (gardens_gdf['Shape_STAr'] / 1000 * 90).astype(int)
    
    # Calculate distances between gardens and buildings
    for _, garden in gardens_gdf.iterrows():
        garden_buildings = []
        for _, building in buildings_gdf.iterrows():
            dist = calculate_walk_distance(walking_paths, garden.geometry.centroid, building.geometry.centroid)
            if dist <= 0.93:
                garden_buildings.append((building['OBJECTID'], dist, building['NUM_APTS_C']))
        garden['nearby_buildings'] = sorted(garden_buildings, key=lambda x: x[1])
    
    return buildings_gdf, gardens_gdf

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths):
    buildings_gdf, gardens_gdf = preprocess_data(buildings_gdf, gardens_gdf, walking_paths)
    
    allocated_buildings = []
    not_allocated_buildings = set(buildings_gdf['OBJECTID'])
    
    # Sort gardens by capacity (descending)
    gardens_sorted = gardens_gdf.sort_values('capacity', ascending=False)
    
    for _, garden in gardens_sorted.iterrows():
        remaining_capacity = garden['capacity']
        for building_id, _, apartments in garden['nearby_buildings']:
            if building_id in not_allocated_buildings and apartments <= remaining_capacity:
                allocated_buildings.append((building_id, garden['OBJECTID']))
                not_allocated_buildings.remove(building_id)
                remaining_capacity -= apartments
                if remaining_capacity <= 0:
                    break
    
    # Create GeoDataFrames for allocated and not allocated buildings
    allocated_gdf = buildings_gdf[buildings_gdf['OBJECTID'].isin([b[0] for b in allocated_buildings])].copy()
    allocated_gdf['allocated_garden'] = [b[1] for b in allocated_buildings]
    
    not_allocated_gdf = buildings_gdf[buildings_gdf['OBJECTID'].isin(not_allocated_buildings)].copy()
    
    # Merge allocated buildings with garden information
    allocated_gdf = allocated_gdf.merge(
        gardens_gdf[['OBJECTID', 'MAVAT_NAME', 'ADDRESS']],
        left_on='allocated_garden',
        right_on='OBJECTID',
        suffixes=('_building', '_garden')
    )
    
    allocated_gdf = allocated_gdf.rename(columns={
        'OBJECTID_building': 'building_id',
        'OBJECTID_garden': 'garden_id',
        'MAVAT_NAME': 'garden_name',
        'ADDRESS': 'garden_address'
    })
    
    allocated_gdf = allocated_gdf[[
        'building_id', 'BLDG_NUM', 'BLDG_TYPE', 'NUM_APTS_C', 'StreetName1',
        'garden_id', 'garden_name', 'garden_address', 'geometry'
    ]]
    
    not_allocated_gdf = not_allocated_gdf[[
        'OBJECTID', 'BLDG_NUM', 'BLDG_TYPE', 'NUM_APTS_C', 'StreetName1', 'geometry'
    ]]
    
    return allocated_gdf, not_allocated_gdf

def get_utilization(buildings_gdf, allocated_gdf):
    # Calculate and print utilization
    total_apartments = buildings_gdf['NUM_APTS_C'].sum()
    allocated_apartments = allocated_gdf['NUM_APTS_C'].sum()
    utilization = (allocated_apartments / total_apartments) * 100

    print(f"\nUtilization: {allocated_apartments}/{total_apartments} apartments ({utilization:.2f}%)")
    return f"{utilization:.2f}%"