import sys
import numpy
import csv

# .csv filed passed in commandline
top_file = sys.argv[1]

class Topology():
    def __init__(self, file):
        # open the .csv file and store the data
        with open(file, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
        # create a 2d array of the data
        self.graph = numpy.array(data)
        # store the node names
        self.nodes = self.graph[0, 1:].tolist()
        # list of paths starting from src
        self.paths = [""] * (len(self.nodes))
    
    def min_distance(self, distances, already_done):
        # initially, the minimum distance to check agains is infinity
        min_dist = 9999
        
        # iterate through the indexes of the nodes and return the index with the lowest distance to the src node
        for node_index in range(len(self.nodes)):
            # checking if node's distance is less than current minimum & that is has not already been stored in D'
            if (already_done[node_index] == False and int(distances[node_index]) < min_dist):
                min_dist = int(distances[node_index])
                min_node = node_index
        return min_node
    
    def dijkstra_alg(self, source_node):
        # create a list of the distance of every node to the source node
        distances = self.graph[1:, self.nodes.index(source_node) + 1].tolist()
        # making the src node the first node in each path
        for node_index in range(len(self.paths)):
            if (node_index == self.nodes.index(source_node)):
                continue
            self.paths[node_index] += source_node
            # if there are paths to other nodes, pre-set those
            if (int(distances[node_index]) != 9999):
                self.paths[node_index] += self.nodes[node_index]

        # a list to keep track of the nodes not yet visited
        already_done = [False] * len(self.nodes)

        # N'
        path = ''
        paths_print = ''

        for node_index in range(len(self.nodes)):
            # choose the node with the minimum distance
            cur_node = self.min_distance(distances, already_done)

            # add this node to the path    
            path += self.nodes[cur_node]

            # show that this node has been accounted for
            already_done[cur_node] = True

            # update distances for the new node
            for node_index in range(len(self.nodes)):
                # distance from currently addressed node to each other node
                updated_dist = int(self.graph[cur_node + 1, node_index + 1])
                # this checks that the each checked node has not already been accounted for and whether or not the distance
                # from the src node to the current node plus the distance from the current node to each other node is shorter
                # than the distance from just the src node to each node
                if (updated_dist > 0 and already_done[node_index] == False and int(distances[node_index]) > int(distances[cur_node]) + updated_dist):
                    distances[node_index] = int(distances[cur_node]) + updated_dist
                    # this builds the paths between source and each router each time a better distance is found.
                    # if a better distance is found, that means that the path from source to the cur_node to the node_index node
                    # will be better than whatever the path was before.
                    self.paths[node_index] = source_node + self.paths[cur_node][1:] + self.nodes[node_index]

        # print all of the output for Link-State alg
        print (f"Shortest path tree for node {source_node}:")
        paths_print = ''
        for c in path:
            if c != source_node:
                index = self.nodes.index(c)
                paths_print += str(self.paths[index]) + ", "
        print (paths_print[:-2])
        print(f"Costs of the least-cost paths for node {source_node}:")
        distances_print = ''
        for i in range(len(distances)):
            distances_print += str(self.nodes[i]) + ':' + str(distances[i]) + ", "
        print (distances_print[:-2])

    def is_neighbor(self):
        # you have to build the list this way because python is weird and otherwise it causes bugs
        is_neighbor = [[False for i in range(len(self.nodes))] for j in range(len(self.nodes))]

        # iterate through each index in the 2d array and check if the nodes are connected, update the is_neighbor array
        for node_index_1 in range(len(self.nodes)):
            for node_index_2 in range(len(self.nodes)):
                if (int(self.graph[node_index_1 + 1, node_index_2 + 1]) != 9999):
                    is_neighbor[node_index_1][node_index_2] = True
                    #print(is_neighbor)
        return is_neighbor
        
    # distance_vector_alg
    def distance_vector(self):
        # run is_neighbor to get the array for later use
        neighbor_list = self.is_neighbor()
        # copy the graph in the instance variables for modification
        local_graph = self.graph[1:, 1:]
        # make a copy of that copy so we can update the local_graph only after each successive loop
        local_graph_2 = local_graph
        # need to have a list of which nodes have updated their costs
        has_changed = [True] * len(self.nodes)
        # a flag that is set if there are changes to any given node's cost list
        has_changed_flag = False

        # THIS IS THE ITERATIVE STEP OF DISTANCE VECTOR
        # keep iterating through each node's list until there are no more changes
        while (True in has_changed):
            # iteration through each node's list
            for primary_node_index in range(len(self.nodes)):
                # reset flag for each new list
                has_changed_flag = False

                for node_index_1 in range(len(self.nodes)):
                    for node_index_2 in range(len(self.nodes)):
                        # There are many situations that we don't want to make changes or check
                        # 1. we don't need to compare the distance to the same node (ie u->w vs u->w->w)
                        # 2. the primary node and the second node must be neighbors
                        # 3 & 4. we don't need to compare any distances involving primary node (ie u->u->(any node) or u->w->u)
                        # 5. we don't need to compare distances to nodes that didn't have changes in the last run (if a node didn't have changes it doesn't send the list)
                        if (node_index_1 == node_index_2 or neighbor_list[primary_node_index][node_index_1] == False or primary_node_index == node_index_1 or primary_node_index == node_index_2 or has_changed[node_index_1] == False):
                            continue
                        # THIS IS THE PART OF DISTANCE VECTOR WHERE THE NODE COMPARES DISTANCES TO IT'S NEIGHBOR'S COSTS
                        # if the distance from our primary node to our third node is greater than the distance from the primary to the second to the third, we update cost
                        if (int(local_graph[primary_node_index, node_index_2]) > (int(local_graph[primary_node_index, node_index_1]) + int(local_graph[node_index_1, node_index_2]))):
                            # set the flag since something changed
                            has_changed_flag = True
                            # update our list to be sent out
                            local_graph_2[primary_node_index, node_index_2] = int(local_graph[primary_node_index, node_index_1]) + int(local_graph[node_index_1, node_index_2])
                # ccheck the flag and update the list of changed primary lists accordingly
                if (has_changed_flag):
                    has_changed[primary_node_index] = True
                else:
                    has_changed[primary_node_index] = False
            # THIS IS THE PART OF DISTANCE VECTOR WHERE EACH NODE SENDS IT'S DISTANCE VECTOR TO IT'S NEIGHBORS
            # update the local graph
            local_graph = local_graph_2
        
        # print out the individual distance vectors
        print("\n")
        node_index = 0
        for vector in local_graph:
            formated_vector = " ".join(vector)
            print(f"Distance vector for node {self.nodes[node_index]}: {formated_vector}")
            node_index += 1

top = Topology(top_file)

source_node = input("Please provide the source node: ")

while (source_node not in top.nodes):
    print(f"Not a valid source node. Valid source nodes are {top.nodes}")
    source_node = input("Please provide the source node:\n")

top.dijkstra_alg(source_node)
    
top.distance_vector()
