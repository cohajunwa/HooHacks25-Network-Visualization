import pandas as pd
import networkx as nx
import scipy
import numpy as np
import os
import json
import dash
import dash_cytoscape as cyto
from dash import html, dcc
import math
from temp_ei import*
from dash.dependencies import Input, Output
from dash import dcc, html, Input, Output, State

import transforming_data as transform
from scipy.stats import norm

def read_input(edges, attributes = 0):
    """Takes in two csv files. The directionality of the edge will be FROM rows TO columns"""
    
    df1 = pd.read_csv(edges, index_col=0)
    block_display = 0
    if attributes == 0:
        block_display = 1
        block_names = [f"block{i+1}" for i in range(df1.shape[0])]
        rel_dict = {
        block_names[i]: {"targets": {block_names[j]: df1.iloc[i, j] for j in range(df1.shape[1])}} for i in range(df1.shape[0])
        }
    
        return rel_dict
    else:
        df2 = pd.read_csv(attributes, index_col=0)

    graph_dict = {}
    seen_edges = set()
    # Initialize attribute dictionary
    attribute_dict = {}

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
        if block_display == 0 and row in df2.index:
            attribute_dict[row] = df2.loc[row].to_dict()  # Convert row to dictionary
            graph_dict.setdefault(row, {}).setdefault("attributes", {})
            for attr_name in df2.columns:  # Use the correct column names from df2
                graph_dict[row]["attributes"][attr_name] = int(df2.at[row, attr_name])

    # Create adjacency matrix
    nodes = list(graph_dict.keys())  # Extract all nodes
    node_indices = {node: i for i, node in enumerate(nodes)}  # Map nodes to indices
    adj_matrix = np.zeros((len(nodes), len(nodes)))  # Initialize with zeros

    for node, data in graph_dict.items():
        for target, weight in data.get("targets", {}).items():
            adj_matrix[node_indices[node], node_indices[target]] = weight

    # Convert adjacency matrix to DataFrame for better readability
    adj_matrix_df = pd.DataFrame(adj_matrix, index=nodes, columns=nodes)

    if block_display == 0:
        return graph_dict, df2, adj_matrix_df
    else: 
        return graph_dict, adj_matrix_df



def make_x_graph(graph_dict, directed=False):
    """makes dict from input reader function above and makes it an object in networkx. This
    is the 2nd function and is needed for calculations. You do not have to call this function!"""
    
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

def node_calculation(G):
    dc = nx.degree_centrality(G)
    bc = nx.betweenness_centrality(G)
    cc = nx.closeness_centrality(G)
    return dc,bc,cc

def network_calculations(G):
    m = len(G.edges)
    n = len(G.nodes)
    d = m/(n*(n-1))

    #node_groups = {"A": "Group1", "B": "Group1", "C": "Group2", "D": "Group2"}
    #E = sum(1 for u, v in G.edges if node_groups[u] != node_groups[v])
    #I = sum(1 for u, v in G.edges if node_groups[u] == node_groups[v])
    #ei_index = (E - I) / (E + I) if (E + I) != 0 else 0    
    return d
 
def format_for_dash_cytoscape(graph_dict, G):
    """Converts the graph dictionary into a format suitable for Dash Cytoscape (directed edges)."""
    
    elements = []
    node_positions = calculate_positions(graph_dict, G)  # Get node positions dynamically

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

def calculate_positions(graph_dict, G):
    """Dynamically spaces out nodes in a circular layout."""
    dc, bc, cc = node_calculation(G)
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
        radial_distance = (centrality - min_centrality) / centrality_range * 1000 + 100  # Adjust the range of distances
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
    """Creates a Dash visualization. Displays attributes of a node when clicked."""
    
    # Create Cytoscape elements
    G = make_x_graph(g_dict)
    cytoscape_elements = format_for_dash_cytoscape(g_dict, G)

    # dash_app = dash.Dash(__name__, server = app, url_base_pathname="/dash/")
    # Dash App
    # app = dash.Dash(__name__)

    return html.Div([
        html.Div([
            cyto.Cytoscape(
            id='cytoscape-graph',
            elements=cytoscape_elements,
            layout={'name': 'preset'},  # 'preset' uses manually set positions
            style={'width': '100%', 'height': '300px'},
            stylesheet=[
                {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': 'data(color)'}},
                {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
            ]
        ),
        ], style={'width': '70%', 'display': 'inline-block'}),

        # Sidebar for node attributes
        html.Div(
            id='node-attributes',
            style={
                'width': '28%', 
                'border': '1px solid black', 
                'padding': '10px', 
                'height': '300px',  
                'overflow': 'auto',  # Enables scrolling if content overflows
                'font-family': 'Arial, sans-serif',
                'border-radius': '10px'
            }
        )
    ],  style={'display': 'flex'})


    # return html.Div([
    #     cyto.Cytoscape(
    #         id='cytoscape-graph',
    #         elements=cytoscape_elements,
    #         layout={'name': 'preset'},  # 'preset' uses manually set positions
    #         style={'width': '100%', 'height': '500px'},
    #         stylesheet=[
    #             {'selector': 'node', 'style': {'label': 'data(label)', 'background-color': 'data(color)'}},
    #             {'selector': 'edge', 'style': {'curve-style': 'bezier', 'target-arrow-shape': 'triangle'}}
    #         ]
    #     ),
    #     # dash.dcc.Store(id = 'selected-node'),

    #     # Textbox to display node attributes
    #     html.Div(
    #         id='node-attributes',
    #         style={'marginTop': '20px', 'border': '1px solid black', 'padding': '10px', 'width': '50%'}
    #     )
    # ])

    # Callback to update textbox with node's attributes
    # @app.callback(
    #     Output('node-attributes', 'children'),
    #     Input('cytoscape-graph', 'selectedNodeData')  # Listens for node clicks
    # )
    # def display_node_attributes(selectedNodeData):
    #     """Displays attributes of the clicked node."""
    #     if selectedNodeData and len(selectedNodeData) > 0:
    #         node_id = selectedNodeData[0]['id']  # Get the node's ID
    #         node_data = g_dict.get(node_id, {})
    #         attributes = node_data.get('attributes', {})
            
    #         # Generate attribute text
    #         attributes_text = [html.H4(f"Attributes of node {node_id}:")]
    #         for key, value in attributes.items():
    #             attributes_text.append(html.P(f"{key}: {value}"))
            
    #         return attributes_text
        
    #     return html.P("Click on a node to see its attributes.")

    # app.run_server(debug=True)

if __name__ == '__main__':
    # Phase 1
    g_dict, df2, matrix = read_input("campnet.csv", "campattr.csv")
    make_dash(g_dict)
    # Rename the first column (since it's unnamed)
    df2.rename(columns={df2.columns[0]: "State"}, inplace=True)
    attributes = df2.to_numpy()
    G = make_x_graph(g_dict)
    dc, bc, cc = node_calculation(G) # Dynamically updated, must search for node ID in dict
    
    d = network_calculations(G) # Static scalar values
    attributes_col = []
    for i in range(len(attributes[0])):
        for row in attributes:
            attributes_col.append(row[i])
        observed_ei, p_value, confidence_interval = ei_test(matrix, attributes_col, num_permutations=50)
        print(observed_ei, p_value, confidence_interval)

    # Phase 2
    g_dict2= read_input("sample_blockmodeling.csv")
    make_dash(g_dict2)
    #d2 = network_calculations(G2) # Static scalar values

    
