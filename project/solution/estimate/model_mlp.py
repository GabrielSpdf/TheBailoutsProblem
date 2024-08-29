from sklearn.preprocessing import StandardScaler
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neural_network import MLPClassifier
from bayes_opt import BayesianOptimization

def load_data(filepath):
    data = np.loadtxt(filepath, delimiter=',')
    return data

# Mapeamento das funções de ativação e solvers para índices
activation_map = {0: 'logistic', 1: 'tanh', 2: 'relu'}
solver_map = {0: 'lbfgs', 1: 'sgd', 2: 'adam'}

def mlp_evaluate(hidden_layer_sizes, activation, solver, alpha, learning_rate_init):
    # Converter os índices de volta para strings usando os mapas
    activation = activation_map[int(activation)]
    solver = solver_map[int(solver)]
    
    params = {
        'hidden_layer_sizes': tuple([int(hidden_layer_sizes)]),
        'activation': activation,
        'solver': solver,
        'alpha': alpha,
        'learning_rate_init': learning_rate_init,
        'max_iter': 1000,
        'random_state': 42
    }
    model = MLPClassifier(**params)
    
    # Aplicando o scaler aos dados de treinamento
    X_train_scaled = scaler.fit_transform(X_train)
    
    cv_score = cross_val_score(model, X_train_scaled, y_train, cv=3, scoring='accuracy')
    return cv_score.mean()

# Carregar os dados de treinamento e teste
data_train = load_data('4000vit.txt')
data_test = load_data('800vit.txt')

# Dividindo as features e os rótulos para treinamento e teste
X_train = data_train[:, 3:6]  # qPA, pulso, frequencia respiratoria
y_train = data_train[:, -1] - 1  # classe de gravidade

X_test = data_test[:, 3:6]  # qPA, pulso, frequencia respiratoria
y_test = data_test[:, -1] - 1  # classe de gravidade

# Dividindo os dados de treinamento em treinamento e validação
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

# Inicializar o scaler
scaler = StandardScaler()

# Ajuste o scaler ao conjunto de treinamento e transforme o conjunto de validação e teste
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

# Definir os parâmetros para a otimização bayesiana
params = {
    'hidden_layer_sizes': (10, 100),  # Número de neurônios na camada oculta
    'activation': (0, 2),  # Índices de funções de ativação
    'solver': (0, 2),  # Índices dos solvers
    'alpha': (0.0001, 0.1),  # Regularização L2
    'learning_rate_init': (0.001, 0.1)  # Taxa de aprendizado
}

# Otimização Bayesiana
optimizer = BayesianOptimization(f=mlp_evaluate, pbounds=params, random_state=42, verbose=2)
optimizer.maximize(init_points=25, n_iter=100)

# Melhores parâmetros
best_params = optimizer.max['params']
print(f"Melhores parâmetros: {best_params}")

# Ajustar os parâmetros categóricos e transformar os dados de acordo
best_params['hidden_layer_sizes'] = tuple([int(best_params['hidden_layer_sizes'])])
best_params['activation'] = activation_map[int(best_params['activation'])]
best_params['solver'] = solver_map[int(best_params['solver'])]

# Treinar o modelo final com os melhores parâmetros
model = MLPClassifier(**best_params, max_iter=1000, random_state=42)
model.fit(X_train_scaled, y_train)

# Validação
val_predictions = model.predict(X_val_scaled)
print("Validação (com 4.000 vítimas):")
print(classification_report(y_val, val_predictions))

# Teste
test_predictions = model.predict(X_test_scaled)
print("Teste (com 800 vítimas):")
print(classification_report(y_test, test_predictions))

# Salvamento do modelo (opcional, dependendo do formato desejado)
import joblib
joblib.dump(model, 'modelo_mlp.pkl')
print("Modelo salvo com sucesso!")

