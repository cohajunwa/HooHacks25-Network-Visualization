## Inspiration
Social Network Analysis (SNA) is a relatively new field of research, combining mathematical techniques in graph theory and linear algebra to sociometry, a mapping of individuals' or actors' relationships towards one another. Tools for SNA are limited, with python having numerous libraries capable of network analysis but not accounting for relational data in combination with attributes; R consists of an _sna_ package but produces static visualizations that cannot be modified.

## What it does
The **Network Visualization Tool** is a user-friendly web application that reads in csv files of network data and corresponding attribute data and generates an informative and interactive visualization of the network. 
The interface allows you to click and move the nodes around. Clicking a node can also give you individual information of its attributes, without having to swap between two spreadsheets! This action will also update the information panel next to the visualization providing information of the node's individual centrality measures.
Next to the visualization there are also measures that apply to the entire network (such as density) displayed for your convenience. A notable SNA specific measure is the E-I Index, an indicator of heterogeneity and homogeneity in the network - scroll down to the **SNA Measures** section in our project's README for a more detailed explanation - applied to different attributes from the data.
For large network with lots of nodes, it can be difficult for you to try to understand let alone interpret a complete network visualization. To remedy this without running multiple successive calculations, the information panel has the option to open a consolidated graph. This consolidated graph collapses similar actors into a set number of roles, and maps the relationships amongst the identified roles accordingly. 

## How we built it
The back-end of this project was created using Python, with simple measures that existed in preexisting Python library _NetworkX_ being implemented again. For data management and calculations we made use of Python libraries _pandas_, _numpy_, _scipy_.
_explain the portions here guys!_

## Challenges we ran into
Learning how to use flash and integrating flash with dash. We also spent a lot of time figuring out the theory and calculations for our project, including agglomerative clustering within our backend. We had trouble deploying our website online due to some time constraints and limited space available on Python Anywhere (our project was too large for its free application).

## Accomplishments that we're proud of
We have a lot of great statistics on our website, including a comprehensive e-i index calculation with confidence levels and calculations to support graph simplification using structural equivalence to cluster nodes together and help the user better understand their data. These features are not very accessible to those not versed in data science in other applications (the whole inspiration for this project). Students taking Public policy classes (at W&M, one of our teammates are) for example use similar software but need to manually create the blocks for this simplification. Our software does this automatically and makes this project aid in accessibility for social network analysis and also an education resource for those still learning.

## What we learned
Other team members learned a lot about this type of social network analysis and some graph theory! We learned alot about Flash and frontend development during this project. Most importantly though, we learned how to communicate about our code that we were committing and write insightful comments. These are the foundations of good coding practices :) We also loved this project and had the best weekend!

## What's next for Network Visualization Tool
We will be pitching this project to the W&M public policy faculty to implement in our software in their classes about social networks (mainly between different states and countries in this application). We will also be presenting this to the data science faculty as well for use in certain courses. This project can be expanded upon in a couple ways also that we are going to be collaborating on after the hackathon. These ways include 1) Deploying it on the web 2) Better user interface and instruction/accommodation for file upload 3) Adding AI to the software to summarize the data that the user has uploaded (not analyze it)

## SNA measures
### Centrality Measures
Centrality measures are used to identify the most important nodes in a network. There are several different types of centrality measures, including degree centrality, closeness centrality, and betweenness centrality. Each of these measures provides a different perspective on the importance of a node in the network. For example, degree centrality measures the number of connections a node has, while betweenness centrality measures how often a node lies on the shortest path between two other nodes. The Network Visualization Tool calculates these measures for each node in the network and displays them in the information panel when a node is clicked.
### E-I Index
The E-I Index is a measure of the degree to which a network is heterogeneous or homogeneous. It is calculated by taking the number of edges that connect nodes within the same group (intra-group) and subtracting the number of edges that connect nodes in different groups (inter-group). The E-I Index can take on values between -1 and 1, with -1 indicating a completely homogeneous network and 1 indicating a completely heterogeneous network. A value of 0 indicates that the network is equally heterogeneous and homogeneous. This is key to quantifying the social phenomen of cohesion - better known as birds of a feather flock together.
### Simplified Graph based on Structural Equivalence and Role Assignment
The simplified graph is a representation of the network that groups nodes into roles based on their structural equivalence. The nodes in one block occupy a similar role in the network. This calculation is completed through agglomerative clustering.