"""
Class to handle Deep First Search, as graph.
"""
# import packages
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import copy
class IDS:
    def __init__(self, nodes: list,
                 edges: tuple,
                 start_node: str = "a",
                 end_node: str = "h"):
        self._end_node = end_node
        self._start_node = start_node
        self._step = 0
        self._limit = 0
        self._unsolved = True
        self._nodes = nodes
        self._edges = edges
        self._frames = []
        self._frontier = deque() #create frontier
        self._explored = [] #save explored nodes
        self._came_from = {} #save the parent of a node
        self._path = [] ##safe solution
        self._search(start_node, end_node)
        self._get_path_cost()
        self.visualise()

    def _search(self, current_node, goal):
        self._graph = nx.Graph()
        self._fill_graph(self._edges, self._nodes)
        self._graph.nodes[current_node]["start"] = True
        self._frontier.append(current_node)
        while self._unsolved:
            current_node = self._frontier.pop()
            self._graph.nodes[current_node]["occupied"] = True
            self._graph.nodes[current_node]["frontier"] = False
            self._graph.nodes[current_node]["step"] = self._step
            ## check if reached goal
            if current_node == goal:
                while current_node:
                    self._path.append(current_node)
                    ##find parent of node or None(for the start node)
                    current_node = self._came_from.get(current_node)
                self._path = list(self._path)
                for node1, node2 in zip(
                        self._path[:-1], self._path[1:]):
                    self._graph[node1][node2]["color"] = "red"
                self._frames.append((self._graph.copy(), self._frontier.copy(), copy.deepcopy(self._limit)))
                self._unsolved=False
                return None

            ## add node to explored
            self._explored.append(current_node)
            ## expand frontier and save parent for newly added nodes
            for node in self._graph.neighbors(current_node):
                if not (node in self._frontier or
                 node in self._explored):
                    self._came_from[node] = current_node
                    depth = []
                    dummy_node = node
                    while dummy_node:
                        depth.append(dummy_node)
                        dummy_node = self._came_from.get(dummy_node)
                    if len(depth) > self._limit:
                        continue
                    self._frontier.append(node)
                    self._graph.nodes[node]["frontier"] = True
            self._graph.nodes[current_node]["occupied"] = False
            self._graph.nodes[current_node]["explored"] = True
            self._step += 1
            self._frames.append((self._graph.copy(), self._frontier.copy(), copy.deepcopy(self._limit)))
            if not self._frontier:
                self._explored = []
                self._limit += 1
                self._search(self._start_node, self._end_node)


    def _get_path_cost(self):
        self._path_cost = {
            "stepcost": sum(
                self._graph.get_edge_data(node1, node2)["stepcost"]
                for node1, node2 in zip(
                    self._path[:-1], self._path[1:]
                )
            )
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
        fig, ax = plt.subplots(figsize=(8, 6))
        pos = nx.kamada_kawai_layout(self._graph)  # Layout for positioning
        def _plot_frame(frame):
            ax.clear()

            node_colors = []
            for node, data in frame[0].nodes(data=True):
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
            # Draw nodes
            nx.draw_networkx_nodes(frame[0], pos, node_color=node_colors, node_size=2000,
                                   edgecolors="black", ax=ax)
            edge_colors = [edge[2]['color'] for edge in frame[0].edges(data=True)]
            # Draw edges with weights
            nx.draw_networkx_edges(frame[0], pos, width=1.5, edge_color=edge_colors)
            # Add edge labels (step cost)
            edge_labels = {(u, v): f"{d['stepcost']}" for u, v, d in frame[0].edges(data=True)}
            nx.draw_networkx_edge_labels(frame[0], pos, edge_labels=edge_labels,
                                         font_size=10, font_color="black", ax=ax)
            # Add node labels (name + heuristic)
            node_labels = {node: f"{node}\nstep: {data['step']}"
                           for node, data in frame[0].nodes(data=True)}
            nx.draw_networkx_labels(frame[0], pos, labels=node_labels,
                                    font_size=12, font_color="black", ax=ax)
            ax.text(0, -1, f"Frontier: {[ele for ele in frame[1]]}",
                     horizontalalignment='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
            if frame[1]:
                ax.text(0, 1, f"Limit: {frame[2]}",
                        horizontalalignment='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))
            else:
                ax.text(0, 1, "No Solution found",
                        horizontalalignment='center', fontsize=10, bbox=dict(facecolor='white', alpha=0.5))

        ani = animation.FuncAnimation(fig, _plot_frame,
                                      frames=self._frames, interval=800, repeat=False)
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
        ("n", "l", 2), ("m", "k", 3), ("b", "m", 2),
        ("n", "j", 2), ("j", "d", 3), ("d", "c", 2)
    )

    g = IDS(nodes, edges, "a", "h")