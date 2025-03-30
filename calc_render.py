import pandas as pd
import networkx as nx
import scipy
import numpy as np
import os
import json

def read_input(edges, attributes):
    """Takes in two csv files. The directionality of the edge will be FROM rows TO columns
    Outputs a dict that is formatted nicely for other functions. This is the first function you call!"""
    
    df1 = pd.read_csv(edges, index_col=0)
    df2 = pd.read_csv(attributes, index_col=0)

    graph_dict = {}
    seen_edges = set()

    for row in df1.index:
        for col in df1.columns:
            value1 = df1.at[row, col]
            edge = tuple(sorted((row, col)))  # (A, B) and (B, A) are the same

            # Stopping double counting and self-loops
            if edge not in seen_edges and value1 != 0 and row != col:
                # Ensure "targets" is correctly nested inside each node
                graph_dict.setdefault(row, {}).setdefault("targets", {})
                graph_dict.setdefault(col, {}).setdefault("targets", {})

                # Add edge weight under "targets"
                graph_dict[row]["targets"][col] = value1
                seen_edges.add(edge)

        # match node from new file
        if row in df2.index:
            graph_dict.setdefault(row, {}).setdefault("attributes", {})
            for attr_name in df2.columns:  # Use the correct column names from df2
                graph_dict[row]["attributes"][attr_name] = int(df2.at[row, attr_name])

    #print(json.dumps(graph_dict, indent=4))
    return graph_dict

def make_x_graph(graph_dict, directed=False):
    """makes dict from input reader function above and makes it an object in networkx. This
    is the 2nd function and is needed for calculations"""
    
    G = nx.DiGraph() if directed else nx.Graph()

    # nodes w attributes
    for node, data in graph_dict.items():
        attributes = data.get("attributes", {})
        G.add_node(node, **attributes)

    # edges
    for node, data in graph_dict.items():
        targets = data.get("targets", {})
        for target, weight in targets.items():
            G.add_edge(node, target, weight=weight)

    return G

import dash
import dash_cytoscape as cyto
from dash import html
import math

def format_for_dash_cytoscape(graph_dict, G):
    """Converts the graph dictionary into a format suitable for Dash Cytoscape (directed edges)."""
    
    elements = []
    node_positions = calculate_circular_positions(graph_dict, G)  # Get node positions dynamically

    # Add nodes with positions
    for node, data in graph_dict.items():
        node_data = {'id': node, 'label': node}  # Ensure ID and label exist
        node_data.update(data.get("attributes", {}))  # Add any attributes (like color, size)

        # Add to elements list with computed positions
        elements.append({'data': node_data, 'position': node_positions[node]})  

    # Add directional edges FROM node TO its specific targets
    for node, data in graph_dict.items():
        if "targets" in data:  # Check if targets exist for this node
            for target, weight in data["targets"].items():
                # Only add edges that are explicitly in the targets dictionary
                elements.append({'data': {'source': node, 'target': target, 'weight': weight}})

    return elements

def node_calculation(G):
    '''botton box calculations for each node, returns 3 dicts and takes a networkx object'''
    dc = nx.degree_centrality(G)
    bc = nx.betweenness_centrality(G)
    cc = nx.closeness_centrality(G)
    return dc,bc,cc

def network_calculations(G):
    '''Top boc calculations for entire network, takes networkx object and outputs two values'''
    pass
 

def calculate_positions(graph_dict, G = None):
    """Dynamically spaces out nodes in a circular layout."""
    num_nodes = len(graph_dict)
    angle_step = 2 * math.pi / max(num_nodes, 1)  # Angle between nodes

    positions = {}
    radius = 600  # Distance from the center
    center_x, center_y = 300, 300  # Center of the graph

    for i, node in enumerate(graph_dict.keys()):
        x = center_x + radius * math.cos(i * angle_step)
        y = center_y + radius * math.sin(i * angle_step)
        positions[node] = {"x": x, "y": y}

    return positions

def calculate_grid_positions(graph_dict, G = None):
    """Dynamically spaces out nodes in a grid layout."""
    num_nodes = len(graph_dict)
    if num_nodes == 0:
        return {}

    grid_size = math.ceil(math.sqrt(num_nodes))  # Define grid dimensions
    spacing_x, spacing_y = 300, 300  # Adjust for better spacing
    start_x, start_y = 100, 100  # Start position

    positions = {}
    index = 0
    for row in range(grid_size):
        for col in range(grid_size):
            if index >= num_nodes:
                break  # Stop when all nodes are placed
            node = list(graph_dict.keys())[index]
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            positions[node] = {"x": x, "y": y}
            index += 1

    return positions
# Convert to Dash Cytoscape format

def calculate_circular_positions(graph_dict, G):
    """Dynamically spaces out nodes in a circular layout based on centrality."""
    centrality_dict, bc, cc = node_calculation(G)
    num_nodes = len(graph_dict)
    if num_nodes == 0:
        return {}

    # Sort nodes by their centrality (highest centrality nodes closer to the center)
    sorted_nodes = sorted(centrality_dict.items(), key=lambda x: x[1], reverse=True)
    
    # Map centralities to radial distance: higher centrality -> smaller radius (closer to center)
    max_centrality = max(centrality_dict.values())
    min_centrality = min(centrality_dict.values())
    centrality_range = max_centrality - min_centrality if max_centrality != min_centrality else 1  # Avoid division by zero
    
    radius_dict = {}
    for node, centrality in sorted_nodes:
        # Normalize the centrality to a radial distance (lower centrality gets larger radius)
        radial_distance = (centrality - min_centrality) / centrality_range * 5000 + 100  # Adjust the range of distances
        radius_dict[node] = radial_distance

    # Calculate positions based on circular layout with adjusted radii
    positions = {}
    angle_step = 2 * math.pi / num_nodes  # Evenly space nodes around the circle
    for i, (node, centrality) in enumerate(sorted_nodes):
        angle = i * angle_step
        radius = radius_dict[node]
        x = 500 + radius * math.cos(angle)  # Centering the graph on x = 500, y = 500
        y = 500 + radius * math.sin(angle)  # Same for y

        positions[node] = {"x": x, "y": y}

    return positions

def make_dash(g_dict):
    """Makes dash visualization! Takes in dict from input reader and calls other functions in this script. Will output application"""

    G = make_x_graph(g_dict)
    cytoscape_elements = format_for_dash_cytoscape(g_dict, G)

    # Dash App
    app = dash.Dash(__name__)

    app.layout = html.Div([
        cyto.Cytoscape(
            id='cytoscape-graph',
            elements=cytoscape_elements,
            layout={'name': 'preset'},  # 'preset' uses manually set positions
            style={'width': '100%', 'height': '500px'},
            stylesheet=[
                {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': 'data(color)'}},
                {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
            ]
        )
    ])

    app.run_server(debug=True)

if __name__ == '__main__':
    # Example usage
    g_dict = read_input("example_book1.csv", "attributes.csv")
    G = make_x_graph(g_dict)
    print(json.dumps(g_dict, indent=4))
    make_dash(g_dict)
    
