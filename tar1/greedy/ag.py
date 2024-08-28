import random

# Exemplo de dados de vítimas (id, (x, y), severidade)
victims = {
    1: ([10, 10], 1),
    2: ([20, 30], 2),
    3: ([30, 40], 1),
    4: ([40, 20], 3),
    5: ([50, 50], 1)
}

centroid = [30, 30]  # Exemplo de coordenada do centróide do cluster

POP_SIZE = 20  # Tamanho da população
MUTATION_RATE = 0.1  # Taxa de mutação
GENERATIONS = 100  # Número de gerações

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

