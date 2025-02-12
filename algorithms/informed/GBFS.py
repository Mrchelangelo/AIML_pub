"""
Date: 03.01.2025
Purpose: Solve Activity 1 from Week 3 in AIML - navigate a robot around obstacles
Apply Greedy Best First Search Algorithm with Manhattan Distance as heuristic
"""
# import packages
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class GBFS:
    def __init__(self, nodes: dict,
                 edges: tuple,
                 start_node: str = "a",
                 end_node: str = "h"):
        self._graph = nx.Graph()
        self._fill_graph(edges, nodes)
        self._step = 0
        self._frames = [self._graph.copy()]
        self._frontier = [start_node] #create frontier
        self._explored = [] #save explored nodes
        self._came_from = {} #save the parent of a node
        self._path = [] ##safe solution
        self._search(start_node, end_node)
        self._get_path_cost()
        self.visualise()

    def _search(self, current_node, goal):
        self._graph.nodes[current_node]["start"] = True
        while current_node:
            self._graph.nodes[current_node]["occupied"] = True
            self._graph.nodes[current_node]["step"] = self._step
            self._frames.append(self._graph.copy())
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
                self._frames.append(self._graph.copy())
                return None

            ## add node to explored and remove from frontier
            self._explored.append(current_node)
            self._frontier.remove(current_node)
            ## expand frontier and save parent for newly added nodes
            for node in self._graph.neighbors(current_node):
                if not (node in self._frontier or
                 node in self._explored):
                    self._frontier.append(node)
                    self._came_from[node] = current_node
            self._graph.nodes[current_node]["occupied"] = False
            self._graph.nodes[current_node]["explored"] = True
            ## define next node based on heuristic
            current_node = self._find_next()


    def _find_next(self):
        self._step += 1
        if len(self._frontier) == 0:
            return False ##if there is no solution
        min = float("inf")
        min_node = None
        for node in self._frontier:
            if self._graph.nodes[node]["heuristic"] < min:
                min = self._graph.nodes[node]["heuristic"]
                min_node = node
        return min_node

    def _get_path_cost(self):
        self._path_cost = {
            "heuristic": sum(self._graph.nodes[ele]["heuristic"]
                             for ele in self._path),
            "stepcost": sum(
                self._graph.get_edge_data(node1, node2)["stepcost"]
                for node1, node2 in zip(
                    self._path[:-1], self._path[1:]
                )
            )
        }
        print("The heuristic cost for the path is: ",
              self._path_cost["heuristic"],
              "\nThe stepcost for the path is: ",
              self._path_cost["stepcost"])

    def _fill_graph(self, edges, nodes):
        for node, heuristic in nodes.items():
            ## add each node with its heuristic
            self._graph.add_node(node, heuristic=heuristic,
                                 explored=False, occupied=False,
                                 step="", start=False)
        for node1, node2, stepcost in edges:
            ## add each edges with its stepcost
            self._graph.add_edge(node1, node2, stepcost=stepcost, color="black")

    def visualise(self):
        fig, ax = plt.subplots(figsize=(8, 6))
        pos = nx.kamada_kawai_layout(self._graph)  # Layout for positioning
        def _plot_frame(frame):
            ax.clear()

            node_colors = []
            for node, data in frame.nodes(data=True):
                if data.get("start", False):
                    node_colors.append("yellow")
                elif data.get("occupied", False):
                    node_colors.append("green")
                elif data.get("explored", False):
                    node_colors.append("lightgreen")
                else:
                    node_colors.append("lightblue")
            edge_colors = [edge[2]['color'] for edge in frame.edges(data=True)]
            # Draw nodes
            nx.draw_networkx_nodes(frame, pos, node_color=node_colors, node_size=2000,
                                   edgecolors="black", ax=ax)
            # Draw edges with weights
            nx.draw_networkx_edges(frame, pos, width=1.5, edge_color=edge_colors)
            # Add edge labels (step cost)
            edge_labels = {(u, v): f"{d['stepcost']}" for u, v, d in frame.edges(data=True)}
            nx.draw_networkx_edge_labels(frame, pos, edge_labels=edge_labels,
                                         font_size=10, font_color="black", ax=ax)
            # Add node labels (name + heuristic)
            node_labels = {node: f"{node}\nh(x): {data['heuristic']}\nstep: {data['step']}"
                           for node, data in frame.nodes(data=True)}
            nx.draw_networkx_labels(frame, pos, labels=node_labels,
                                    font_size=12, font_color="black", ax=ax)

        ani = animation.FuncAnimation(fig, _plot_frame,
                                      frames=self._frames, interval=800, repeat=False)
        plt.axis("off")
        plt.show()

if __name__ == "__main__":
    # define nodes with their heuristic
    nodes = {
        "h": 20, "t": 12, "l": 17, "y": 8,
        "p": 0, "w": 12, "m": 10, "s": 19
    }
    # define edges and stepcost
    edges = (
        ("m", "s", 17), ("t", "m", 5), ("y", "m", 12),
        ("h", "t", 12), ("y", "t", 6), ("m", "p", 10),
        ("h", "l", 10), ("y", "l", 16), ("p", "w", 15),
        ("l", "w", 8)
    )

    g = GBFS(nodes, edges, "h", "p")
