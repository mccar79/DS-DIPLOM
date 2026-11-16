# model_utils.py
import pickle
import numpy as np
import pandas as pd

# --- Загрузка модели ---
with open('models/model.pkl', 'rb') as f:
    MODEL = pickle.load(f)

with open('models/encoder.pkl', 'rb') as f:
    ENCODER = pickle.load(f)

with open('models/feature_columns.pkl', 'rb') as f:
    FEATURE_COLUMNS = pickle.load(f)

with open('models/zipcode_mapping.pkl', 'rb') as f:
    ZIPCODE_MAPPING = pickle.load(f)

with open('models/global_mean.pkl', 'rb') as f:
    GLOBAL_MEAN = pickle.load(f)


CATEGORICAL_FEATURES = ['city', 'state', 'property_type_group']

# Подготовка категориальных признаков и zipCode аналогично подготовке перед обучением модели
def prepare_features(input_dict: dict) -> pd.DataFrame:
    # Собираем DataFrame из одного объекта ---
    X = pd.DataFrame([input_dict])

    # One-Hot Encoding ---
    # Убеждаемся, что все категориальные колонки — строки
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].astype(str)

    X_encoded = ENCODER.transform(X[CATEGORICAL_FEATURES])
    encoded_columns = ENCODER.get_feature_names_out(CATEGORICAL_FEATURES)
    X_encoded_df = pd.DataFrame(
        X_encoded, columns=encoded_columns, index=X.index
    )

    X = X.drop(columns=CATEGORICAL_FEATURES)
    X = pd.concat([X, X_encoded_df], axis=1)

    # Target Encoding для zipcode ---
    X['zipcode'] = (
        X['zipcode']
        .astype('string')
        .fillna('missing')
    )
    X['zipcode_target_mean'] = (
        X['zipcode']
        .map(ZIPCODE_MAPPING)
        .fillna(GLOBAL_MEAN)
    )
    X = X.drop(columns=['zipcode'])

    # Выравнивание колонок ---
    X = X.reindex(columns=FEATURE_COLUMNS, fill_value=0)

    return X

# Прогноз цены объекта недвижимости
def predict_price(input_dict: dict) -> float:
    X = prepare_features(input_dict)
    pred_log = MODEL.predict(X)[0]
    return round(float(np.expm1(pred_log)), 2)