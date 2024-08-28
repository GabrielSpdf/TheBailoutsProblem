import xgboost as xgb
import numpy as np
from bayes_opt import BayesianOptimization
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report

def load_data(filepath):
    data = np.loadtxt(filepath, delimiter=',')
    return data

def xgb_evaluate(max_depth, gamma, colsample_bytree, learning_rate, n_estimators, min_child_weight, subsample, reg_lambda, reg_alpha):
    params = {
        'max_depth': int(max_depth),
        'gamma': gamma,
        'colsample_bytree': colsample_bytree,
        'learning_rate': learning_rate,
        'n_estimators': int(n_estimators),
        'min_child_weight': int(min_child_weight),
        'subsample': subsample,
        'reg_lambda': reg_lambda,
        'reg_alpha': reg_alpha,
        'objective': 'multi:softmax',
        'num_class': 4
    }
    model = xgb.XGBClassifier(**params)
    cv_score = cross_val_score(model, X_train, y_train, cv=3, scoring='accuracy')
    return cv_score.mean()

data_train = load_data('4000vit.txt')
data_test = load_data('800vit.txt')

X_train = data_train[:, 3:6] # qPA, pulso, frequencia respiratoria
y_train = data_train[:, -1] - 1# classe de gravidade

X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2, random_state=42)

params = {
    'max_depth': (3, 10),
    'gamma': (0, 5),
    'colsample_bytree': (0.3, 0.9),
    'learning_rate': (0.01, 0.3),
    'n_estimators': (50, 200),
    'min_child_weight': (1, 10),    
    'subsample': (0.5, 1.0),
    'reg_lambda': (0, 10),
    'reg_alpha': (0, 10)
}

# Otimização Bayesiana
optimizer = BayesianOptimization(f=xgb_evaluate, pbounds=params, random_state=42, verbose=2)
optimizer.maximize(init_points=25, n_iter=100)

# Melhores parâmetros
best_params = optimizer.max['params']
print(f"Melhores parâmetros: {best_params}")

# Ajuste os tipos de parâmetros conforme necessário
best_params['max_depth'] = int(best_params['max_depth'])
best_params['n_estimators'] = int(best_params['n_estimators'])

# Treinando o modelo final com os melhores parâmetros
model = xgb.XGBClassifier(**best_params)
model.fit(X_train, y_train)

# Validacao
val_predictions = model.predict(X_val)
print("Validação (com 4.000 vítimas):")
print(classification_report(y_val, val_predictions))

# Teste
X_test = data_test[:, 3:6]
y_test = data_test[:, -1] - 1

test_predictions = model.predict(X_test)
print("Teste (com 800 vítimas):")
print(classification_report(y_test, test_predictions))

# Salvamento do modelo
model.save_model('modelo_xgboost.json')
print("Modelo salvo com sucesso!")
