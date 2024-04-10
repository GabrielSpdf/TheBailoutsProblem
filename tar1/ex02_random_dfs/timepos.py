from vs.constants import VS

class TimePos:
    #Inicia lista
    def __init__(self):
        self.time_pos = {}

    #Se verficia se existe a coordenada
    def ver_coord(self, coord):
        if coord in self.time_pos:
            return True

        return False

    #Retorna o mapa
    def get_map(self, coord):
        return self.time_pos.get(coord)

    def get_all_time_map(self):
        return self.time_pos

    def add_time(self, coord, time):
        self.time_pos[coord] = time


    
