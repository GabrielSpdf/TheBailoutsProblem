import numpy as np
from map import Map
from cluster import *

class Manager():
    def __init__(self, resc1, resc2, resc3, resc4):
        self.resc1 = resc1
        self.resc2 = resc2
        self.resc3 = resc3
        self.resc4 = resc4
        self.map = Map()             
        self.victims = {}         
        self.map_counter = 0        

    # Espera-se que haja quatro mapas
    def full_join_maps(self, map):
        print(f"Resgate com {self.map_counter} mapa(s)")
        if(self.map_counter == 0):
            self.map = map
            self.map_counter = self.map_counter + 1

        elif(self.map_counter == 1 or self.map_counter == 2):
            self.map.union_maps(map)
            self.map_counter = self.map_counter + 1

        elif(self.map_counter == 3):
            self.map.union_maps(map)
            self.map_counter = self.map_counter + 1
            print("Resgate com todos os mapas!")
            self.plan_to_rescuer()
            print("Clusterizacao concluida!")


    def assign_victims_to_rescuers(self, centroids):
        """Atribui as vítimas de cada cluster aos resgatadores."""
        self.resc1.add_victims(centroids[0][2])
        self.resc2.add_victims(centroids[1][2])
        self.resc3.add_victims(centroids[2][2])
        self.resc4.add_victims(centroids[3][2])

    def assign_map_to_rescuers(self):
        """Atribui o mapa a cada resgatador"""
        self.resc1.load_map(self.map)
        self.resc2.load_map(self.map)
        self.resc3.load_map(self.map)
        self.resc4.load_map(self.map)

    def add_man_victims(self, victims):
        for seq, data in victims.items():
            self.victims[seq] = data

    def plan_to_rescuer(self):
        clusters = k_means_pp(self.victims)
        save_clusters(clusters)

        save_plot(clusters)

        self.assign_victims_to_rescuers(clusters)
        self.assign_map_to_rescuers()

