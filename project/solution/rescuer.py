##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim
### Not a complete version of DFS; it comes back prematuraly
### to the base when it enters into a dead end position

import os
import random
import numpy as np
from search import search
from map import Map
from vs.abstract_agent import AbstAgent
from vs.physical_agent import PhysAgent
from vs.constants import VS
from abc import ABC, abstractmethod
from genetic import evaluate_sequence, initialize_random, reproduce_pop, select_best, select_the_best, seq_list2dict

## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstAgent):
    def __init__(self, env, config_file, rescuer_id):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.map = Map()             # explorer will pass the map
        #self.model = xgb.XGBClassifier()  
        #self.model.load_model('/home/gaspad/prog/SistemasInteligentes/tar1/greedy/estimate/modelo_xgboost.json')
        self.env = env
        self.rescuer_id = rescuer_id
        self.start_x = self.env.dic["BASE"][0]
        self.start_y = self.env.dic["BASE"][1]
        self.count = 0
        self.victims = {}         # list of found victims
        self.plan = []              # a list of planned actions
        self.plan_x = self.env.dic["BASE"][0]             # the x position of the rescuer during the planning phase
        self.plan_y = self.env.dic["BASE"][1]             # the y position of the rescuer during the planning phase
        self.plan_visited = set()   # positions already planned to be visited 
        self.plan_rtime = self.TLIM # the remaing time during the planning phase
        self.plan_walk_time = 0.0   # previewed time to walk during rescue
        self.x = self.env.dic["BASE"][0]                  # the current x position of the rescuer when executing the plan
        self.y = self.env.dic["BASE"][1]                  # the current y position of the rescuer when executing the plan
        self.map_counter = 0        # Verificar quantos mapas o agente ja recebeu
                
        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.set_state(VS.IDLE)

    def load_map(self, map):
        print("Resgatador recebeu o mapa!")
        self.map = map

    def add_victims(self, victims):
        self.victims = victims
        # for victim in victims:
        #     seq, data = victim[0], victim[1:]
            
        #     print(f"seq: {seq}")
        #     print(f"data: {data}")
            # print(f"Vítima {seq}: Coordenadas {data[0]}, Severidade {data[1]}")

    def go_save_victims(self):
        """The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment"""

        print(f"\n\n*** R E S C U E R ***")
        # self.map = map
        # self.victims = victims

        # import json
        # print(json.dumps(self.victims, indent=4))

        self.__planner()
        i = 1
        self.plan_x = self.env.dic["BASE"][0]
        self.plan_y = self.env.dic["BASE"][1]
        for a in self.plan:
            self.plan_x += a[0]
            self.plan_y += a[1]
            i += 1

        print(f"{self.NAME} END OF PLAN")

        self.set_state(VS.ACTIVE)
    
    def __a_star(self):
        print(f"self.victims: {self.victims}")
        sorted_victims = sorted(self.victims, key=lambda x: x[2][-1])
        if len(sorted_victims) == 0:
            return

        population_size = 5
        population = initialize_random(self.victims, population_size)
        print("population_size: ", len(population))
        n_generations = 10
        scores = []
        for i in range(n_generations):
            scores.clear()
            print("generation ", i)
            for sequence in population:
                score = evaluate_sequence(
                    self.start_x,
                    self.start_y,
                    sequence,
                    self.victims,
                    self.map,
                    self.COST_LINE,
                    self.COST_DIAG,
                    self.TLIM,
                    self.COST_FIRST_AID,
                )
                scores.append((score, sequence))
            selected = select_best(scores)
            print("selected size: ", len(selected))
            children = reproduce_pop(selected)
            print("children size: ", len(children))
            population = selected + children
            print("population_size: ", len(population))
        best = select_the_best(
            self.start_x,
            self.start_y,
            population,
            self.victims,
            self.map,
            self.COST_LINE,
            self.COST_DIAG,
            self.TLIM,
            self.COST_FIRST_AID,
        )

        best = best[1]

        directory = "clusters_data/cluster"
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_name = os.path.join(directory, f"seq{self.rescuer_id}.txt")

        # Salvar a melhor sequência em um arquivo .txt
        with open(file_name, "w") as f:
            for victim_id in best:
                # Procurar a vítima na lista de self.victims
                victim_info = next((v for v in self.victims if v[0] == victim_id), None)
                
                if victim_info is not None:
                    x, y = victim_info[1]  # Coordenadas X e Y
                    severity_class = victim_info[2][-1]  # Classe de gravidade
                    # Escrever no arquivo no formato ID, X, Y, Classe de gravidade
                    f.write(f"{victim_id}, {x}, {y}, {severity_class}\n")
                else:
                    print(f"Erro: victim_id {victim_id} não encontrado em self.victims.")

        best = seq_list2dict(best, self.victims)
        current_pos = (self.env.dic["BASE"][0],self.env.dic["BASE"][1])
        for victim in best:
            next_plan, time_required = search(
                self.COST_LINE,
                self.COST_DIAG,
                self.map,
                current_pos,
                victim[1]
            )
            
            # print(f"victim: {victim}")
            # print(f"victim[0]: {victim[0]}")
            # print(f"victim[1]: {victim[1]}")
            # print(f"victim[2]: {victim[2]}")
            # exit()

            comeback_plan, time_to_go_back = search(
                self.COST_LINE, self.COST_DIAG, self.map, victim[1], (self.env.dic["BASE"][0],self.env.dic["BASE"][1])
            )
            time_required += self.COST_FIRST_AID
            if (
                self.plan_walk_time + time_required + time_to_go_back
                > self.plan_rtime - 40
            ):
                continue
            self.plan_walk_time += time_required
            self.plan = self.plan + next_plan
            current_pos = victim[1]

        comeback_plan, time_to_go_back = search(
            self.COST_LINE, self.COST_DIAG, self.map, current_pos, (self.env.dic["BASE"][0],self.env.dic["BASE"][1])
        )
        self.plan = self.plan + comeback_plan

        print(self.plan)
        return

    def __planner(self):
        """ A private method that calculates the walk actions in a OFF-LINE MANNER to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberata method"""

        """ This plan starts at origin (0,0) and chooses the first of the possible actions in a clockwise manner starting at 12h.
        Then, if the next position was visited by the explorer, the rescuer goes to there. Otherwise, it picks the following possible action.
        For each planned action, the agent calculates the time will be consumed. When time to come back to the base arrives,
        it reverses the plan."""

        # This is a off-line trajectory plan, each element of the list is a pair dx, dy that do the agent walk in the x-axis and/or y-axis.
        # Besides, it has a flag indicating that a first-aid kit must be delivered when the move is completed.
        # For instance (0,1,True) means the agent walk to (x+0,y+1) and after walking, it leaves the kit.

        self.plan_visited.add((self.env.dic["BASE"][0],self.env.dic["BASE"][1])) # always start from the base, so it is already visited
        self.__a_star()
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           #input(f"{self.NAME} has finished the plan [ENTER]")
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy, there_is_vict = self.plan.pop(0)
        #print(f"{self.NAME} pop dx: {dx} dy: {dy} vict: {there_is_vict}")

        # Walk - just one step per deliberation
        walked = self.walk(dx, dy)

        # Rescue the victim at the current position
        if walked == VS.EXECUTED:
            self.x += dx
            self.y += dy
            #print(f"{self.NAME} Walk ok - Rescuer at position ({self.x}, {self.y})")
            # check if there is a victim at the current position
            if there_is_vict:
                rescued = self.first_aid() # True when rescued
                if rescued:
                    print(f"{self.NAME} Victim rescued at ({self.x}, {self.y})")
                else:
                    print(f"{self.NAME} Plan fail - victim not found at ({self.x}, {self.x})")
        else:
            print(f"{self.NAME} Plan fail - walk error - agent at ({self.x}, {self.x})")
            
        #input(f"{self.NAME} remaining time: {self.get_rtime()} Tecle enter")

        return True

