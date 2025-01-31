"""

Solve Activity 1 from Week 3 in the AIML module. The Task requires to find a path from A to H in
the graph:
        A(5) --------3-------- C(8)
       /                       |
      3                        |
     /                         |
    B(6)                       3
    |                          |
    2                          |
    |                          |
    D(4)-------4--------E(4)-1-F(5)
                        |     /
                        2   3
                        | /
                 H(0)-2-G(2)
Each Character represents a node in the graph with it's respective heuristic
cost in (). The actual costs fot he path is indicated by the integer on the edges.
There are three required algorithms: A* and Greedy Best First search implemented as
graph search and third, A* as Tree search.

This script provides users with the option to excecute each search and visualises the
search process and result. Classes are stored in the classes directory.
"""

from classes.GBFS import GBFS
from classes.Astar_tree import AStarTree
from classes.Astar import AStar

if __name__=="__main__":
    # define start and end
    start_node = "a"
    goal_node = "h"
    ## define nodes with their heuristic
    nodes = {
        "a": 5, "b": 6, "c": 8, "d": 4,
        "e": 4, "f": 5, "g": 2, "h": 0
    }
    ## define edges and stepcost
    edges = (
        ("a", "b", 3), ("a", "c", 3), ("b", "d", 2),
        ("d", "e", 4), ("c", "f", 3), ("e", "f", 1),
        ("e", "g", 2), ("f", "g", 3), ("g", "h", 2)
    )

    ##Starting with Greedy Best First Search
    print("-"*10 + "Greedy Best First Search" + "-"*10)
    GBFS(nodes, edges, start_node, goal_node)
    print("-" * 10 + "A* Graph" + "-" * 10)
    AStar(nodes, edges, start_node, goal_node)
    print("-" * 10 + "A* Tree" + "-" * 10)
    AStarTree(nodes, edges, start_node, goal_node)
