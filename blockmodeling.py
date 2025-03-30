#Processes required for blockmodeling, positional analysis, and structural equivalence
import networkx as nx
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import os

# Similarity measures for matrices

def pearson_correlation(matrix):
    """
    Computes the Pearson correlation coefficient for a row to its corresponding column.
    Pearson correlation is better equipped for valued data
    """
    n = matrix.shape[0]
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            result[i, j] = np.corrcoef(matrix[i, :], matrix[j, :])[0, 1]
    return result

def matches(matrix):
    """
    Computes the matches similarities for each cell by its row and column vectors
    Matches check for the number of times the row vector values matches with the column vector values as a percentage
    Matches are better equipped for binary data
    """
    n = matrix.shape[0]
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            matches = np.sum(matrix[i, :] == matrix[j, :])
            result[i, j] = matches / matrix.shape[1]
    return result

def agglomerative_clustering(similarity_matrix, num_blocks=2):
    """
    Runs a hierarchical agglomerative clustering algorithm on the similarity matrix
    """

    # Convert the similarity matrix to a distance matrix
    distance_matrix = 1 - similarity_matrix

    clusters = AgglomerativeClustering(affinity="precomputed", n_clusters=num_blocks, linkage="complete").fit(distance_matrix)

    print(clusters.labels_)

    labels = clusters.labels_.tolist()

    return labels

def binary_hierarchical_clustering(matrix, num_blocks=2):
    """
    Performs hierarchical clustering on a binary matrix using the matches similarity measure.
    """
    # Compute the similarity matrix using matches
    similarity_matrix = matches(matrix)

    # Perform agglomerative clustering
    labels = agglomerative_clustering(similarity_matrix, num_blocks)

    return labels

def valued_hierarchical_clustering(matrix, num_blocks=2):
    """
    Performs hierarchical clustering on a valued matrix using the Pearson correlation similarity measure.
    """
    # Compute the similarity matrix using Pearson correlation
    similarity_matrix = pearson_correlation(matrix)

    # Perform agglomerative clustering
    labels = agglomerative_clustering(similarity_matrix, num_blocks)

    return labels

def label_blocks(attribute_matrix, labels):
    """
    Adds a column to the attribute matrix indicating the block each node belongs to.
    """
    attribute_matrix['Block'] = labels
    
    return attribute_matrix

def organize_label(labels):
    """
    Returns sorted list of labels
    """

    return sorted(labels)

def organize_blocks(matrix, attribute_matrix):
    """
    Organize the rows in matrix by the block value in the attribute matrix
    """
    # Sort the attribute matrix by 'Block' and then by the first column alphabetically
    sorted_attributes = attribute_matrix.sort_values(by=['Block', attribute_matrix.columns[0]])

    # Reorder the rows in the matrix based on the sorted attribute matrix
    sorted_matrix = matrix[sorted_attributes.index, :]

    return sorted_matrix

def reduced_block_matrix(matrix):
    """
    Returns a reduced block matrix, a matrix with individual blocks as rows and columns with the values representing their densities
    """
    # Get the unique blocks
    unique_blocks = np.unique(matrix[:, -1])

    # Initialize the reduced block matrix
    reduced_matrix = np.zeros((len(unique_blocks), len(unique_blocks)))

    # Calculate the density for each block pair
    for i, block_i in enumerate(unique_blocks):
        for j, block_j in enumerate(unique_blocks):
            # Get the indices of the nodes in each block
            indices_i = np.where(matrix[:, -1] == block_i)[0]
            indices_j = np.where(matrix[:, -1] == block_j)[0]

            # Calculate the density between the two blocks
            density = np.sum(matrix[indices_i][:, indices_j]) / (len(indices_i) * len(indices_j))
            reduced_matrix[i, j] = density

    return reduced_matrix

def image_matrix(reduced_matrix, alpha=0.5):
    """
    Returns an image matrix, a matrix with the values representing their densities
    """
    # Set values to 1 if greater than alpha, otherwise 0
    image_matrix = (reduced_matrix > alpha).astype(int)

    return image_matrix