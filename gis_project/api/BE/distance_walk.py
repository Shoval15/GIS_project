import networkx as nx
import osmnx as ox
import math
from shapely.geometry import Point

def calculate_walk_distance(G, orig, dest):
    # Ensure orig and dest are Point objects
    if not isinstance(orig, Point):
        orig = Point(orig)
    if not isinstance(dest, Point):
        dest = Point(dest)
    
    # Find the nearest network nodes to the origin and destination points
    orig_node = ox.distance.nearest_nodes(G, orig.y, orig.x)
    dest_node = ox.distance.nearest_nodes(G, dest.y, dest.x)
    try:
        # Calculate the shortest path
        route = nx.shortest_path(G, orig_node, dest_node, weight='time')
        distance = nx.path_weight(G, route, weight='length')
        return distance
    except nx.NetworkXNoPath:
        print("No path found between the given points.")
        return math.inf
