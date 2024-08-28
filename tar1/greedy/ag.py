import random
import numpy as np


POP_SIZE = 20  # Tamanho da população
MUTATION_RATE = 0.1  # Taxa de mutação
GENERATIONS = 100  # Número de gerações

# setar vitimas
# setar centroide

def calculate_distance(coord1, coord2):
    """Calcula a distância euclidiana entre duas coordenadas."""
    return np.linalg.norm(np.array(coord1) - np.array(coord2))

def fitness(sequence, victims, centroid):
    """Calcula o fitness de uma sequência, priorizando vítimas mais graves."""
    total_distance = 0
    weighted_rescue = 0
    
    for i in range(len(sequence) - 1):
        victim_id = sequence[i]
        next_victim_id = sequence[i + 1]
        victim = victims[victim_id]
        next_victim = victims[next_victim_id]
        
        severity_weight = 6 if victim[1] == 1 else 3 if victim[1] == 2 else 2 if victim[1] == 3 else 1
        weighted_rescue += severity_weight
        
        total_distance += calculate_distance(victim[0], next_victim[0])
    
    # Adiciona a última vítima na contagem
    last_victim_id = sequence[-1]
    last_victim = victims[last_victim_id]
    severity_weight = 6 if last_victim[1] == 1 else 3 if last_victim[1] == 2 else 2 if last_victim[1] == 3 else 1
    weighted_rescue += severity_weight
    
    # Penaliza o fitness por grandes distâncias percorridas
    fitness_value = weighted_rescue / (1 + total_distance)
    
    return fitness_value

def create_individual(victim_ids):
    """Cria um novo indivíduo (sequência aleatória de resgate)."""
    individual = victim_ids[:]
    random.shuffle(individual)
    return individual

def select(population, fitnesses):
    """Seleciona dois indivíduos da população com base no fitness."""
    return random.choices(population, weights=fitnesses, k=2)

def crossover(parent1, parent2):
    """Realiza o crossover entre dois pais."""
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child1 = parent1[start:end] + [x for x in parent2 if x not in parent1[start:end]]
    child2 = parent2[start:end] + [x for x in parent1 if x not in parent2[start:end]]
    return child1, child2

def mutate(individual):
    """Realiza mutação em um indivíduo."""
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]  # Troca dois elementos
    return individual

# Inicializa a população
victim_ids = list(victims.keys())
population = [create_individual(victim_ids) for _ in range(POP_SIZE)]

# Executa o Algoritmo Genético
for generation in range(GENERATIONS):
    fitnesses = [fitness(individual, victims, centroid) for individual in population]
    
    # Melhor solução na geração atual
    best_individual = population[np.argmax(fitnesses)]
    best_fitness = max(fitnesses)
    print(f"Geração {generation}: Melhor Fitness = {best_fitness:.4f}, Sequência = {best_individual}")
    
    # Nova geração
    new_population = population[:2]  # Elitismo: mantém os dois melhores
    while len(new_population) < POP_SIZE:
        parent1, parent2 = select(population, fitnesses)
        child1, child2 = crossover(parent1, parent2)
        new_population.extend([mutate(child1), mutate(child2)])
    
    population = new_population

# Melhor sequência final
final_fitnesses = [fitness(individual, victims, centroid) for individual in population]
best_individual = population[np.argmax(final_fitnesses)]
print(f"Melhor sequência encontrada: {best_individual} com fitness {max(final_fitnesses):.4f}")
