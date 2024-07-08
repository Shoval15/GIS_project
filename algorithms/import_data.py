import geopandas as gpd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import pandas as pd
from shapely.geometry import  Polygon, box
from utilities import convert_to_wgs84
import networkx as nx
import osmnx as ox


def make_arcgis_query_selenium(xmin, ymin, xmax, ymax):
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL errors
    driver = webdriver.Chrome(options=chrome_options)
        
    try:
        # Navigate to the URL
        url = f"https://gisviewer.jerusalem.muni.il/arcgis/rest/services/BaseLayers/MapServer/30/query?where=1%3D1&text=&objectIds=&time=&geometry=%7B%22xmin%22%3A{xmin}%2C%22ymin%22%3A{ymin}%2C%22xmax%22%3A{xmax}%2C%22ymax%22%3A{ymax}%7D&geometryType=esriGeometryEnvelope&inSR=%7B%22wkid%22%3A2039%2C%22latestWkid%22%3A2039%7D&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=OBJECTID%2CSTRT_CODE1%2CStreetName1%2CBLDG_NUM%2CBLDG_TYPE%2CBLDG_CH%2CNUM_FLOORS%2CNUM_ENTR%2CNUM_APTS_C%2Clayer%2CSTRT_CODE2%2CStreetName2%2CShape%2CShape.STArea%28%29%2CShape.STLength%28%29&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&returnTrueCurves=false&resultOffset=&resultRecordCount=&f=json"
        driver.get(url)
        # Get the inner text of the HTML body
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        # Find the element containing JSON data (assuming it's within a <pre> tag)
        data_element = driver.find_element(By.TAG_NAME, 'body')
        response_text = data_element.text
        
        # Parse the JSON response
        data = json.loads(response_text)

        return data

    finally:
        driver.quit()  # Close the WebDriver session

def import_buildings(selected_polygon):
    # Calculate bounding box (xmin, ymin, xmax, ymax)
    minx, miny, maxx, maxy = selected_polygon.bounds
    json_res = make_arcgis_query_selenium(minx, miny, maxx, maxy)
    features = json_res['features']
    attributes = [feature['attributes'] for feature in features]
    geometries = [feature['geometry']['rings'][0] for feature in features]
    # Convert geometries to shapely polygons
    polygons = [Polygon(geometry) for geometry in geometries]
    # Create a DataFrame from attributes
    df = pd.DataFrame(attributes)
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=polygons)
    # Set the coordinate reference system (CRS)
    gdf.set_crs(epsg=json_res['spatialReference']['wkid'], inplace=True)
    gdf['geometry'] = gdf['geometry'].apply(convert_to_wgs84)
    return gdf

def import_land_designations(selected_polygon):
    # Load the shapefile
    land_designations_path = r'land_designations\GPL0.shp'
    data = gpd.read_file(land_designations_path)
    
    # Filter data for 'שטח ציבורי פתוח'
    gardens_data = data[data['MAVAT_NAME'] == 'שטח ציבורי פתוח']
    gardens_gdf = gpd.GeoDataFrame(gardens_data, geometry='geometry')
    # Ensure selected_polygon is a GeoSeries if it isn't already
    if not isinstance(selected_polygon, gpd.GeoSeries):
        selected_polygon = gpd.GeoSeries([selected_polygon])
    
    # Filter gardens_gdf to only include those within the selected_polygon
    filtered_gardens_gdf = gardens_gdf[gardens_gdf.geometry.within(selected_polygon.unary_union)]
    filtered_gardens_gdf['geometry'] = filtered_gardens_gdf['geometry'].apply(convert_to_wgs84)
    filtered_gardens_gdf['OBJECTID'] = filtered_gardens_gdf.index

    return filtered_gardens_gdf

def import_walking_paths(selected_polygon):
    selected_polygon = convert_to_wgs84(selected_polygon)
    # Calculate bounding box (xmin, ymin, xmax, ymax)
    minx, miny, maxx, maxy = selected_polygon.bounds
    
    mode = 'walk'
    # Create the graph of the area from OSM data. It will download the data and create the graph
    G = ox.graph_from_bbox( maxx, minx, maxy, miny, network_type=mode)

    # OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    return G
    fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)

    # find the shortest path (by distance)
    # between these nodes then plot it
    orig = list(G)[8]
    dest = list(G)[50]

    # find k-shortest path
    routes = ox.routing.shortest_path(G, orig, dest, weight="length")
    print(routes)
    # plot the shortes path
    fig, ax = ox.plot_graph_route(G, routes, route_color="r", 
                              route_linewidth=6, node_size=0)
