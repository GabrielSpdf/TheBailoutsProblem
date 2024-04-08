# EXPLORER AGENT
# @Author: Tacla, UTFPR
#
### It walks randomly in the environment looking for victims. When half of the
### exploration has gone, the  goes back to the base.

import sys
import os
import random
import math
import time
from abc import ABC, abstractmethod
from vs.abstract_agent import AbstAgent
from vs.constants import VS
from map import Map
from opt import Opt 

class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()

    def is_empty(self):
        return len(self.items) == 0

class Explorer(AbstAgent):
    def __init__(self, env, config_file, resc, vec):
        """ Construtor do agente random on-line
        @param env: a reference to the environment 
        @param config_file: the absolute path to the 's config file
        @param resc: a reference to the rescuer agent to invoke when exploration finishes
        """

        super().__init__(env, config_file)
        self.walk_stack = Stack()  # a stack to store the movements
        self.set_state(VS.ACTIVE)  #  is active since the begin
        self.resc = resc           # reference to the rescuer agent
        self.x = 0                 # current x position relative to the origin 0
        self.y = 0                 # current y position relative to the origin 0

        self.plan = []
        self.plan_x = 0
        self.plan_y = 0
        self.clock = 0
        self.plan_visited = set()
        self.map = Map()           # create a map for representing the environment
        self.opt = Opt() 
        self.time_back = (self.TLIM/2)
        self.vector = vec
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
        self.opt.add_coord((self.x, self.y), 0)

    def get_next_position(self, vec):
        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()

        for i in range(8):
            time.sleep(0.01)

            #Vetor de prioridade
            print(f"Direção: {vec[i]}")
            direction = vec[i]

            prox_x, prox_y = Explorer.AC_INCR[direction]
            # print(f"self.x: {self.x}")
            # print(f"self.y: {self.y}")

            # print(f"prox_x: {prox_x}")
            # print(f"prox_y: {prox_y}")
            target_xy = (self.x + prox_x, self.y + prox_y)
            # print(f"target_xy: {target_xy}")

            if self.opt.ver_coord(target_xy):
                print("Ja visitado 1")
                print(1)
                continue

            #Check if pos was already visited
            if (target_xy in self.plan_visited):
                print("Ja visitado 2")
                continue
            
            #Check if pos is valid
            if obstacles[direction] == VS.CLEAR:
                self.plan_x = self.x
                self.plan_y = self.y

                self.plan_x += prox_x
                self.plan_y += prox_y
                # print(f"self.plan_x: {self.plan_x}")
                # print(f"self.plan_y: {self.plan_y}")

                #Pos added to set
                self.plan_visited.add((self.plan_x, self.plan_y))
                
                print("Andou")
                if(prox_x != 0 and prox_y != 0):
                    self.clock += 1.5
                else:
                    self.clock += 1

                print(f"Tempo total: {self.TLIM}")
                print(f"Tempo consumido: {self.clock}")

                print("Mapa: ")
                print(self.opt.get_all())
                return Explorer.AC_INCR[direction]
   

        #If agent hasnt possible movements
        print("retornou -2 -2")
        return -2, -2


        
    def explore(self):

        dx, dy = self.get_next_position(self.vector)

        if((dx, dy) == (-2, -2)):
            print("fudeu2")
            self.come_back()

        # Moves the body to another position
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()


        print(f"Resultado: {result}")
        #@returns -1 = the agent bumped into a wall or reached the end of grid
        #@returns -2 = the agent has no enough time to execute the action
        #@returns 1 = the action is succesfully executed

        # Test the result of the walk action
        # Should never bump, but for safe functioning let's test
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            #print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.walk_stack.push((dx, dy))

            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy          

            # Check for victims
            seq = self.check_for_victim()
            if seq != VS.NO_VICTIM:
                vs = self.read_vital_signals()
                self.victims[vs[0]] = ((self.x, self.y), vs)
                print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
            # Calculates the difficulty of the visited cell
            # 1 = Linha reta
            # 1.5 = Diagonal
            difficulty = (rtime_bef - rtime_aft)
            print(f"Dificuldade: {difficulty}")
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
            #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")

            #Adicionou a coordenada ao mapa de pesos
            self.opt.add_coord((self.x, self.y), self.clock)

        return

    #Função de retorno
    def come_back(self):
        #Desempilha para voltar
        dx, dy = self.walk_stack.pop()
        dx = dx * -1
        dy = dy * -1

        result = self.walk(dx, dy)
        if result == VS.BUMPED:
            print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
            return
        
        if result == VS.EXECUTED:
            # update the agent's position relative to the origin
            self.x += dx
            self.y += dy
            #print(f"{self.NAME}: coming back at ({self.x}, {self.y}), rtime: {self.get_rtime()}")


    #Encontra o caminho ate a base
    def greedy_path_to_zero(self, map):
        cur_pos = (self.x, self.y)
        new_time = 0

        # Movimentos possíveis: (dx, dy)
        moves = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        path = [cur_pos]  # Caminho começando na posição inicial
        
        while map[cur_pos] != 0:
            next_pos = None
            min_weight = float('inf')
            
            for move in moves:
                candidate_pos = (cur_pos[0] + move[0], cur_pos[1] + move[1])
                
                # Se a posição candidata está no mapa e seu peso é menor que o menor peso encontrado até agora
                if candidate_pos in map and map[candidate_pos] < min_weight:
                    min_weight = map[candidate_pos]
                    next_pos = candidate_pos
            
            # Atualiza a posição atual para a posição com menor peso encontrada
            new_time += map[cur_pos] 
            curr_pos = next_pos
            path.append(curr_pos)


        return path, new_time

        
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        #Aumenta com o tempo
        consumed_time = self.TLIM - self.get_rtime()

        #consumed_time == self.clock

        #Se tempo esta na metade, calcula mapa e novo tempo
        #if(self.clock <= self.time_back):
        #    base_path, candidate_time = greedy_path_to_zero(self.opt.get_all)

        #    if(candidate_time > self.time_back):
        #        self.time_back = candidate_time

        #    else:
        #        #volta tudo

           


        #Enquanto ha tempo, continua
        if consumed_time < self.get_rtime():
            self.explore()
            return True

        # time to come back to the base
        if self.walk_stack.is_empty() or (self.x == 0 and self.y == 0):
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME}: rtime {self.get_rtime()}, invoking the rescuer")
            #input(f"{self.NAME}: type [ENTER] to proceed")
            self.resc.go_save_victims(self.map, self.victims)
            return False

        self.come_back()
        return True

