import networkx as nx
import osmnx as ox
import math

def calculate_walk_distance(G, orig, dest):
    # Find the nearest node
    closest_to_orig  = ox.distance.nearest_nodes(G, orig.x, orig.y)
    closest_to_dest  = ox.distance.nearest_nodes(G, dest.x, dest.y)
    
    try:
        # find shortest path
        routes = ox.routing.shortest_path(G, closest_to_orig, closest_to_dest, weight="length")
        # Calculate the length of the route
        route_length = nx.shortest_path_length(G, closest_to_orig, closest_to_dest, weight="length")
        # # plot the shortes path
        # fig, ax = ox.plot_graph_route(G, routes, route_color="r", 
        #                         route_linewidth=6, node_size=0)
    except nx.NetworkXNoPath:
        print("No path found between the origin and destination.")
        return math.inf
    return route_length