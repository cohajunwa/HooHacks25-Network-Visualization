#Code for reading in network data and modifying network data

import pandas as pd
import os

def read_matrix(file_path, file_name, sep=','):
    # Ensure the "Network Data" directory exists
    output_dir = os.path.join(os.path.dirname(file_path), "Network Data")
    os.makedirs(output_dir, exist_ok=True)

    # Read the matrix from the CSV file
    matrix = pd.read_csv(os.path.join(file_path, file_name), sep=sep)

    # Save the matrix to the "Network Data" directory with the same file name
    output_path = os.path.join(output_dir, file_name)
    matrix.to_csv(output_path, sep=sep, index=False)

    return matrix

def read_binary_edgelist_undirected(filepath, file_name, sep=','):
    # Ensure the "Network Data" directory exists
    output_dir = os.path.join(os.path.dirname(filepath), "Network Data")
    os.makedirs(output_dir, exist_ok=True)

    # Read the binary edgelist from the CSV file
    edgelist = pd.read_csv(os.path.join(filepath, file_name), sep=sep)

    # Label the columns of the edgelist
    edgelist.columns = ['sender', 'receiver']

    # Get unique nodes from the edgelist
    unique_nodes = sorted(set(edgelist.iloc[0]).union(set(edgelist.iloc[1])))

    # Create an empty adjacency matrix
    matrix = pd.DataFrame(0, index=unique_nodes, columns=unique_nodes)
    # Fill every cell in the matrix with 0
    matrix[:] = 0

    # Populate the adjacency matrix
    for _, row in edgelist.iterrows():
        matrix.at[row.iloc[0], row.iloc[1]] = 1
        matrix.at[row.iloc[1], row.iloc[0]] = 1  # Assuming the graph is undirected

    # Save the matrix to the "Network Data" directory with the same file name
    output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_matrix.csv")
    matrix.to_csv(output_path, sep=sep)

    return matrix

def read_binary_edgelist_directed(filepath, file_name, sep=','):
    # Ensure the "Network Data" directory exists
    output_dir = os.path.join(os.path.dirname(filepath), "Network Data")
    os.makedirs(output_dir, exist_ok=True)

    # Read the binary edgelist from the CSV file
    edgelist = pd.read_csv(os.path.join(filepath, file_name), sep=sep)

    # Label the columns of the edgelist
    edgelist.columns = ['sender', 'receiver']

    # Get unique nodes from the edgelist
    unique_nodes = sorted(set(edgelist.iloc[0]).union(set(edgelist.iloc[1])))

    # Create an empty adjacency matrix
    matrix = pd.DataFrame(0, index=unique_nodes, columns=unique_nodes)
    # Fill every cell in the matrix with 0
    matrix[:] = 0

    # Populate the adjacency matrix
    for _, row in edgelist.iterrows():
        matrix.at[row.iloc[0], row.iloc[1]] = 1

    # Save the matrix to the "Network Data" directory with the same file name
    output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_directed_matrix.csv")
    matrix.to_csv(output_path, sep=sep)

    return matrix


def read_valued_edgelist(filepath, file_name, sep=','):
    # Ensure the "Network Data" directory exists
    output_dir = os.path.join(os.path.dirname(filepath), "Network Data")
    os.makedirs(output_dir, exist_ok=True)

    # Read the valued edgelist from the CSV file
    edgelist = pd.read_csv(os.path.join(filepath, file_name), sep=sep)

    # Label the columns of the edgelist
    edgelist.columns = ['sender', 'receiver', 'value']

    # Get unique nodes from the edgelist
    unique_nodes = sorted(set(edgelist.iloc[:, 0]).union(set(edgelist.iloc[:, 1])))

    # Create an empty adjacency matrix
    matrix = pd.DataFrame(0, index=unique_nodes, columns=unique_nodes)
    # Fill every cell in the matrix with 0
    matrix[:] = 0

    # Populate the adjacency matrix with weights
    for _, row in edgelist.iterrows():
        matrix.at[row.iloc[0], row.iloc[1]] = row.iloc[2]

    # Save the matrix to the "Network Data" directory with the same file name
    output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_valued_matrix.csv")
    matrix.to_csv(output_path, sep=sep)

    return matrix

def read_attribute_file(filepath, file_name, sep=","):
    # Ensure the "Network Data" directory exists
    output_dir = os.path.join(os.path.dirname(filepath), "Network Data")
    os.makedirs(output_dir, exist_ok=True)

    # Read the attribute file from the CSV file
    attributes = pd.read_csv(os.path.join(filepath, file_name), sep=sep)

    # Sort the attribute file by the first column in alphabetical and numerical order
    attributes = attributes.sort_values(by=attributes.columns[0], key=lambda col: col.astype(str))

    #Save the attribute file to the "Network Data" directory with the same file name
    output_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}_attributes.csv")
    attributes.to_csv(output_path, sep=sep, index=False)

    return attributes

#tests
#read_matrix("", "StateMigration2023.csv")
#read_binary_edgelist_undirected("", "MadreSana_wave1.csv")
#read_valued_edgelist("", "MadreSana_wave1.csv")
#read_binary_edgelist_directed("", "MadreSana_wave1.csv")