"""
Author: Stefan Mörchen
Date: 03.01.2025
Purpose: Solve Activity 1 from Week 3 in AIML - navigate a robot around obstacles
Apply Tree Search for A* Algorithm with Manhattan Distance as heuristic
"""
# import packages
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import copy
from algorithm.utils.TreeNode import TreeNode

class AStarTree:
    """
    A class representing a graph used for heuristic-based pathfinding via search Tree.

    Attributes:
        _graph (nx.Graph): The NetworkX graph representation.
        _end_node (str): The goal node.
        _step (int): A counter to track search steps.
        _frames (list): Stores frames for visualization.
        _frontier (list): The list of nodes to explore.
        _path (list): The solution path.
    """

    def __init__(self, nodes: dict, edges: tuple, start_node: str = "a", end_node: str = "h"):
        """
        Initializes the MyGraph object.

        Args:
            nodes (dict): A dictionary mapping node names to heuristic values.
            edges (tuple): A tuple of edges where each edge is (node1, node2, stepcost).
            start_node (str, optional): The starting node (default: "a").
            end_node (str, optional): The goal node (default: "h").
        """
        self._end_node = end_node
        self._step = 0
        self._graph = nx.Graph()
        self._fill_graph(edges, nodes)
        self._frames = []
        self._frontier = []
        self._path = []
        self._search(start_node, end_node)
        self._get_path_cost()
        self.visualise()

    def _search(self, current_node, goal):
        """
        implements A* search algorithm with a search tree
        Args:
             current_node: determines start of the path
             goal: determines goal state
        """
        ##set initial first node that is explored (start_node)
        current_node = TreeNode(current_node,
                                heuristic=0,
                                neighbors=self._graph.neighbors(current_node)
                                )
        current_node.set_step(self._step) ##set search step
        current_node.toggle_start()
        self._root = current_node ##set root for search tree
        self._frontier.append(current_node) ##expand frontier
        while current_node: ##start search loop
            current_node.toggle_occupied() ##toogle node to occupied
            current_node.set_step(self._step) ##set search step (redundand for start node, but needed earlier)
            self._frames.append(copy.deepcopy(self._root))  ##append snapshot of current search tree for animation
            ## check if reached goal
            if current_node.name == goal:
                self._end_leaf = current_node
                while current_node:##generate solution
                    self._path.append(current_node._id) ##add node to path solution
                    ##find parent of node or None(for the start node)
                    current_node.edge_color = "red" ##set path color for later visualisation
                    current_node = current_node.parent ##switch to next node on path
                self._path = list(reversed(list(self._path))) ##reverse path to have right order
                self._frames.append(self._root) ##append a last snapshot of solved tree
                return None

            ## remove from frontier
            self._frontier.remove(current_node)
            current_node.toggle_occupied() ##to to unoccupied
            current_node.toggle_explored() ##set as explored
            ## expand frontier and save parent for newly added nodes
            for node in current_node._neighbors: ##get neighbors to expand frontier
                    node_data = self._graph.nodes[node] ##get attributes of node (h(x), neighbors)
                    self._frontier.append( ##add node to frontier
                        TreeNode(
                            node,
                            heuristic=node_data["heuristic"], ##h(x) heuristic value of node
                            neighbors=self._graph.neighbors(node), ##neighbors for later expansion of frontier
                            parent=current_node, ##parent, for tree struktur and later path generation
                            path_cost=self._graph.get_edge_data(current_node.name,
                                                                node)["stepcost"], ##cost to get to the node from parent
                        )
                    )
            ## define next node based on heuristic
            current_node = self._find_next()

    def _find_next(self):
        """determiens the node in the frontier with the lowest cumulative heuristic value"""
        self._step += 1 ##increase search step
        if len(self._frontier) == 0:
            return False  ##if there is no solution
        min_ = float("inf") ##variable to determine the cheapest next node
        min_node = None ##next node
        for node in self._frontier: ##go over all nodes in frontier to find the
            ##node with the cheapest cumulative heuristic value from root to self
            ## Difference to GBFS -> find minimal path sum
            ##GBFS would just find the node with cheapest individual heuristic
            if node.sum_heuristic < min_: ##if heuristic value is lower set node as new node
                min_ = node.sum_heuristic
                min_node = node
        return min_node

    def _get_path_cost(self):
        """Generates Dictionary with the heuristic approximiated costs and actual costs and prints it"""
        self._path_cost = {
            "heuristic": self._end_leaf.sum_heuristic,
            "stepcost": self._end_leaf.sum_path_cost
        }
        print("The heuristic cost for the path is: ",
              self._path_cost["heuristic"],
              "\nThe stepcost for the path is: ",
              self._path_cost["stepcost"])

    def _fill_graph(self, edges, nodes):
        """
        Create and fill the Graph Structure for which the solution is searched
        Args:
             edges: determines edges and its costs
             nodes: determines nodes of graph and their attributes
        """
        for node, heuristic in nodes.items():
            ## add each node with its heuristic
            self._graph.add_node(node, heuristic=heuristic,
                                 explored=False, occupied=False)
        for node1, node2, stepcost in edges:
            ## add each edges with its stepcost
            self._graph.add_edge(node1, node2, stepcost=stepcost, color="gray")

    def visualise(self):
        """Vidualise the search process animates a growing search tree to
        let user see how the algorithm traverses the tree in order to find a solution.
        The finished tree shows explored nodes in light green, the goal node in green and
        unexplored nodes in lightblue, the solving path is red. Each node displays
        its cumulative heuristic cost, unique id and search step. Unexplored nodes have no search step.
        Actual pathcosts are displayed at the respective edge."""
        fig, ax = plt.subplots(figsize=(8, 6)) ##initialise the plt objective

        def _plot_frame(frame):
            ax.clear() ##clear tzhe graph for each animation frame

            G = nx.DiGraph() ##initialise graph to be turned into tree
            edge_labels = {} ##edgelabels are generated in the next function

            def add_edges(node):
                """Recursive function to add nodes and edges to the graph."""
                if not node in G.nodes():
                    G.add_node(node._id,
                               label=node.name,
                               occupied=node._occupied,
                               explored=node._explored,
                               sum_heuristic=node.sum_heuristic,
                               step=node.step,
                               start=node.start)
                for child in node.children:
                    G.add_edge(node._id, child._id, color=child.edge_color)
                    edge_labels[(node._id, child._id)] = child.path_cost
                    add_edges(child)

            add_edges(frame)
            #determine edge colors, always the same except in the last frame
            edge_colors = [edge[2]['color'] for edge in G.edges(data=True)]
            ##determine node color and label
            node_colors = []
            node_labels = {}
            for node, data in G.nodes(data=True):
                node_labels[node] = (f"{data.get('label')}\n" +
                                     f"∑h(x): {data.get('sum_heuristic')}\n" +
                                     f"id: {node}\n" +
                                     f"step: {data.get('step')}")
                if data.get("start", False):
                    node_colors.append("yellow")
                elif data.get("occupied", False):
                    node_colors.append("green")
                elif data.get("explored", False):
                    node_colors.append("lightgreen")
                else:
                    node_colors.append("lightblue")
            ## Tree layout (Graphviz better for hierarchical structures)
            try:
                pos = nx.nx_agraph.graphviz_layout(G, prog="dot")  # Needs pygraphviz
            except ImportError:
                pos = nx.planar_layout(G)  # Fallback layout

            nx.draw(G, pos, with_labels=False, node_color=node_colors, edge_color=edge_colors, edge_cmap=plt.cm.Blues,
                    node_size=2000, ax=ax)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, label_pos=0.5, ax=ax)
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_weight="bold", font_size=10, ax=ax)

        ani = animation.FuncAnimation(fig, _plot_frame,
                                      frames=self._frames, interval=1000, repeat=False)
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    # define nodes with their heuristic
    nodes = {
        "a": 5, "b": 6, "c": 8, "d": 4,
        "e": 4, "f": 5, "g": 2, "h": 0
    }
    # define edges and stepcost
    edges = (
        ("a", "b", 3), ("a", "c", 3), ("b", "d", 2),
        ("d", "e", 4), ("c", "f", 3), ("e", "f", 1),
        ("e", "g", 2), ("f", "g", 3), ("g", "h", 2)
    )

    g =AStarTree(nodes, edges, "a", "h")
