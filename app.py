from flask import Flask, flash, request, redirect, url_for, render_template, session, jsonify
from werkzeug.utils import secure_filename
from reading_data import read_attribute_file, read_matrix
from calc_render import read_input, make_x_graph, node_calculation, network_calculations, make_dash
from dash.dependencies import Input, Output, State
import dash
import os
import json

app = Flask(__name__)
dash_app = dash.Dash(__name__, server=app, url_base_pathname="/dash/")

app.secret_key = 'PLEASE_SAVE_THIS_SOMEWHERE_ELSE'

app.config["UPLOAD_FOLDER"] = "Uploads/"

ALLOWED_EXTENSIONS = {'csv'}

degree_centrality, betweenness_centrality, closeness_centrality = {}, {}, {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        relational_file = request.files.get('relational')
        attribute_file = request.files.get('attribute')
        
        if not relational_file and not attribute_file:
            error = "No file selected. Please upload a .csv file"
            return render_template('index.html', error = error)

        filenames = {'relational_file': None, 'attribute_file': None}

        for file in [relational_file, attribute_file]:
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

                if file == relational_file:
                    filenames["relational"] = file.filename
                else:
                    filenames["attribute"] = file.filename
            elif file:
                error = "Invalid file format! Please upload a .csv file"
                return render_template('index.html', error = error)

        session["filenames"] = filenames # Storing uploaded files in session to be read & processed later
        return redirect(url_for('visualize'))
    return render_template('index.html')

def create_network_graph(filenames):
    global degree_centrality, betweenness_centrality, closeness_centrality
    relational_filename = filenames.get("relational")
    attribute_filename = filenames.get("attribute")

    if not relational_filename and not attribute_filename:
        return # Figure out error handling

    if relational_filename:
        read_matrix('Uploads', relational_filename)
    if attribute_filename:
        read_attribute_file('Uploads', attribute_filename)

    relational_file = os.path.join(app.config['UPLOAD_FOLDER'], relational_filename)
    attribute_file = os.path.join(app.config['UPLOAD_FOLDER'], attribute_filename)
    
    g_dict, df2, adj_matrix_df = read_input(relational_file, attribute_file) # Produces dictionary to create graph
    G = make_x_graph(g_dict) # Creates network graph

    degree_centrality, betweenness_centrality, closeness_centrality = node_calculation(G)
    

    dash_app.layout = make_dash(g_dict)
    @dash_app.callback(
        Output('node-attributes', 'children'),
        Input('cytoscape-graph', 'selectedNodeData')  # Listens for node clicks
    )
    def display_node_attributes(selectedNodeData):
        """Displays attributes of the clicked node."""
        if selectedNodeData and len(selectedNodeData) > 0:
            node_id = selectedNodeData[0]['id']  # Get the node's ID
            node_data = g_dict.get(node_id, {})
            attributes = node_data.get('attributes', {})
            centrality_values = (degree_centrality.get(node_id, 0), betweenness_centrality.get(node_id, 0), closeness_centrality.get(node_id, 0))
            centrality_measures = ['Degree Centrality', 'Betweenness Centrality', 'Closeness Centrality']
            # Generate attribute text
            attributes_text = [
                dash.html.H4(f"Attributes of node {node_id}:")
            ]
            for key, value in attributes.items():
                attributes_text.append(dash.html.P(f"{key}: {value}"))

            attributes_text.append(dash.html.H4(f"Centrality Measures"))
            for centrality_measure, value in zip(centrality_measures, centrality_values):
                attributes_text.append(dash.html.P(f"{centrality_measure}: {value}"))

            return attributes_text
        
        return dash.html.P("Click on a node to see its attributes.")
    # @dash_app.callback(
    #     Output('selected-node', 'data'),
    #     Input('cytoscape-graph', 'tapNodeData')
    # )
    # def update_centrality(clicked_node):
    #     if not clicked_node:
    #         return {}

    #     node_id = clicked_node['id']
    #     print(f"Node clicked: {node_id}", flush=True)

    #     # data = {
    #     #     "degree": degree_centrality.get(node_id, 0),
    #     #     "closeness": closeness_centrality.get(node_id, 0),
    #     #     "betweenness": betweenness_centrality.get(node_id, 0)
    #     # }

    #     # print(f"Sending data to JavaScript: {data}", flush=True)

    #     # return data
    #     # return dash.dcc.Location(href=f"/visualize/{node_id}", id="redirect-location")
    #     return redirect(url_for(f'visualize/{node_id}'))
    
    return G

@app.route('/visualize', methods = ['GET', 'POST'])
# @app.route('/visualize/<node_id>', methods=['GET', 'POST']) 
def visualize(node_id = None):
    filenames = session.get("filenames", {})  # Retrieve filenames from session
    
    G = create_network_graph(filenames)

    density = network_calculations(G) 

    network_density = density

    # Dummy values for now
    attributes = ['a', 'b', 'c']
    ei_indices = [0.2, 0.3, 0.7]

    degree_centrality, closeness_centrality, betweenness_centrality = 0, 0, 0
    if node_id:
        degree_centrality = degree_centrality.get(node_id, 0)
        closeness_centrality = closeness_centrality.get(node_id, 0)
        betweenness_centrality = betweenness_centrality.get(node_id, 0)

    return render_template('visuals.html', network_density=network_density, 
                           ei_indices=zip(attributes, ei_indices),
                           degree_centrality=degree_centrality, 
                           closeness_centrality=closeness_centrality,
                           betweenness_centrality=betweenness_centrality) 

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
