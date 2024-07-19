from . import utilities
import json
import geopandas as gpd

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths, apartment_type, project_status, distance)
    allocation = {}
    total_apartments = len(buildings_gdf)
    allocated_apartments = 0
    
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

    # Convert to GeoJSON
    geojson_data = json.loads(merged_data.to_json())

    # Write to JSON file
    with open('allocated_buildings_with_gardens.json', 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)

    # Calculate allocation statistics
    allocated_apartments = len(allocated_buildings)
    not_allocated_apartments = total_apartments - allocated_apartments
    allocation_stats = {
        "total_apartments": total_apartments,
        "allocated_apartments": allocated_apartments,
        "not_allocated_apartments": not_allocated_apartments,
        "allocation_percentage": (allocated_apartments / total_apartments) * 100 if total_apartments > 0 else 0
    }
    return merged_data, not_allocated_buildings, geojson_data, allocation_stats, gardens_gdf