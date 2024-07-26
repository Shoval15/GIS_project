from . import utilities
import json

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status,  meters_for_resident, residents):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths, apartment_type, project_status, distance,  meters_for_resident, residents)
    allocation = {}    
    # Sort gardens by capacity (descending)
    gardens_sorted = gardens_gdf.sort_values('capacity', ascending=False)

    for idx, garden in gardens_sorted.iterrows():
        remaining_capacity = garden['remaining_capacity']
        for building_ID, _, apartments in garden['nearby_buildings']:
            if building_ID not in allocation and  remaining_capacity >= apartments:
                allocation[building_ID] = garden['OBJECTID']
                gardens_gdf.loc[gardens_gdf['OBJECTID'] == garden['OBJECTID'], 'remaining_capacity'] -= apartments
                remaining_capacity -= apartments
                if remaining_capacity <= 0:
                    break  # Move to next garden if this one is full

    # Create GeoDataFrames for allocated and not allocated buildings
    allocated_buildings = buildings_gdf[buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()
    allocated_buildings['allocated_garden'] = allocated_buildings['OBJECTID'].map(allocation)
    not_allocated_buildings = buildings_gdf[~buildings_gdf['OBJECTID'].isin(allocation.keys())].copy()

    # Merge allocated buildings with garden details
    merged_data = allocated_buildings.merge(
        gardens_gdf[['OBJECTID', 'Shape.STArea()', 'YEUD', 'Descr', 'capacity', 'remaining_capacity']], 
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

    allocation_stats = utilities.calculate_stats(buildings_gdf, merged_data)
    return merged_data, not_allocated_buildings, allocation_stats, gardens_gdf