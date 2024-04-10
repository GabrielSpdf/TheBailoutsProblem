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
from timepos import TimePos

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
        self.change = 0
        self.count = 0
        self.mothers_call = 0
        self.home_path = []
        self.plan_visited = set()
        self.map = Map()           # create a map for representing the environment
        self.opt = Opt() 
        self.time_pos = TimePos()
        self.time_back = (self.TLIM/2)
        self.vector = vec
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
        self.opt.add_coord((self.x, self.y), 0)
        self.time_pos.add_time((self.x, self.y), 0)

    #Funcao para voltar para a base
    def back_home(self, path):
        #Vai ate a base
        i = 0
        while((self.x, self.y)!=(0, 0)):
            (dx, dy) = path[i]
            result = self.walk(dx, dy)

            if result == VS.BUMPED:
                print("Voltando base, bateu a cabeca!")
                # print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
                return
            
            if result == VS.EXECUTED:
                # update the agent's position relative to the origin
                self.x += dx
                self.y += dy

            i = i + 1
        print("Voltando devido ao tempo...")



    #Busca proxima posicao
    def get_next_position(self, vec):
        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()

        for i in range(8):
            time.sleep(0.001)

            #Vetor de prioridade
            # print(f"Direção: {vec[i]}")
            direction = vec[i]

            prox_x, prox_y = Explorer.AC_INCR[direction]
            # print(f"self.x: {self.x}")
            # print(f"self.y: {self.y}")

            # print(f"prox_x: {prox_x}")
            # print(f"prox_y: {prox_y}")
            target_xy = (self.x + prox_x, self.y + prox_y)
            # print(f"target_xy: {target_xy}")

            if self.opt.ver_coord(target_xy):
                # print("Ja visitado 1")
                # print(1)
                continue

            #Check if pos was already visited
            if (target_xy in self.plan_visited):
                # print("Ja visitado 2")
                continue
            
            #Check if pos is valid
            if obstacles[direction] == VS.CLEAR:
                self.plan_x = self.x
                self.plan_y = self.y

                self.plan_x += prox_x
                self.plan_y += prox_y

                #Pos added to set
                self.plan_visited.add((self.plan_x, self.plan_y))
                
                # print("Andou")
                # if(dx != 0 and dy != 0):
                #     self.clock = self.clock + 1.5
                #     self.time_back = self.time_back + 1.5
                # else:
                #     self.clock = self.clock + 1
                #     self.time_back = self.time_back + 1

                # print("Mapa: ")
                # print(self.opt.get_all())
                return Explorer.AC_INCR[direction]
   
        # print(f"self.x: {self.x} & self.y: {self.y}")
        #If agent hasnt possible movements
        if(self.x != 0 or self.y != 0):
            # print("retornou -2 -2")
            return -2, -2
        else: 
            return 0, 0

    #Encontra o melhor caminho ate a base
    def greedy_path_to_zero(self, mapa):
        time_map = self.time_pos.get_all_time_map()
        cur_pos = (self.x, self.y)
        new_time = 0

        # Movimentos possíveis: (dx, dy)
        moves = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        path = []
        
        while mapa[cur_pos] != 0:
            # print("Looping...")
            next_pos = None
            best_move = None
            min_weight = float('inf')
            # print(f"Posicao atual: {mapa[cur_pos]}")
            
            for move in moves:
                candidate_pos = (cur_pos[0] + move[0], cur_pos[1] + move[1])
                
                # Se a posição candidata está no mapa e seu peso é menor que o menor peso encontrado até agora
                # print("Verifica se esta no mapa")
                if candidate_pos in mapa and mapa[candidate_pos] < min_weight:
                    # print("Esta no mapa")
                    min_weight = mapa[candidate_pos]
                    next_pos = candidate_pos
                    best_move = move
            
            # Atualiza a posição atual para a posição com menor peso encontrada
            # print(time_map[next_pos])
            new_time = new_time + time_map[next_pos]
            print(f"new_time: {new_time}")

            cur_pos = next_pos
            path.append(best_move)
        
        #Transforma vetor numa pilha
        path = path[::-1]
        return path, new_time



    #Explorador 
    def explore(self):
        print(f"Tempo para voltar: {self.time_back}")
        dx, dy = self.get_next_position(self.vector)

        #Ficou sem movimento
        if((dx, dy) == (-2, -2)):
            self.change = 1
            print("Ficou sem movimento")
            self.home_path, self.time_back = self.greedy_path_to_zero(self.opt.get_all())

            #Verifica tempo
            print(f"NEW self.time_back: {self.time_back}")
    
            #Pega melhor movimento para base
            dx, dy = self.home_path.pop() # pylint: disable=unbalanced-tuple-unpacking
            print("Voltando 1 posicao em direcao a base")

            rtime_bef = self.get_rtime()
            result = self.walk(dx, dy)
            rtime_aft = self.get_rtime()

            #time_remix eh um valor negativo
            time_remix = rtime_aft - rtime_bef
            
            self.clock = self.clock - time_remix
            if(self.change == 1):
                self.time_back = self.time_back - time_remix

            print(f"Tempo que levou: {rtime_aft - rtime_bef}")

            if result == VS.BUMPED:
                self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
                # print(f"{self.NAME}: when coming back bumped at ({self.x+dx}, {self.y+dy}) , rtime: {self.get_rtime()}")
                # return
            
            if result == VS.EXECUTED:
                # update the agent's position relative to the origin
                self.x += dx
                self.y += dy

                self.home_path.append((dx, dy))


                # Check for victims
                seq = self.check_for_victim()
                if seq != VS.NO_VICTIM:
                    vs = self.read_vital_signals()
                    self.victims[vs[0]] = ((self.x, self.y), vs)
                    print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                    #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
                
                # Calculates the difficulty of the visited cell
                difficulty = (rtime_bef - rtime_aft)
                if dx == 0 or dy == 0:
                    difficulty = difficulty / self.COST_LINE
                else:
                    difficulty = difficulty / self.COST_DIAG

                # Update the map with the new cell
                self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())
                #print(f"{self.NAME}:at ({self.x}, {self.y}), diffic: {difficulty:.2f} vict: {seq} rtime: {self.get_rtime()}")V
            
            return


        # Moves the body to another position
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        #time_remix eh um valor negativo
        time_remix = rtime_aft - rtime_bef
        
        self.clock = self.clock - time_remix
        if(self.change == 1):
            self.time_back = self.time_back - time_remix

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
            # self.walk_stack.push((dx, dy))
            self.x += dx
            self.y += dy          

            self.home_path.append((dx, dy))


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
            # print(f"Dificuldade: {difficulty}")
            if dx == 0 or dy == 0:
                difficulty = difficulty / self.COST_LINE
            else:
                difficulty = difficulty / self.COST_DIAG

            # Update the map with the new cell
            self.map.add((self.x, self.y), difficulty, seq, self.check_walls_and_lim())

            #Adicionou a coordenada ao mapa de pesos
            if not self.opt.ver_coord((self.x, self.y)):
                self.opt.add_coord((self.x, self.y), self.clock)
                self.time_pos.add_time((self.x, self.y), -time_remix)

        return

    
    #"Funcao main"
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        #Aumenta com o tempo
        # consumed_time = self.TLIM - self.get_rtime()
        print(f"Tempo restante: {self.get_rtime()}")

        #Caso o tempo do explorador ultrapasse o tempo limite
        # print(f"self.get_rtime: {self.get_rtime()}")
        if(self.mothers_call == 0):
            #Se tempo esgotou
            if(self.get_rtime()+10 <= self.time_back):
                self.change = 1
                print("Tempo excedeu")
                self.home_path, candidate_time = self.greedy_path_to_zero(self.opt.get_all())

                self.time_back = candidate_time
                print(f"NEW self.time_back: {self.time_back}")
        
                #Volta base
                if(self.get_rtime()+10 <= self.time_back):   
                    self.mothers_call = 1
                    print("Voltando para base")
            else:
                if(self.x == 0 and self.y == 0):
                    self.count = self.count + 1

                if(self.count < 2):
                    # print("Foi viajar")
                    self.explore()
                    return True
                else:
                    self.mothers_call = 1
                    print("Voltando para base")
        else:
            if(self.x == 0 and self.y == 0):
                print("Voltou a base com sucesso!")
                print(f"Voltou a base restando: {self.get_rtime()}")
                print(f"O tempo de volta era: {self.time_back}")
                print("Resgatem!")
                self.resc.go_save_victims(self.map, self.victims)
                return False

            (dx, dy) = self.home_path.pop()
            result = self.walk(dx, dy)

            if(result == VS.BUMPED):
                print("Tropecou voltando para base...")
                return

            if(result == VS.EXECUTED):
                self.x += dx
                self.y += dy


        if(self.x == 0 and self.y == 0 and self.count >= 2):
            print("Voltou a base com sucesso!")
            print(f"Voltou a base restando: {self.get_rtime()}")
            print(f"O tempo de volta era: {self.time_back}")
            print("Resgatem!")
            self.resc.go_save_victims(self.map, self.victims)
            return False

        return True
