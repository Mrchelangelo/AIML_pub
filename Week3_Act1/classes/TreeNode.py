class TreeNode:
    """
    A class representing a node in a tree structure, with support for parent-child relationships,
    heuristic values, and edge attributes such as color and path cost.

    Attributes:
        name (str): The name of the node.
        _id (int): A unique identifier for the node.
        _occupied (bool): Indicates whether the node is occupied.
        _explored (bool): Indicates whether the node has been explored.
        step (int): indicates when the node was explored
        _neighbors (list): A list of neighboring nodes.
        heuristic (float): The heuristic value of the node.
        sum_heuristic (float): The cumulative heuristic value from root to this node.
        children (list): A list of child nodes.
        parent (TreeNode or None): The parent node.
        edge_color (str): The color of the edge connecting to the parent.
        path_cost (float): The cost associated with the edge to the parent.
        sum_path_cost (float): The cumulative path cost from root to this node.

    Class Attributes:
        node_counter (int): A counter to assign unique IDs to each node.
    """
    node_counter = 0  # Class-level counter for unique node IDs

    def __init__(self, name, heuristic, neighbors=None, parent=None, edge_color="black", path_cost=0):
        """
        Initializes a TreeNode with given attributes.

        Args:
            name (str): The name of the node.
            heuristic (float): The heuristic value of the node.
            neighbors (list, optional): A list of neighboring nodes (default: None).
            parent (TreeNode, optional): The parent node (default: None).
            edge_color (str, optional): The color of the edge connecting to the parent (default: "black").
            path_cost (float, optional): The cost associated with the edge to the parent (default: 0).
        """
        self.name = name
        self._id = TreeNode.node_counter  # Assign a unique ID
        TreeNode.node_counter += 1  # Increment ID counter

        self._occupied = False  # Track if the node is occupied
        self._explored = False  # Track if the node is explored
        self.step = ""  # Step description
        self.start = False
        self._neighbors = neighbors if neighbors is not None else []  # Store neighbors

        self.heuristic = heuristic
        self.sum_heuristic = heuristic  # Will be updated if a parent exists

        self.children = []  # List of child nodes
        self.parent = parent  # Reference to parent node

        self.edge_color = edge_color  # Edge color
        self.path_cost = path_cost  # Path cost
        self.sum_path_cost = path_cost  # Cumulative path cost

        if parent:
            parent.add_child(self, edge_color, path_cost)

    def add_child(self, child, edge_color="black", path_cost=0):
        """
        Adds a child node and updates cumulative heuristic and path cost values.

        Args:
            child (TreeNode): The child node to add.
            edge_color (str, optional): The color of the edge connecting to the child (default: "black").
            path_cost (float, optional): The cost associated with the edge to the child (default: 0).
        """
        child.parent = self
        child.edge_color = edge_color
        child.path_cost = path_cost
        child.sum_heuristic = self.sum_heuristic + child.heuristic
        child.sum_path_cost = self.sum_path_cost + path_cost
        self.children.append(child)

    def toggle_occupied(self):
        """Toggles the occupied status of the node."""
        self._occupied = not self._occupied

    def toggle_start(self):
        """Toggles the occupied status of the node."""
        self.start = not self.start

    def toggle_explored(self):
        """Toggles the explored status of the node."""
        self._explored = not self._explored

    def set_step(self, step: str):
        """
        Sets the step description for the node.

        Args:
            step (str): The step description.
        """
        self.step = step

    def __repr__(self):
        """Returns a string representation of the node."""
        return f"TreeNode({self.name}, h={self.heuristic}, sum_h={self.sum_heuristic})"
