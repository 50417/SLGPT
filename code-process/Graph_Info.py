
import math
class Graph_Info():
    def __init__(self , name):
        self.simulink_name = name
        #self.source_destination_path = []
        #self.subgraphs = []
        self.subgraphs_size = []
        self.no_of_subgraphs = 0
        self.source_destination_path = False
        self.max_source_destination_path_length = 0
        self.min_source_destination_path_length = math.inf
        self.max_sub_graph_size = 0


    def addpath(self,path):
        #self.source_destination_path.append(path)

        self.source_destination_path = True
        self.max_source_destination_path_length = max(len(path),self.max_source_destination_path_length)

        self.min_source_destination_path_length = min(len(path),self.min_source_destination_path_length)

    def add_subgraph(self,sg):
        if (len(sg) != 0):
            self.no_of_subgraphs+=1
        #self.subgraphs.append(sg)
        self.max_sub_graph_size = max(self.max_sub_graph_size,len(sg))
        self.subgraphs_size.append(len(sg))
