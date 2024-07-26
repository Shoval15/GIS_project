from . import utilities
import json
import geopandas as gpd
import numpy as np
from collections import defaultdict

def garden_centric_allocation(buildings_gdf, gardens_gdf, walking_paths, distance, apartment_type, project_status, meters_for_resident, residents):
    buildings_gdf, gardens_gdf = utilities.preprocess_data(buildings_gdf, gardens_gdf, walking_paths, apartment_type, project_status, distance, meters_for_resident, residents)
    
    allocation = defaultdict(list)
    
    # Sort gardens by capacity (descending)
    gardens_sorted = gardens_gdf.sort_values('capacity', ascending=False)

    # Multiple iterations
    for pass_num in range(3): 
        for idx, garden in gardens_sorted.iterrows():
            remaining_capacity = garden['remaining_capacity']
            nearby_buildings = sorted(garden['nearby_buildings'], key=lambda x: x[1])  # Sort by distance
            
            for building_ID, _, apartments in nearby_buildings:
                if building_ID not in [b[0] for b in allocation[garden['OBJECTID']]] and remaining_capacity > 0:
                    apartments_to_allocate = min(apartments, remaining_capacity)
                    allocation[garden['OBJECTID']].append((building_ID, apartments_to_allocate))
                    gardens_gdf.loc[gardens_gdf['OBJECTID'] == garden['OBJECTID'], 'remaining_capacity'] -= apartments_to_allocate
                    remaining_capacity -= apartments_to_allocate                    
                    if remaining_capacity <= 0:
                        break

    # Create GeoDataFrames for allocated and not allocated buildings
    allocated_building_ids = [b[0] for alloc in allocation.values() for b in alloc]
    allocated_buildings = buildings_gdf[buildings_gdf['OBJECTID'].isin(allocated_building_ids)].copy()
    allocated_buildings['allocated_garden'] = allocated_buildings['OBJECTID'].map({b: g for g, alloc in allocation.items() for b, _ in alloc})
    not_allocated_buildings = buildings_gdf[~buildings_gdf['OBJECTID'].isin(allocated_building_ids)].copy()

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

    # Convert to GeoJSON
    geojson_data = json.loads(merged_data.to_json())

    # Write to JSON file
    with open('allocated_buildings_with_gardens.json', 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)


    with open('not_allocated_buildings.json', 'w', encoding='utf-8') as f:
        geojson_data = json.loads(not_allocated_buildings.to_json())
        json.dump(geojson_data, f, ensure_ascii=False, indent=4)


    # Write to JSON file
    with open('gardens_after_allocation.json', 'w', encoding='utf-8') as f:
        geojson_data_gardens = gardens_gdf.to_json()
        f.write(geojson_data_gardens)

    allocation_stats = utilities.calculate_stats(buildings_gdf, merged_data)
    
    return merged_data, not_allocated_buildings, allocation_stats, gardens_gdf