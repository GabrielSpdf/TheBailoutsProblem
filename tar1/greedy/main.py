import sys
import os
import time

## importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer
from manager import Manager

def main(data_folder_name):
   
    # Set the path to config files and data files for the environment
    current_folder = os.path.abspath(os.getcwd())
    data_folder = os.path.abspath(os.path.join(current_folder, data_folder_name))

    
    # Instantiate the environment
    env = Env(data_folder)
    
    # config files for the agents
    rescuer_file = os.path.join(data_folder, "rescuer_config.txt")
    explorer_file = os.path.join(data_folder, "explorer_config.txt")
    
    # Instantiate agents rescuer and explorer
    resc1 = Rescuer(env, rescuer_file, 1)
    resc2 = Rescuer(env, rescuer_file, 2)
    resc3 = Rescuer(env, rescuer_file, 3)
    resc4 = Rescuer(env, rescuer_file, 4)

    man = Manager(resc1, resc2, resc3, resc4)

    #Vetor de prioridade de movimentos
    v1 = [2, 1, 0, 7, 6, 5, 4, 3]
    v2 = [2, 3, 4, 5, 6, 7, 0, 1]
    v3 = [6, 7, 0, 1, 2, 3, 4, 5]
    v4 = [6, 5, 4, 3, 2, 1, 0, 7]

    exp1 = Explorer(env, explorer_file, man, v1)
    exp2 = Explorer(env, explorer_file, man, v2)
    exp3 = Explorer(env, explorer_file, man, v3)
    exp4 = Explorer(env, explorer_file, man, v4)

    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
                    data_folder_name = os.path.join("datasets", "data_300v_90x90")
        
    main(data_folder_name)
