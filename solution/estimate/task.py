import joblib
import xgboost as xgb
import numpy as np
from sklearn.metrics import classification_report


filepath = "/home/gaspad/prog/SistemasInteligentes/project/solution/datasets/data_408v_94x94"

signals_path = filepath + '/env_vital_signals_cego.txt'
target_path = filepath + '/target.txt'

signals = np.loadtxt(signals_path, delimiter=',')
target = np.loadtxt(target_path, delimiter=',')
    
# model = joblib.load('/home/gaspad/prog/SistemasInteligentes/project/solution/estimate/modelo_mlp.pkl')

model = xgb.XGBClassifier()  
model.load_model('/home/gaspad/prog/SistemasInteligentes/project/solution/estimate/modelo_xgboost.json')


X_test = signals[:, 3:6]
y_test = target[:, -1]

predictions = model.predict(X_test)

predictions = predictions + 1

for i in range(len(y_test)):
    print(f"Esperado: {y_test[i]} | Previsto: {predictions[i]}")

print("Relatorio de Classificacao:")
print(classification_report(y_test, predictions))


    

