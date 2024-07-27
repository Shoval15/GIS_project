import pyproj
from shapely.geometry import Point, Polygon
from . import distance_walk
from geojson import FeatureCollection, Feature
from shapely.geometry import mapping
from pyproj import Transformer, CRS
from shapely import wkt
import numpy as np
from shapely.strtree import STRtree
import geopandas as gpd

# Define the order of project statuses
status_order = [
    'פתיחת תיק תב"ע',
    'הפקדה',
    'תכנית מאושרת',
    'נפתח תיק היתר',
    'היתר בנייה'
]

# Function to convert a Point or Polygon to WGS84
def convert_coords(geometry, to='4326'):
    if to == '4326':
        # Define the transformer from Israel TM to WGS84 (latitude and longitude)
        transformer = pyproj.Transformer.from_proj(
            pyproj.Proj('epsg:2039'),  # Israel Transverse Mercator
            pyproj.Proj('epsg:4326'))   # WGS84 (latitude and longitude)
    else:
        # Define the transformer from WGS84 (EPSG:4326) to Israel TM (EPSG:2039)
        transformer = pyproj.Transformer.from_proj(
            pyproj.Proj('epsg:4326'),   # WGS84 (latitude and longitude)
            pyproj.Proj('epsg:2039'))   # Israel Transverse Mercator
        
    if isinstance(geometry, Point):
        lon, lat = transformer.transform(geometry.x, geometry.y)
        return Point(lon, lat)
    elif isinstance(geometry, Polygon):
        exterior_ring = []
        if to == '4326':
            exterior_ring = [transformer.transform(x, y) for x, y in geometry.exterior.coords]
        else:
            exterior_ring = [transformer.transform(y, x) for x, y in geometry.exterior.coords]
        return Polygon(exterior_ring)
 
# Function to convert a string "(x, y)" to a Point object
def str_to_point(s):
    x, y = map(float, s.strip("()").split(","))
    return Point(x, y)

def calculate_max_distance(building_geom, garden_geom):
    if isinstance(building_geom, Point):
        # Calculate distance from the building point to all garden vertices
        return max(building_geom.distance(garden_geom.exterior))
    
    # Calculate distance from the building's bounding box to the garden's bounding box
    building_bbox = building_geom.bounds
    garden_bbox = garden_geom.bounds
    
    # Calculate distances from each corner of the building bbox to each corner of the garden bbox
    distances = [
        building_geom.distance(Point(gx, gy))
        for gx in [garden_bbox[0], garden_bbox[2]]  # xmin, xmax
        for gy in [garden_bbox[1], garden_bbox[3]]  # ymin, ymax
    ]
    
    return max(distances)

def calculate_distance(building, garden):
    return building.distance(garden)

def calculate_min_distance(building_geom, garden_geom):
    if isinstance(building_geom, Point):
        # Calculate distance from the building point to the garden centroid
        return building_geom.distance(garden_geom.centroid)
    else:
        # Calculate distance from the building centroid to the garden centroid
        return building_geom.centroid.distance(garden_geom.centroid)

def find_nearby_buildings(garden, buildings_gdf, G, max_distance=0.93):
    distances = []
    for _, building in buildings_gdf.iterrows():
        dist = distance_walk.calculate_walk_distance(G, garden.geometry.centroid, building.geometry.centroid)
        if dist <= max_distance and building['units_e'] > 0:
            distances.append((building['OBJECTID'], dist, building['units_e']))
    return sorted(distances, key=lambda x: x[1])  # Sort by distance

def remove_empty_buildings(buildings_gdf):
    invalid_values = [0, None, np.nan, '']
    #  filter the GeoDataFrame (no null, no empty, no 0)
    filtered_buildings_gdf = buildings_gdf[
        ~buildings_gdf['units_e'].isin(invalid_values) & 
        (buildings_gdf['units_e'].notna()) &
        (buildings_gdf['units_e'] != '')
    ]

    # ensure it's greater than 0
    filtered_buildings_gdf = filtered_buildings_gdf[filtered_buildings_gdf['units_e'] > 0]
    return filtered_buildings_gdf


