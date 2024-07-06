def make_arcgis_query_requests(xmin, ymin, xmax, ymax):
    url = "https://gisviewer.jerusalem.muni.il/arcgis/rest/services/BaseLayers/MapServer/30/query"
    
    params = {
        "where": "1=1",
        "text": "",
        "objectIds": "",
        "time": "",
        "geometry": f'{{"xmin": {xmin}, "ymin": {ymin}, "xmax": {xmax}, "ymax": {ymax}}}',
        "geometryType": "esriGeometryEnvelope",
        "inSR": '{"wkid": 2039, "latestWkid": 2039}',
        "spatialRel": "esriSpatialRelIntersects",
        "relationParam": "",
        "outFields": "",
        "returnGeometry": "true",
        "maxAllowableOffset": "",
        "geometryPrecision": "",
        "outSR": "",
        "returnIdsOnly": "false",
        "returnCountOnly": "false",
        "orderByFields": "",
        "groupByFieldsForStatistics": "",
        "outStatistics": "",
        "returnZ": "false",
        "returnM": "false",
        "gdbVersion": "",
        "returnDistinctValues": "false",
        "returnTrueCurves": "false",
        "resultOffset": "",
        "resultRecordCount": "",
        "f": "pjson"
    }

    headers = {
        "authority": "gisviewer.jerusalem.muni.il",
        "Priority": "u=0, i",
        "Referer": "https://gisviewer.jerusalem.muni.il/arcgis/rest/services/BaseLayers/MapServer/30/query?where=1%3D1&text=&objectIds=&time=&geometry=%7B%22xmin%22%3A+215933%2C%22ymin%22%3A+630000%2C%22xmax%22%3A+217288%2C%22ymax%22%3A+630900%7D&geometryType=esriGeometryPolygon&inSR=%7B%22wkid%22%3A2039%2C%22latestWkid%22%3A2039%7D&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=&returnGeometry=true&maxAllowableOffset=&geometryPrecision=&outSR=&returnIdsOnly=false&returnCountOnly=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&returnZ=false&returnM=false&gdbVersion=&returnDistinctValues=false&returnTrueCurves=false&resultOffset=&resultRecordCount=&f=html"
    }
    
    response = requests.get(url, params=params, headers=headers)

    
    if response.status_code == 200:
        return response.json()  # Assuming the response is JSON data
    else:
        return f"Error: {response.status_code}"