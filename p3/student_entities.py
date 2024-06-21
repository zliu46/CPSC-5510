"""
CPSC 5510, Seattle University, Project #3
:Author: student #4173058  Zhou Liu
:Version: s24
"""

# YOU MAY NOT ADD ANY IMPORTS
from entity import Entity
from student_utilities import to_layer_2

NODES = 4 #number of nodes
INFINITY = 999 #integer value 999 is infinity. 

def common_init(self):
    """
    Initialize the distance table and send initial distance vectors to neighbors.
    
    This function sets up the distance table with initial values based on direct costs to neighbors.
    It then prints the initialized distance table and sends the initial minimum cost paths to neighbors.
    """
    self.distance_table = [[INFINITY for _ in range(NODES)] for _ in range(NODES)]
    print(f"entity {self.id}: initializing")
    for i in range(NODES):
        self.distance_table[self.id][i] = self.costs[i]
    self.printdt()
    self.send_updates()

def common_update(self, packet):
    """
    Update the distance table based on incoming packets and send updated distance vectors if necessary.
    
    This function processes incoming packets, updating the distance table if a shorter path is found.
    If the distance table is updated, it sends the new minimum cost paths to neighbors.
    
    Args:
        packet (Packet): The incoming packet containing source node ID and minimum cost to each node.
    """
    print(f"node {self.id}: update from {packet.src} received")
    updated = False
    source = packet.src
    for i in range(NODES):
        if self.distance_table[i][source] > packet.mincost[i]:
            self.distance_table[i][source] = packet.mincost[i]
            new_cost = self.costs[source] + packet.mincost[i]
            if new_cost < self.distance_table[i][self.id]:
                self.distance_table[i][self.id] = new_cost
                updated = True
    if updated:
        print(f"change based on update")
        self.printdt()
        self.send_updates()
    else:
        print(f"no changes in node {self.id}, so nothing to do")
        self.printdt()

def common_link_cost_change(self, to_entity, new_cost):
    """
    Handle link cost changes and update the distance table.
    
    This function updates the distance table when the cost to a direct neighbor changes.
    It then sends the new minimum cost paths to neighbors.
    
    Args:
        to_entity (int): The ID of the neighboring node.
        new_cost (int): The new cost to the neighboring node.
    """
    # self.costs[to_entity] = new_cost
    # for i in range(NODES):
    #     if i != self.id:
    #         self.distance_table[i][self.id] = min(
    #             self.distance_table[i][j] + self.costs[j]
    #             for j in range(NODES)
    #         )
    self.costs[to_entity] = new_cost
    updated = False
    for i in range(NODES):
        if i == self.id:
            continue
        current_cost = self.distance_table[i][self.id]
        new_path_cost = self.distance_table[i][to_entity] + new_cost
        if new_path_cost < current_cost:
            self.distance_table[i][self.id] = new_path_cost
            updated = True
    print(f"Check check check check check check")
    if updated:
        self.send_updates()
    self.send_updates()

class Entity0(Entity):
    def __init__(self):
        """Router running a DV algorithm at node 0"""
        super().__init__()
        self.id = 0
        self.costs = [0, 1, 3, 7]
        self.neighbors = [1, 2, 3]
        common_init(self)

    def update(self, packet):
        """Update distance table based on incoming packet."""
        common_update(self, packet)

    def link_cost_change(self, to_entity, new_cost):
        """Handle link cost change to a neighboring node."""
        common_link_cost_change(self, to_entity, new_cost)

    def send_updates(self):
        """Send the current minimum cost paths to all directly connected neighbors."""
        for neighbor in self.neighbors:
            to_layer_2(self.id, neighbor, self.distance_table[self.id][:])

    def printdt(self):
        """Print the current distance table."""
        print(f"node: {self.id}")
        for i in range(NODES):
            print(self.distance_table[i])

class Entity1(Entity):
    def __init__(self):
        """Router running a DV algorithm at node 1"""
        super().__init__()
        self.id = 1
        self.costs = [1, 0, 1, INFINITY]
        self.neighbors = [0, 2]
        common_init(self)

    def update(self, packet):
        """Update distance table based on incoming packet."""
        common_update(self, packet)

    def link_cost_change(self, to_entity, new_cost):
        """Handle link cost change to a neighboring node."""
        common_link_cost_change(self, to_entity, new_cost)

    def send_updates(self):
        """Send the current minimum cost paths to all directly connected neighbors."""
        for neighbor in self.neighbors:
            to_layer_2(self.id, neighbor, self.distance_table[self.id][:])

    def printdt(self):
        """Print the current distance table."""
        print(f"node: {self.id}")
        for i in range(NODES):
            print(self.distance_table[i])

class Entity2(Entity):
    def __init__(self):
        """Router running a DV algorithm at node 2"""
        super().__init__()
        self.id = 2
        self.costs = [3, 1, 0, 2]
        self.neighbors = [0, 1, 3]
        common_init(self)

    def update(self, packet):
        """Update distance table based on incoming packet."""
        common_update(self, packet)

    def link_cost_change(self, to_entity, new_cost):
        """Handle link cost change to a neighboring node."""
        common_link_cost_change(self, to_entity, new_cost)

    def send_updates(self):
        """Send the current minimum cost paths to all directly connected neighbors."""
        for neighbor in self.neighbors:
            to_layer_2(self.id, neighbor, self.distance_table[self.id][:])

    def printdt(self):
        """Print the current distance table."""
        print(f"node: {self.id}")
        for i in range(NODES):
            print(self.distance_table[i])

class Entity3(Entity):
    def __init__(self):
        """Router running a DV algorithm at node 3"""
        super().__init__()
        self.id = 3
        self.costs = [7, INFINITY, 2, 0]
        self.neighbors = [0, 2]
        common_init(self)

    def update(self, packet):
        """Update distance table based on incoming packet."""
        common_update(self, packet)

    def link_cost_change(self, to_entity, new_cost):
        """Handle link cost change to a neighboring node."""
        common_link_cost_change(self, to_entity, new_cost)

    def send_updates(self):
        """Send the current minimum cost paths to all directly connected neighbors."""
        for neighbor in self.neighbors:
            to_layer_2(self.id, neighbor, self.distance_table[self.id][:])

    def printdt(self):
        """Print the current distance table."""
        print(f"node: {self.id}")
        for i in range(NODES):
            print(self.distance_table[i])