def preprocess_data(buildings_gdf, gardens_gdf, G, apartment_type, project_status, max_distance,  meters_for_resident, residents):
    
    buildings_gdf = remove_empty_buildings(buildings_gdf)
    # Filter buildings based on apartment_type
    if apartment_type == "existing":
        filtered_buildings = buildings_gdf[buildings_gdf['gen_status'] == 'exists']
    else:
        # Further filter based on project_status if needed
        if project_status:
            # Find the index of the current project_status
            current_status_index = status_order.index(project_status)
            
            # Create a list of valid statuses (current and all previous)
            valid_statuses = status_order[:current_status_index + 1]
            if 'תכנית מאושרת' in valid_statuses:
                valid_statuses.append('מאושרת')
            # Filter the buildings
            buildings_gdf = buildings_gdf[
                (buildings_gdf['gen_status'] != 'renewal') | 
                (buildings_gdf['tichnun_s'].isin(valid_statuses))
            ]
        # Remove 'exists' buildings that overlap with 'renewal' buildings
        renewal_buildings = buildings_gdf[buildings_gdf['gen_status'] == 'renewal']
        exists_buildings = buildings_gdf[buildings_gdf['gen_status'] == 'exists']
        # Create spatial index for renewal buildings
        sindex = STRtree(renewal_buildings.geometry.values)

        def check_overlap(geom):
            possible_matches_idx = sindex.query(geom)
            if len(possible_matches_idx) > 0:
                possible_matches = renewal_buildings.iloc[possible_matches_idx]
                intersections = possible_matches.geometry.intersection(geom)
                overlap_ratio = intersections.area / geom.area
                return (overlap_ratio > 0.8).any()
            return False

        # Apply the check_overlap function to exists_buildings
        to_remove = exists_buildings[exists_buildings.geometry.apply(check_overlap)]['OBJECTID'].tolist()

        # Remove the identified buildings
        buildings_gdf = buildings_gdf[~buildings_gdf['OBJECTID'].isin(to_remove)]
        
        filtered_buildings = buildings_gdf[~buildings_gdf['OBJECTID'].isin(to_remove)]
        result = filtered_buildings['units_e'].where(filtered_buildings['units_p'].isnull(), filtered_buildings['units_p'])
        filtered_buildings.loc[:, 'units_e'] = result.infer_objects(copy=False)
    # Calculate garden capacities
    gardens_gdf['capacity'] = (gardens_gdf['Shape.STArea()'] / (meters_for_resident * residents)).astype(int)
    gardens_gdf['remaining_capacity'] = gardens_gdf['capacity']
    
    # Calculate distances between gardens and buildings
    gardens_gdf['nearby_buildings'] = gardens_gdf.apply(lambda x: find_nearby_buildings(x, filtered_buildings, G,  max_distance), axis=1)
    return filtered_buildings, gardens_gdf

def swap_coordinates(geom):
    if geom['type'] == 'Point':
        geom['coordinates'] = geom['coordinates'][::-1]
    elif geom['type'] in ['LineString', 'MultiPoint']:
        geom['coordinates'] = [coord[::-1] for coord in geom['coordinates']]
    elif geom['type'] in ['Polygon', 'MultiLineString']:
        geom['coordinates'] = [[coord[::-1] for coord in ring] for ring in geom['coordinates']]
    elif geom['type'] == 'MultiPolygon':
        geom['coordinates'] = [[[coord[::-1] for coord in ring] for ring in polygon] for polygon in geom['coordinates']]
    return geom

