import pandas as pd
from shapely.ops import unary_union

def calculate_distance(building, garden):
    return building.distance(garden)

def allocate_buildings_to_gardens(buildings_gdf, gardens_gdf):
    # Convert geometry to centroids for distance calculation
    buildings_gdf['centroid'] = buildings_gdf['geometry'].centroid
    gardens_gdf['centroid'] = gardens_gdf['geometry'].centroid
    
    # Initialize columns to track allocations
    buildings_gdf['allocated_garden'] = None
    gardens_gdf['allocated_apartments_amount'] = 0
    gardens_gdf['allocated_buildings'] = [[] for _ in range(len(gardens_gdf))]
    
    # Convert 0.93 km to meters
    max_distance = 930
    
    for g_index, garden in gardens_gdf.iterrows():
        # Track the remaining capacity of the garden
        remaining_capacity = (garden['Shape_STAr'] / 1000) * 90
        
        # Filter buildings within the distance
        nearby_buildings = buildings_gdf[buildings_gdf['centroid'].distance(garden['centroid']) <= max_distance]
        
        # Sort nearby buildings by distance to the garden
        nearby_buildings = nearby_buildings.copy()
        nearby_buildings['distance'] = nearby_buildings['centroid'].apply(lambda x: calculate_distance(x, garden['centroid']))
        nearby_buildings.sort_values('distance', inplace=True)
        
        for b_index, building in nearby_buildings.iterrows():
            if remaining_capacity <= 0:
                break
            if pd.isna(building['allocated_garden']) and building['NUM_APTS_C'] <= remaining_capacity:
                # Allocate building to the garden
                buildings_gdf.at[b_index, 'allocated_garden'] = garden['OBJECTID']
                remaining_capacity -= building['NUM_APTS_C']
                gardens_gdf.at[g_index, 'allocated_apartments_amount'] += building['NUM_APTS_C']
                gardens_gdf.at[g_index, 'allocated_buildings'].append(building['OBJECTID']) 
    
    return buildings_gdf, gardens_gdf