#Data transformation functions for already existing network data

import os
import pandas as pd

def read_matrix(file_path, file_name, sep='\t'):

    """
    Reads a matrix from a given CSV file and file path
    """

    # Ensure the "Network Data" directory exists
    output_dir = os.path.join(os.path.dirname(file_path), "Network Data")
    os.makedirs(output_dir, exist_ok=True)

    # Read the matrix from the CSV file into a Pandas DataFrame
    matrix = pd.read_csv(os.path.join(file_path, file_name), sep=sep)

    return matrix

def write_matrix(matrix, file_path, file_name, sep='\t'):
    # Ensure the file_path exists
    output_dir = os.path.join(os.path.dirname(file_path))
    os.makedirs(output_dir, exist_ok=True)

    # Save the matrix to the chosen filepath with the same file name
    output_path = os.path.join(output_dir, file_name)
    matrix.to_csv(output_path, sep=sep, index=False)

    return "Symmetrized matrix saved to " + output_path

def symmetrize_minimum(matrix):
    """
    Given a square matrix in the form of a Pandas DataFrame, the function:
    Symmetrizes the matrix by taking the minimum value between each pair of elements.
    """

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j:
                matrix.iloc[i, j] = matrix.iloc[j, i] = min(matrix.iloc[i, j], matrix.iloc[j, i])

    return matrix

def symmetrize_maximum(matrix):
    """
    Given a square matrix in the form of a NumPy array, the function:
    Symmetrizes the matrix by taking the maximum value between each pair of elements.
    """
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j:
                matrix.iloc[i, j] = matrix.iloc[j, i] = max(matrix.iloc[i, j], matrix.iloc[j, i])

    return matrix

def symmetrize_average(matrix):
    """
    Given a square matrix in the form of a Pandas DataFrame, the function:
    Symmetrizes the matrix by taking the average value between each pair of elements.
    """

    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j:
                matrix.iloc[i, j] = matrix.iloc[j, i] = (matrix.iloc[i, j] + matrix.iloc[j, i]) / 2
    
    return matrix

def symmetrize(file_path, file_name, method='minimum', sep='\t'):
    """
    Given a square matrix in the form of a Pandas DataFrame, the function:
    Symmetrizes the matrix using the specified method.
    """

    matrix = read_matrix(file_path, file_name, sep)

    # Convert the matrix to a NumPy array for processing
    matrix = matrix.to_numpy()

    if method == 'minimum':
        matrix = symmetrize_minimum(matrix)
    elif method == 'maximum':
        matrix =  symmetrize_maximum(matrix)
    elif method == 'average':
        matrix =  symmetrize_average(matrix)
    else:
        raise ValueError("Invalid method. Choose 'minimum', 'maximum', or 'average'.")
    
    write_matrix(matrix, file_path, file_name, sep)
    
    return "Symmetrization complete. Matrix saved to " + os.path.join(file_path, file_name)

def make_binary(matrix):
    """
    Converts a matrix to binary format.
    """
    matrix[matrix > 0] = 1
    return matrix

def produce_binary(file_path, file_name, sep='\t'):
    """
    Given a square matrix in the form of a Pandas DataFrame, the function:
    Converts the matrix to binary format.
    """
    matrix = read_matrix(file_path, file_name, sep)
    matrix = make_binary(matrix)
    write_matrix(matrix, file_path, file_name, sep)

    return "Binary matrix saved to " + os.path.join(file_path, file_name)