def create_allocated_layer(gdf):
    features = []
    for idx, row in gdf.iterrows():
        # Convert the geometry to GeoJSON format and swap coordinates
        geom = mapping(row['geometry'])
        swapped_geom = swap_coordinates(geom)
        
        # Create a new feature with selected properties
        new_feature = Feature(
            geometry=swapped_geom,
            properties={
                'OBJECTID_building': row['OBJECTID_building'],
                'OBJECTID_garden': row['OBJECTID_garden'],
                'units_e': row['units_e'],
                'address': row['address'],
                'YEUD': row['YEUD'],
                'Descr': row['Descr'],
                'capacity': row['capacity'],
                'remaining_capacity': row['remaining_capacity'],
                'gen_status': row['gen_status']
            }
        )
        features.append(new_feature)
    
    return FeatureCollection(features)

def create_not_allocated_layer(not_allocated_buildings):
    features = []
    for idx, row in not_allocated_buildings.iterrows():
        # Convert the geometry to GeoJSON format and swap coordinates
        geom = mapping(row['geometry'])
        swapped_geom = swap_coordinates(geom)

        # Create a new feature with selected properties
        new_feature = Feature(
            geometry=swapped_geom,
            properties={
                'OBJECTID': row['OBJECTID'],
                'units_e': row['units_e'],
                'address': row['address'],
                'gen_status': row['gen_status']
            }
        )
        features.append(new_feature)
    
    return FeatureCollection(features)

def create_gardens_layer(gardens_gdf):
    features = []
    for idx, row in gardens_gdf.iterrows():
        geom = mapping(row['geometry'])
        swapped_geom = swap_coordinates(geom)
        new_feature = Feature(
            geometry=swapped_geom,
            properties={
                'OBJECTID': row['OBJECTID'],
                'YEUD': row['YEUD'],
                'Descr': row['Descr'],
                'capacity': row['capacity'],
                'remaining_capacity': row['remaining_capacity'],
                'Shape.STArea()': row['Shape.STArea()']
            }
        )
        features.append(new_feature)
    
    return FeatureCollection(features)


def check_polygon_size(polygon, min_area=10000):
    # Define the source CRS (WGS84) and target CRS (ITM - Israel Transverse Mercator)
    src_crs = CRS("EPSG:4326")
    dst_crs = CRS("EPSG:2039")
    transformer = Transformer.from_crs(src_crs, dst_crs, always_xy=True)
    # Transform the polygon coordinates to ITM
    polygon_itm_coords = [transformer.transform(x, y) for x, y in polygon.exterior.coords]
    polygon_itm = wkt.loads(f"POLYGON (({', '.join([f'{x} {y}' for x, y in polygon_itm_coords])}))")
    # Calculate the area in square meters
    area = polygon_itm.area
    if area < min_area:
        return False
    return True  # If the polygon is large enough


def filter_gdf_by_polygon(gdf, polygon):
    polygon = Polygon([(y, x) for x, y in polygon.exterior.coords])
    gdf_within_or_intersects_p = gdf[gdf.geometry.within(polygon) | gdf.geometry.intersects(polygon)]
    return gdf_within_or_intersects_p


def calculate_stats(buildings_gdf, allocated_buildings_gdf):
    total_apartments = int(buildings_gdf['units_e'].sum())
    allocated_apartments = int(allocated_buildings_gdf['units_e'].sum())
    not_allocated_apartments = total_apartments - allocated_apartments
    
    total_buildings = len(buildings_gdf)
    allocated_buildings = len(allocated_buildings_gdf)
    not_allocated_buildings = total_buildings - allocated_buildings
    
    allocation_stats = {
        "total_apartments": total_apartments,
        "allocated_apartments": allocated_apartments,
        "not_allocated_apartments": not_allocated_apartments,
        "apartment_allocation_percentage": (allocated_apartments / total_apartments) * 100 if total_apartments > 0 else 0,
        "total_buildings": total_buildings,
        "allocated_buildings": allocated_buildings,
        "not_allocated_buildings": not_allocated_buildings,
        "building_allocation_percentage": (allocated_buildings / total_buildings) * 100 if total_buildings > 0 else 0
    }

    return allocation_stats