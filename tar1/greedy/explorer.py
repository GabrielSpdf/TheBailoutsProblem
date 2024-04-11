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
        self.env = env             # obter dados do mapa
        self.plan_x = 0            # variavel auxiliar para calculo de x
        self.plan_y = 0            # variavel auxiliar para calculo de y
        self.count = 0             # contador para verificar se chegou na base          
        self.index = 0             # indexador do mapa de heuristica
        self.mothers_call = 0      # chamada para voltar para base
        self.vv = []               # vetor de vitimas
        self.home_path = []        # caminho para base
        self.basex = 0             # posicao da base x
        self.basey = 0             # posicao da base y
        self.map = Map()           # create a map for representing the environment
        self.opt = Opt()           # inicializar mapa de heuristica
        self.time_back = 0         # tempo para voltar para base
        self.vector = vec          # vetor contendo a prioridade de movimentos do agente  
        self.victims = {}          # a dictionary of found victims: (seq): ((x,y), [<vs>])
                                   # the key is the seq number of the victim,(x,y) the position, <vs> the list of vital signals

        # put the current position - the base - in the map
        self.map.add((self.x, self.y), 1, VS.NO_VICTIM, self.check_walls_and_lim())
        self.opt.add_coord((self.x, self.y), self.index)


    #Busca proxima posicao
    def get_next_position(self, vec):
        # Check the neighborhood walls and grid limits
        obstacles = self.check_walls_and_lim()

        for i in range(8):
            #Vetor de prioridade
            direction = vec[i]

            #Atribui movimentos
            prox_x, prox_y = Explorer.AC_INCR[direction]

            #Qual sera a proxima posicao
            target_xy = (self.x + prox_x, self.y + prox_y)

            #Se ja foi visitado, continua
            if self.opt.ver_coord(target_xy):
                continue

            #Check if pos is valid
            if obstacles[direction] == VS.CLEAR:
                self.plan_x = self.x
                self.plan_y = self.y

                self.plan_x += prox_x
                self.plan_y += prox_y


                # time.sleep(0.2)
                return Explorer.AC_INCR[direction]
   

        #Nao encontrou movimentos
        if(self.x != 0 or self.y != 0):
            return -2, -2
        else: 
            return 0, 0

    #Encontra o melhor caminho ate a base
    def greedy_path_to_zero(self, map_index):
        cur_pos = (self.x, self.y)
        new_time = 0

        # Movimentos possíveis: (dx, dy)
        moves = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        path = []
        
        while map_index[cur_pos] != 0:
            # print("Looping...")
            next_pos = None
            best_move = None
            min_index = float('inf')

            for move in moves:
                new_x = cur_pos[0] + move[0]
                new_y = cur_pos[1] + move[1]
                candidate_pos = (new_x, new_y)
                
                # Se a posição candidata está no mapa e seu peso é menor que o menor peso encontrado até agora
                if candidate_pos in self.opt.opt_data and map_index[candidate_pos] < min_index:
                    # print("Esta no mapa")
                    if move[0] != 0 and move[1] != 0:   # diagonal
                        base = 1.5
                    else:                     # walk vertical or horizontal
                        base = 1
                    min_index = map_index[candidate_pos]
                    next_pos = candidate_pos
                    best_move = move
                    pospos_x = cur_pos[0]
                    pospos_y = cur_pos[1]
            
            new_x = next_pos[0]
            new_y = next_pos[1]

            if (new_x < self.env.dic["GRID_WIDTH"]and
                new_y < self.env.dic["GRID_HEIGHT"] and
                self.env.obst[new_x][new_y] != 100):
                plus = base * self.env.obst[new_x][new_y]
            else:
                plus = base

            # print(f"move: {best_move}")
            # print(f"tempo gasto: {plus}")


            # Atualiza a posição atual para a posição com menor peso encontrada
            new_time = new_time + plus
            cur_pos = next_pos
            path.append(best_move)
        
        #Transforma vetor numa pilha
        path = path[::-1]
        return path, new_time

    #Explorador 
    def explore(self):
        # print(f"Tempo para voltar: {self.time_back}")
        dx, dy = self.get_next_position(self.vector)

        #Ficou sem movimento
        if((dx, dy) == (-2, -2)):
            # print("Ficou sem movimento")

            #Volta 1 posicao para base
            dx, dy = self.home_path.pop() # pylint: disable=unbalanced-tuple-unpacking

            # time.sleep(0.001)
            #Calcula quanto tempo levou para esse movimento
            rtime_bef = self.get_rtime()
            result = self.walk(dx, dy)
            rtime_aft = self.get_rtime()


            self.time_back = self.time_back - (rtime_bef - rtime_aft)

            # print(f"Voltou 1 posicao em direcao a base")
            
            #Se posicao eh ok, volta
            if result == VS.EXECUTED:
                self.x += dx
                self.y += dy
            else: 
                print("Nao ok")

            
            return

        
        #Se o agente tem movimento

        #Calcula quanto tempo levou para esse movimento
        rtime_bef = self.get_rtime()
        result = self.walk(dx, dy)
        rtime_aft = self.get_rtime()

        #@returns -1 = the agent bumped into a wall or reached the end of grid
        #@returns -2 = the agent has no enough time to execute the action
        #@returns 1 = the action is succesfully executed
        
        if result == VS.BUMPED:
            # update the map with the wall
            self.map.add((self.x + dx, self.y + dy), VS.OBST_WALL, VS.NO_VICTIM, self.check_walls_and_lim())
            #print(f"{self.NAME}: Wall or grid limit reached at ({self.x + dx}, {self.y + dy})")

        if result == VS.EXECUTED:
            self.x += dx
            self.y += dy          

            aux_x = self.x
            aux_y = self.y

            #dx, dy eh o movimento que voce fez para avancar
            #para voltar vc tem que dar append no movimento contrario
            # print(f"Append em: {-dx} e {-dy}")
            self.home_path.append((-dx, -dy))

            #Para voltar, voce nao precisa escanear novamente
            if -dx != 0 and -dy != 0:   # diagonal
                base = 1.5
            else:                     # walk vertical or horizontal
                base = 1

            #Volta
            new_x = aux_x - dx
            new_y = aux_y - dy

            # print(f"new_x: {new_x}")
            # print(f"new_y: {new_y}")

            if (new_x < self.env.dic["GRID_WIDTH"]and
                new_y < self.env.dic["GRID_HEIGHT"] and
                self.env.obst[new_x][new_y] != 100):
                plus = base * self.env.obst[new_x][new_y]
            else:
                plus = base
            
            # print(f"plus: {plus}")
            self.time_back = self.time_back + plus

            #Se coordenada nao esta no mapa de vitimas
            if ((self.x, self.y) not in self.vv):
                seq = self.check_for_victim()

                #Se encontrou uma vitima na coordenada
                if(seq != VS.NO_VICTIM):
                    #Atualiza 
                    self.vv.append((self.x, self.y))

                    #Gasta tempo para diagnosticar
                    vs = self.read_vital_signals()
                    self.victims[vs[0]] = ((self.x, self.y), vs)
                    print(f"{self.NAME} Victim found at ({self.x}, {self.y}), rtime: {self.get_rtime()}")
                    #print(f"{self.NAME} Seq: {seq} Vital signals: {vs}")
            
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
                # print(f"result: {result}")
                self.index = self.index + 1
                self.opt.add_coord((self.x, self.y), self.index)

        return

    
    #"Funcao main"
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        # print(f"pos: {self.x} && {self.y}")

        #Aumenta com o tempo
        # consumed_time = self.TLIM - self.get_rtime()

        # print(f"Tempo de volta: {self.time_back}")

        # print(f"time_back: {self.time_back}")
        #Se nao precisa voltar para base
        if(self.mothers_call == 0):
            #Se tempo esgotou
            if(self.get_rtime()-25 <= self.time_back):
                print("Tempo excedeu")

                #Calcula uma possivel rota melhor
                candidate_path, candidate_time = self.greedy_path_to_zero(self.opt.get_all())
                print(f"Novo tempo candidato para voltar: {candidate_time}")
                
                #Se a rota calculada eh melhor, continua
                if(candidate_time <= self.time_back and candidate_time <= self.get_rtime()-25):
                    print("Caminho novo eh melhor")
                    self.time_back = candidate_time
                    self.home_path = candidate_path

                #Se a rota calculada eh pior do que atual, volta
                else:
                    self.mothers_call = 1
                    print(f"Tempo restante: {self.get_rtime()}")
                    print(f"Tempo que agente vai levar: {self.time_back}")
                    print("Voltando para base devido ao tempo")

            
            #Se ainda ha tempo
            else:
                #Se esta na base 
                if(self.x == self.basex and self.y == self.basey):
                    self.count = self.count + 1
                
                #Se nao eh a segunda vez na base
                if(self.count < 2):
                    self.explore()
                    return True

                #Chegou na base
                else:
                    self.mothers_call = 1
                    print("Chegou na base")

        #Se precisa voltar para base
        else:
            #Se chegou na base
            if(self.x == self.basex and self.y == self.basey):
                print("Voltou a base com sucesso!")
                print(f"Voltou a base restando: {self.get_rtime()}")
                print(f"O tempo de volta restante era: {self.time_back}")
                print(f"{self.NAME}: rtime {self.get_rtime()}")
                print("Resgatem!")
                print(f"VICTIMS: {self.victims}")

                self.resc.add_victims(self.victims)
                self.resc.full_join_maps(self.map)

                return False

            #Faz o caminho de volta para base

            # print(f"selfx e selfxy: {self.x} && {self.y}")
            # print(f"time_back: {self.time_back}")
            # print(f"remaining_time: {self.get_rtime()}")
            
            # print(f"pos: {self.x} && {self.y}")
            
            if(self.x != self.basex or self.y != self.basey):
                (dx, dy) = self.home_path.pop()
                # print(f"Movimento tomado: {dx} e {dy}")
                # print(f"PILHA: {self.home_path}")

                rtime_bef = self.get_rtime()
                result = self.walk(dx, dy)
                rtime_aft = self.get_rtime()
                # time.sleep(0.001)

                #Desconta o tempo andado
                
                # print(f"Tempo gasto: {rtime_bef - rtime_aft}")
                self.time_back = self.time_back - (rtime_bef - rtime_aft)

                if(result == VS.BUMPED):
                    print("Tropecou voltando para base...")
                    return

                #Se o movimento eh valido, atualiza
                if(result == VS.EXECUTED):
                    self.x += dx
                    self.y += dy

        #Se chegou na base
        if(self.x == self.basex and self.y == self.basey and self.count >= 2):
            print("Voltou a base com sucesso!")
            print(f"Voltou a base restando: {self.get_rtime()}")
            print(f"O tempo de volta era: {self.time_back}")

            print(f"{self.NAME}: rtime {self.get_rtime()}")
            print("Resgatem!")
            print(f"VICTIMS: {self.victims}")

            self.resc.add_victims(self.victims)
            self.resc.full_join_maps(self.map)
            # self.resc.go_save_victims(self.map, self.victims)
            return False

        return True
