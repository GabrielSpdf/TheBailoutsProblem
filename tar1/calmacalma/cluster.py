import os
import random as rd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

N_CLUSTER = 4
MAX_IT = 200
DPI = 100


def k_means(victims, clusters = N_CLUSTER, max_iter = MAX_IT):
    x_min, x_max, y_min, y_max = __get_limits(victims) 

    print(f"x_min: {x_min}, x_max: {x_max}")
    print(f"y_min: {y_min}, y_max: {y_max}")

    #Vetor dos centroides
    centroids = []

    #Para cada centroide um valor eh sorteado
    for _ in range(clusters):
        if x_max - 1 > x_min:
            cx = rd.randint(x_min, x_max - 1)
        else:
            cx = x_min  # ou trate o erro conforme necessário

        if y_max - 1 > y_min:
            cy = rd.randint(y_min, y_max - 1)
        else:
            cy = y_min  # ou trate o erro conforme necessário

        centroids.append([cx, cy, []])
    
    c_changed = True
    it = 0

    while it < max_iter and c_changed:
        c_changed = False

        #Limpa os vetores de cada centroide
        for c in centroids:
            c[2].clear()

        #Para cada individuo do dataset
        for id, data in victims.items():
            min_dist = -1
            closest = -1
            coord, _ = data

            #Calcula a distancia quadratica do individuo i para cada centroide
            for i, c in enumerate(centroids):
                c_dist = (c[0] - coord[0])**2 +  (c[1] - coord[1])**2

                #Se o centroid atual esta mais proximo, atribui
                if c_dist < min_dist or min_dist == -1:
                    min_dist = c_dist
                    closest = i
            
            #Adiciona individuo mais proximo ao vetor de centroides
            centroids[closest][2].append((id, coord))

        
        #Para cada centroide no vetor de centroides 
        for c in centroids:
            n = len(c[2])
            x, y = 0, 0

            #Coordenadas do centroide
            old_x, old_y = c[0], c[1]

            #Para cada individuo, somar as coordenadas
            for v in c[2]:
                x += v[1][0]
                y += v[1][1]
            
            #Se ainda ha individuos a serem analisados
            if n != 0:
                #Realiza a media da coordenadas
                c[0] = x/n
                c[1] = y/n

                #Se a coordenada do centroide mudou
                if c[0] != old_x or c[1] != old_y:
                    c_changed = True
            #Se nao ha mais individuo
            else:
                c[0] = rd.randint((-1)*int(x_min/2), int(x_max/2))
                c[1] = rd.randint((-1)*int(y_min/2), int(y_max/2))
            

        it = it + 1

    return centroids

def __get_limits(victims):
    x_max, x_min, y_max, y_min = None, None, None, None

    print(f"Vitimas: {victims}")

    #Para cada vitima
    for _id , data in victims.items():
        coord, _ = data

        x, y = coord

        #Se valores nao foram alterados
        if x_max == None or x_min == None:
            x_max = x;
            x_min = x;

        if y_max == None or y_min == None:
            y_max = y
            y_min = y
        
        #Encontrar maior x & y
        if x > x_max:
            x_max = x
        else:
            x_min = x

        if y > y_max:
            y_max = y
        else:
            y_min = y

    return x_min, x_max, y_min, y_max


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


def save_plot(clusters, grid_w, grid_h):
    # Define diferentes cores para os clusters
    colors = ['r', 'g', 'b', 'y', 'c', 'm', 'k']

    # Ajuste do tamanho da figura para corresponder à proporção da janela do Pygame
    fig_size_x = grid_w  
    fig_size_y = grid_h

    # Cria uma nova figura para o plot
    plt.figure(figsize=(fig_size_x, fig_size_y))

    plt.xlim(0, grid_w)
    plt.ylim(0, grid_h)

    plt.gca().invert_yaxis()

    plt.gca().set_aspect('equal', adjustable='box')

    # Itera sobre os clusters
    for i, cluster in enumerate(clusters):
        # Coleta todas as coordenadas x e y deste cluster
        x_coords = [victim[1][0] for victim in cluster[2]]
        y_coords = [victim[1][1] for victim in cluster[2]]

        # Plot os pontos do cluster com a cor correspondente
        plt.scatter(x_coords, y_coords, c=colors[i % len(colors)], label=f'Cluster {i}')

        # Plot o centróide do cluster
        plt.scatter(cluster[0], cluster[1], c=colors[i % len(colors)], marker='x', s=100, label=f'Centroide {i}')

    # Adiciona uma legenda para identificar cada cluster
    plt.legend()

    # Adiciona títulos para os eixos e para o plot
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.title('Visualização dos Clusters')

    directory = "clusters_data/"
    if not os.path.exists(directory):
        os.makedirs(directory)  # Cria o diretório se ele não existir
    file_name = os.path.join(directory, f"plot.png")

    # Salva a figura no caminho especificado
    plt.savefig(file_name, dpi=DPI)

    # Fecha a figura para liberar memória
    plt.close()

