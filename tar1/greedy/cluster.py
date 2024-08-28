import os
import random as rd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.use('Agg')

N_CLUSTER = 4
MAX_IT = 200
DPI = 100

def k_means_pp(victims, clusters = N_CLUSTER, max_iter = MAX_IT, tolerance=0.0001):
    # Inicializacao dos centroides
    centroids = []
    victim_coords = [data[0] for data in victims.values()] 

    # Escolhe o primeiro centroide aleatoriamente
    first_centroid = victim_coords[rd.randint(0, len(victim_coords) - 1)]
    centroids.append([first_centroid[0], first_centroid[1], []])

    # Escolhe os proximos centroides com base em K-means++
    for _ in range(1, clusters):
        distances = []
        
        # Para cada ponto, calcula a distancia ao centroide mais proximo
        for coord in victim_coords:
            min_dist = min((coord[0] - c[0])**2 + (coord[1] - c[1])**2 for c in centroids)
            distances.append(min_dist)

        # Seleciona o proximo centroide com probabilidade proporcional a distancia
        distances = np.array(distances)
        probabilities = distances / distances.sum()
        next_centroid_idx = np.random.choice(range(len(victim_coords)), p=probabilities)
        next_centroid = victim_coords[next_centroid_idx]

        centroids.append([next_centroid[0], next_centroid[1], []])
    
    # Continuacao K-means...
    c_changed = True
    it = 0

    while it < max_iter and c_changed:
        c_changed = False

        # Limpa os vetores de cada centroide
        for c in centroids:
            c[2].clear()

        # Para cada vitima
        for id, data in victims.items():
            min_dist = float("inf")
            closest = -1
            coord, severity = data

            # Calcula a distancia quadratica para cada centroide
            for i, c in enumerate(centroids):
                c_dist = (c[0] - coord[0])**2 +  (c[1] - coord[1])**2

                # Atribui o centroide mais proximo
                if c_dist < min_dist:
                    min_dist = c_dist
                    closest = i
            
            # Adiciona a vitima ao vetor do centroide mais proximo
            centroids[closest][2].append((id, coord, severity))

        
        # Recalcula os centroides
        for c in centroids:
            weighted_x, weighted_y = 0, 0
            total_weight = 0

            for _, (x, y), severity in c[2]:
                weight = 0
                if severity == 1:
                    weight = 6
                elif severity == 2:
                    weight = 3
                elif severity == 3:
                    weight = 2
                elif severity == 4:
                    weight = 1

                weighted_x += x * weight
                weighted_y += y * weight
                total_weight += weight

            if total_weight != 0:
                new_x = weighted_x / total_weight
                new_y = weighted_y / total_weight
            else:
                new_x, new_y = c[0], c[1]

            if abs(new_x - c[0]) > tolerance or abs(new_y - c[1]) > tolerance:
                c_changed = True

            c[0], c[1] = new_x, new_y

        it += 1

    return centroids

######################################################

#######################################################

def save_clusters(clusters):
    #Para cluster
    for i, cluster in enumerate(clusters):
        # Cria o nome do arquivo
        directory = "clusters_data/cluster"
        if not os.path.exists(directory):
            os.makedirs(directory)  # Cria o diretório se ele não existir
        file_name = os.path.join(directory, f"cluster{i}.txt")
        
        # Inicializa o conteúdo do arquivo
        contents = f"{cluster[0]},{cluster[1]}\n"
        
        # Adiciona informações de cada 'vítima' ao conteúdo do arquivo
        for victim in cluster[2]:
            id = victim[0]
            x = victim[1][0]
            y = victim[1][1]
            contents += f"{id},{x},{y},0.0,1\n"
        
        # Escreve o conteúdo no arquivo
        with open(file_name, 'w') as file:
            file.write(contents)

##########################################################

def save_plot(centroids, filename='cluster_plot.png', dpi=100):
    # Diretório onde o plot será salvo
    save_dir = 'clusters_data/'
    
    # Cria o diretório se ele não existir
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Cores para os clusters
    colors = ['blue', 'green', 'purple', 'orange']  # Adicione mais cores se necessário

    # Inicia o plot
    plt.figure(dpi=dpi)

    # Plotar os clusters
    for idx, centroid in enumerate(centroids):
        cluster_victims = centroid[2]  # As vítimas pertencentes ao cluster
        cluster_coords = np.array([v[1] for v in cluster_victims])

        if cluster_coords.size > 0:  # Verifica se o cluster não está vazio
            plt.scatter(cluster_coords[:, 0], cluster_coords[:, 1], color=colors[idx % len(colors)], label=f'Cluster {idx + 1}')

        # Plotar os centroides
        plt.scatter(centroid[0], centroid[1], color='red', marker='X', s=200, edgecolor='black')

    # Configurações do plot
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Visualização dos Clusters')
    plt.legend()

    # Caminho completo para salvar a imagem
    save_path = os.path.join(save_dir, filename)
    
    # Salvar o plot
    plt.savefig(save_path)
    plt.close()

    print(f"Plot salvo em: {save_path}")
