from vs.constants import VS

class Opt:
    #Inicia lista
    def __init__(self):
        self.opt_data = {}

    #Se verficia se existe a coordenada
    def ver_coord(self, coord):
        if coord in self.opt_data:
            return True

        return False

    #Retorna o mapa
    def get_map(self, coord):
        return self.opt_data.get(coord)

    def get_all(self):
        return self.opt_data

    #Adiciona coordenada e o peso da posicao
    def add_coord(self, coord, visit_n):
        self.opt_data[coord] = visit_n



    
