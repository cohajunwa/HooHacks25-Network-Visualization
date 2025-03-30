#Temporary file for testing cohesion and homophily of network data
import pandas as pd
import numpy as np
import transforming_data as transform
from scipy.stats import norm

def clean_matrix(matrix):
    """
    Symmetrizes the matrix by maximum to ignore tie direction
    Makes the matrix binary to ignore tie weight
    """

    # Symmetrize the matrix
    matrix = transform.symmetrize_maximum(matrix)

    # Convert the matrix to binary
    matrix = transform.make_binary(matrix)

    return matrix

def calc_ei(matrix, attribute_column):
    """
    Calculates the E-I index for a given matrix.
    The E-I index is a measure of the cohesion of a network.
    It is calculated as the difference between the number of edges within blocks and the number of edges between blocks.
    """

    # Get the number of nodes in the matrix
    n = matrix.shape[0]

    # Initialize variables to count edges within and between blocks
    I = 0
    E = 0

    # Iterate through the upper triangle of the matrix to count edges
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] == 1 and attribute_column[i] == attribute_column[j]:
                I += 1
            elif matrix[i, j] == 1 and attribute_column[i] != attribute_column[j]:
                E += 1

    # Calculate the E-I index
    ei_index = (E - I) / (E + I)

    return ei_index

def generate_ei_permutation(matrix, num_ties):
    """
    Randomly fill in the matrix with num_ties number of cells with value 1
    """

    # Get the number of nodes in the matrix
    n = matrix.shape[0]

    # Create a copy of the matrix to fill in

    # Randomly select num_ties number of cells to fill in with 1
    for _ in range(num_ties):
        i = np.random.randint(0, n)
        j = np.random.randint(0, n)
        while matrix[i, j] == 1 or i == j:
            i = np.random.randint(0, n)
            j = np.random.randint(0, n)
        matrix[i, j] = 1
        matrix[j, i] = 1

    return matrix

def ei_test(matrix, attribute_column, num_permutations=50):
    """
    Performs a permutation test for the E-I index.
    The test is performed by randomly permuting the edges in the matrix and calculating the E-I index for each permutation.
    The p-value is calculated as the proportion of permutations that have an E-I index greater than or equal to the observed E-I index.
    """

    # Clean the matrix
    matrix = clean_matrix(matrix)

    # Calculate the observed E-I index
    observed_ei = calc_ei(matrix, attribute_column)

    # Initialize a lit to to store E-I permutation scores
    ei_indices = []

    # Perform the permutations
    while len(ei_indices) < num_permutations:
        permuted_matrix = generate_ei_permutation(np.zeros_like(matrix), np.sum(matrix) // 2)
        ei_indices.append(calc_ei(permuted_matrix, attribute_column))

    # Calculate the standard deviation of E-I indices
    ei_std_dev = np.std(ei_indices)

    if ei_std_dev == 0:
        ei_std_dev = 1e-10

    # Calculate the mean of E-I indices
    ei_mean = np.sum(ei_indices) / num_permutations

    # Calculate how many standard deviations the observed E-I index is away from the mean
    ei_z_score = (observed_ei - ei_mean) / ei_std_dev
    
    # Calculate the p-value for a two-tailed test
    p_value = 2 * (1 - norm.cdf(abs(ei_z_score)))

    # Calculate the confidence interval for the E-I mean
    confidence_interval = [ei_mean - 1.96 * ei_std_dev, ei_mean + 1.96 * ei_std_dev]

    return observed_ei, p_value, confidence_interval

def max_ei(matrix, num_ties, attribute_column):
    """
    Creates a permutation that maximizes the number of external ties
    Returns the E-I index of permutation that maximizes heterogeneity
    """

    maximum_matrix = np.zeros_like(matrix)
    n = matrix.shape[0]

    while num_ties > 0:
        # iterate through the upper triangle of the matrix
        for i in range(n):
            for j in range(i + 1, n):
                if num_ties > 0 and attribute_column[i] != attribute_column[j]:
                    maximum_matrix[i, j] = 1
                    maximum_matrix[j, i] = 1
                    num_ties -= 1
        
        # if all hetergeneous ties are filled, iterate through the upper triangle again and fill in 0s with 1s
        for i in range(n):
            for j in range(i + 1, n):
                if num_ties > 0 and maximum_matrix[i, j] == 0:
                    maximum_matrix[i, j] = 1
                    maximum_matrix[j, i] = 1
                    num_ties -= 1
    
    return calc_ei(maximum_matrix, attribute_column)

def min_ei(matrix, num_ties, attribute_column):
    """
    Creates a permutation that minimizes the number of external ties
    Returns the E-I index of permutation that maximizes homogeneity
    """

    minimum_matrix = np.zeros_like(matrix)
    n = matrix.shape[0]

    while num_ties > 0:
        # iterate through the upper triangle of the matrix
        for i in range(n):
            for j in range(i + 1, n):
                if num_ties > 0 and attribute_column[i] == attribute_column[j]:
                    minimum_matrix[i, j] = 1
                    minimum_matrix[j, i] = 1
                    num_ties -= 1
        
        # if all homgeneous ties are filled, iterate through the upper triangle again and fill in 0s with 1s
        for i in range(n):
            for j in range(i + 1, n):
                if num_ties > 0 and minimum_matrix[i, j] == 0:
                    minimum_matrix[i, j] = 1
                    minimum_matrix[j, i] = 1
                    num_ties -= 1
    
    return calc_ei(minimum_matrix, attribute_column)

def rescaled_ei(matrix, attribute_column):
    """
    Calculates the rescaled E-I index for a given matrix.
    The rescaled E-I index is calculated as the difference between the number of edges within blocks and the number of edges between blocks,
    divided by the maximum number of external ties possible.
    """

    # Get the number of nodes in the matrix
    n = matrix.shape[0]

    # Clean the matrix
    matrix = clean_matrix(matrix)

    # Initialize the observed E-I index and the number of unique ties
    observed_ei = calc_ei(matrix, attribute_column)
    num_ties = np.sum(matrix) // 2

    # Calculate the minimum and maximum E-I indices
    min_ei_index = min_ei(matrix, num_ties, attribute_column)
    max_ei_index = max_ei(matrix, num_ties, attribute_column)

    # Rescale the observed E-I index
    rescaled_ei_index = (max_ei_index - min_ei_index) * (observed_ei - min_ei_index) / (max_ei_index - min_ei_index) + min_ei_index

    return rescaled_ei_index