import sys
import os
import time

## importa classes
from vs.environment import Env
from explorer import Explorer
from rescuer import Rescuer

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
    resc1 = Rescuer(env, rescuer_file)
    resc2 = Rescuer(env, rescuer_file)
    resc3 = Rescuer(env, rescuer_file)
    resc4 = Rescuer(env, rescuer_file)

    # Explorer needs to know rescuer to send the map
    # that's why rescuer is instatiated before
    v1 = [2, 1, 0, 7, 6, 5, 4, 3]
    v2 = [2, 3, 4, 5, 6, 7, 0, 1]
    v3 = [6, 7, 0, 1, 2, 3, 4, 5]
    v4 = [6, 5, 4, 3, 2, 1, 0, 7]

    # exp1 = Explorer(env, explorer_file, resc1, v1)
    exp2 = Explorer(env, explorer_file, resc2, v2)
    # exp3 = Explorer(env, explorer_file, resc3, v3)
    # exp4 = Explorer(env, explorer_file, resc4, v4)

    # Run the environment simulator
    env.run()
    
        
if __name__ == '__main__':
    """ To get data from a different folder than the default called data
    pass it by the argument line"""
    
    if len(sys.argv) > 1:
        data_folder_name = sys.argv[1]
    else:
        data_folder_name = os.path.join("datasets", "data_10v_12x12")
        
    main(data_folder_name)