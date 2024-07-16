import geopandas as gpd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd
from shapely.geometry import  Polygon
from . import utilities
import osmnx as ox
from urllib.parse import urlencode, quote


def make_arcgis_query_selenium(layer_number, xmin, ymin, xmax, ymax, out_fields="*", where="1=1"):
    base_url = "https://gisviewer.jerusalem.muni.il/arcgis/rest/services/BaseLayers/MapServer"
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=chrome_options)
    geometry_dict = json.loads(f'{{"xmin":{xmin},"ymin":{ymin},"xmax":{xmax},"ymax":{ymax}}}')
    params = {'geometry': json.dumps(geometry_dict)}
    # Use urlencode to convert the dictionary to a URL-encoded string
    encoded_geometry = urlencode(params) 
    encoded_out_fields = quote(out_fields)
    encoded_where = quote(where)
    try:
        # Construct the URL with the provided parameters
        url = (f"{base_url}/{layer_number}/query?"
               f"where={encoded_where}&"
               f"{encoded_geometry}&"
               f"geometryType=esriGeometryEnvelope&"
               f"inSR=%7B%22wkid%22%3A4326%2C%22latestWkid%22%3A4326%7D&"
               f"spatialRel=esriSpatialRelIntersects&"
               f"outFields={encoded_out_fields}&"
               f"returnGeometry=true&"
               f"outSR=&returnIdsOnly=false&returnCountOnly=false&"
               f"returnDistinctValues=false&returnTrueCurves=false&"
               f"f=json")
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        # Find the element containing JSON data
        data_element = driver.find_element(By.TAG_NAME, 'body')
        response_text = data_element.text
        data = json.loads(response_text)
        return data

    finally:
        driver.quit()


def import_buildings(selected_polygon):
    # Calculate bounding box (xmin, ymin, xmax, ymax)
    minx, miny, maxx, maxy = selected_polygon.bounds
    out_fields = "OBJECTID,CID,MAX_rel_he,MAX_med_he,BLDG_NUM_1,BLDG_TYPE_,NUM_FLOORS,\
                    NUM_ENTR_1,NUM_APTS_C,semel_bait,StreetName,StreetNa_1,X_1,Y_1,\
                    StreetCode,BldNum_1,Shape,Shape.STArea(),Shape.STLength()"
    # json_res = make_arcgis_query_selenium_old(minx, miny, maxx, maxy)
    json_res = make_arcgis_query_selenium('370', minx, miny, maxx, maxy, out_fields)
    features = json_res['features']
    attributes = [feature['attributes'] for feature in features]
    geometries = [feature['geometry']['rings'][0] for feature in features]
    # Convert geometries to shapely polygons
    polygons = [Polygon(geometry) for geometry in geometries]
    df = pd.DataFrame(attributes)
    gdf = gpd.GeoDataFrame(df, geometry=polygons)
    # Set the coordinate reference system (CRS)
    gdf.set_crs(epsg=json_res['spatialReference']['wkid'], inplace=True)
    gdf['geometry'] = gdf['geometry'].apply(utilities.convert_coords)
    return gdf

def import_urban_renewal(selected_polygon):
    # Calculate bounding box (xmin, ymin, xmax, ymax)
    minx, miny, maxx, maxy = selected_polygon.bounds
    out_fields = "OBJECTID, num, name, maslul, yazam, units_e, units_p, tichnun_s, date,\
                    start, info, picture, units_a, status_num, adress, schunah, Shape.STArea(), Shape"
    json_res = make_arcgis_query_selenium('183', minx, miny, maxx, maxy, out_fields)
    features = json_res['features']
    attributes = [feature['attributes'] for feature in features]
    geometries = [feature['geometry']['rings'][0] for feature in features]
    # Convert geometries to shapely polygons
    polygons = [Polygon(geometry) for geometry in geometries]
    df = pd.DataFrame(attributes)
    gdf = gpd.GeoDataFrame(df, geometry=polygons)
    # Set the coordinate reference system (CRS)
    gdf.set_crs(epsg=json_res['spatialReference']['wkid'], inplace=True)
    gdf['geometry'] = gdf['geometry'].apply(utilities.convert_coords)
    return gdf

def import_gardens(selected_polygon):
    # Calculate bounding box (xmin, ymin, xmax, ymax)
    minx, miny, maxx, maxy = selected_polygon.bounds
    out_fields = "OBJECTID, Shape.STArea(), YEUD, Descr "
    json_res = make_arcgis_query_selenium('50', minx, miny, maxx, maxy, out_fields, where='YEUD=670')
    features = json_res['features']
    attributes = [feature['attributes'] for feature in features]
    geometries = [feature['geometry']['rings'][0] for feature in features]
    # Convert geometries to shapely polygons
    polygons = [Polygon(geometry) for geometry in geometries]
    df = pd.DataFrame(attributes)
    gdf = gpd.GeoDataFrame(df, geometry=polygons)
    # Set the coordinate reference system (CRS)
    gdf.set_crs(epsg=json_res['spatialReference']['wkid'], inplace=True)
    gdf['geometry'] = gdf['geometry'].apply(utilities.convert_coords)
    return gdf

def union_building_and_renewal(buildings_gdf, renewal_gdf):
    buildings_prepared = buildings_gdf.copy()
    buildings_prepared['units_e'] = buildings_prepared['NUM_APTS_C']
    buildings_prepared['address'] = buildings_prepared['StreetName'] + ' ' + buildings_prepared['BldNum_1'].astype(str)
    buildings_prepared['units_p'] = None
    buildings_prepared['maslul'] = None
    buildings_prepared['yazam'] = None
    buildings_prepared['tichnun_s'] = None
    buildings_prepared['status_num'] = None
    buildings_prepared['gen_status'] = 'exists'
    buildings_prepared = buildings_prepared[['OBJECTID', 'Shape.STArea()', 'geometry', 'units_e', 'units_p',
                                              'address', 'maslul', 'yazam', 'tichnun_s', 'status_num', 'gen_status']]
    # Prepare renewal_gdf
    renewal_prepared = renewal_gdf.copy()
    renewal_prepared['units_e'] = renewal_prepared['units_e']
    renewal_prepared['address'] = renewal_prepared['adress']
    renewal_prepared['units_p'] = renewal_prepared['units_a']
    renewal_prepared['gen_status'] = 'renewal'
    renewal_prepared = renewal_prepared[['OBJECTID', 'Shape.STArea()', 'geometry', 'units_e', 'units_p',
                                          'address', 'maslul', 'yazam', 'tichnun_s', 'status_num', 'gen_status']]
    # Union the two prepared GeoDataFrames
    result_gdf = pd.concat([buildings_prepared, renewal_prepared], ignore_index=True)
    result_gdf = gpd.GeoDataFrame(result_gdf, geometry='geometry')
    # reset the index
    result_gdf = result_gdf.reset_index(drop=True)
    return result_gdf

def import_walking_paths(selected_polygon):
    # selected_polygon = utilities.convert_coords(selected_polygon)
    # Calculate bounding box (xmin, ymin, xmax, ymax)
    minx, miny, maxx, maxy = selected_polygon.bounds
    mode = 'walk'
    # Create the graph of the area from OSM data. It will download the data and create the graph
    G = ox.graph_from_bbox(bbox=(miny, maxy, minx, maxx), network_type=mode)
    # OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G
