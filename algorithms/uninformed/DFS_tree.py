"""
Class to handle Best First Search, as graph.
"""
# import packages
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
from algorithm.utils.TreeNode import TreeNode
import copy
class BFS:
    def __init__(self, nodes: list,
                 edges: tuple,
                 start_node: str = "a",
                 end_node: str = "h"):
        self._end_node = end_node
        self._step=0
        self._graph = nx.Graph()
        self._fill_graph(edges, nodes)
        self._frames = []
        self._frontier = deque() #create frontier
        self._explored = [] #save explored nodes
        self._came_from = {} #save the parent of a node
        self._path = [] ##safe solution
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
                                neighbors=self._graph.neighbors(current_node),
                                frontier=True,
                                )
        current_node.toggle_start()
        current_node.set_step(self._step)
        self._root = current_node ##set root for search tree
        self._frontier.append(current_node) ##expand frontier
        while current_node: ##start search loop
            current_node = self._frontier.pop()
            current_node.toggle_frontier()
            current_node.toggle_occupied() ##toogle node to occupied
            current_node.set_step(self._step) ##set search step (redundand for start node, but needed earlier)
            ## check if reached goal
            if current_node.name == goal:
                self._end_leaf = current_node
                while current_node:##generate solution
                    self._path.append(current_node._id) ##add node to path solution
                    ##find parent of node or None(for the start node)
                    current_node.edge_color = "red" ##set path color for later visualisation
                    current_node = current_node.parent ##switch to next node on path
                self._path = list(reversed(list(self._path))) ##reverse path to have right order
                self._frames.append((self._root, self._frontier.copy())) ##append a last snapshot of solved tree
                return None

            current_node.toggle_occupied() ##to to unoccupied
            current_node.toggle_explored() ##set as explored
            ## expand frontier and save parent for newly added nodes
            for node in current_node._neighbors: ##get neighbors to expand frontier
                    node_data = self._graph.nodes[node] ##get attributes of node (h(x), neighbors)
                    self._frontier.append( ##add node to frontier
                        TreeNode(
                            node,
                            frontier=True,
                            neighbors=self._graph.neighbors(node), ##neighbors for later expansion of frontier
                            parent=current_node, ##parent, for tree struktur and later path generation
                            path_cost=self._graph.get_edge_data(current_node.name,
                                                                node)["stepcost"], ##cost to get to the node from parent
                        )
                    )
            self._frames.append((copy.deepcopy(self._root), self._frontier.copy()))  ##append snapshot of current search tree for animation
            self._step += 1

    def _get_path_cost(self):
        self._path_cost = {
            "stepcost": self._end_leaf.sum_path_cost
        }
        print("The stepcost for the path is: ",
              self._path_cost["stepcost"])

    def _fill_graph(self, edges, nodes):
        for node in nodes:
            ## add each node with its heuristic
            self._graph.add_node(node,
                                 explored=False, occupied=False,
                                 frontier=False,
                                 step=""
                                 )
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
                               frontier=node._frontier,
                               step=node.step,
                               start=node.start)
                for child in node.children:
                    G.add_edge(node._id, child._id, color=child.edge_color)
                    edge_labels[(node._id, child._id)] = child.path_cost
                    add_edges(child)

            add_edges(frame[0])
            #determine edge colors, always the same except in the last frame
            edge_colors = [edge[2]['color'] for edge in G.edges(data=True)]
            ##determine node color and label
            node_colors = []
            node_labels = {}
            for node, data in G.nodes(data=True):
                node_labels[node] = (f"{data.get('label')}\n" +
                                     f"id: {node}\n" +
                                     f"step: {data.get('step')}")
                if data.get("start", False):
                    node_colors.append("yellow")
                elif data.get("occupied", False):
                    node_colors.append("green")
                elif data.get("explored", False):
                    node_colors.append("lightgreen")
                elif data.get("frontier", False):
                    node_colors.append("pink")
                else:
                    node_colors.append("lightblue")
            ## Tree layout (Graphviz better for hierarchical structures)
            #try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")  # Needs pygraphviz
           # except ImportError:
            #    pos = nx.planar_layout(G)  # Fallback layout

            nx.draw(G, pos, with_labels=False, node_color=node_colors, edge_color=edge_colors, edge_cmap=plt.cm.Blues,
                    node_size=2000, ax=ax)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, label_pos=0.5, ax=ax)
            nx.draw_networkx_labels(G, pos, labels=node_labels, font_weight="bold", font_size=10, ax=ax)

            ax.text(0, -1, f"Frontier: {[ele.name for ele in frame[1]]}",
                    horizontalalignment='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

        ani = animation.FuncAnimation(fig, _plot_frame,
                                      frames=self._frames, interval=100, repeat=False)
        plt.axis("off")
        plt.show()


if __name__ == "__main__":
    # define nodes with their heuristic
    nodes = [
        "a", "b", "c", "d",
        "e", "f", "g", "h",
        "i", "j", "k", "l",
        "m", "n", "o"
    ]
    # define edges and stepcost
    edges = (
        ("a", "b", 3), ("a", "c", 3), ("b", "d", 2),
        ("d", "e", 4), ("c", "f", 3), ("e", "f", 1),
        ("e", "g", 2), ("f", "g", 3), ("g", "h", 2),
        ("h", "o", 2), ("o", "n", 3), ("n", "m", 2),
        ("m", "l", 2), ("l", "k", 3), ("k", "i", 2),
        ("n", "l", 2), ("l", "b", 3), ("b", "i", 2),
        ("n", "j", 2), ("j", "d", 3)
    )

    g = BFS(nodes, edges, "a", "h")