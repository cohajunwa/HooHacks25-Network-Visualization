import pandas as pd
import networkx as nx
import scipy
import numpy as np
import os
import json

def read_input(edges, attributes):
    """Takes in two csv files. The directionality of the edge will be FROM rows TO columns"""
    # TODO add like an error handling for incompatiable files
    
    df1 = pd.read_csv(edges,  index_col=0)
    df2 = pd.read_csv(attributes,  index_col=0)
    graph_dict = {}
    seen_edges = set()

    for row in df1.index:
        for col in df1.columns:
            value = df1.at[row, col]
            edge = tuple(sorted((row, col)))  # (A, B) and (B, A) are the same
            
            # Stopping double counting and self loops and adds to dict
            if edge not in seen_edges and value != 0 and row != col:  # only counting unseen non-zero edges
                # Add to targets dict
                graph_dict.setdefault(row, {"targets": {}})
                graph_dict.setdefault(col, {"targets": {}})
                graph_dict[row]["targets"][col] = value  
                #graph_dict[col]["targets"][row] = value  # (undirected) ?
                seen_edges.add(edge)

            attribute_names = df2.columns[1:] 
            for col2 in df2.columns:
                graph_dict[row][col2] = value 

    print(json.dumps(graph_dict, indent=4))
    return graph_dict

read_input("example_book.csv")

if __name__ == "__main__":
    read_input("example_book.cvs")