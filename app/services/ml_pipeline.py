import pandas as pd
import talib
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
from typing import Tuple, Dict

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df_feat = pd.DataFrame(index=df.index)

    for lag in [1,3,5,10]:
        df_feat[f'ret_{lag}'] = df['close'].pct_change(lag)

    df_feat['SMA_10'] = talib.SMA(df['close'], timeperiod=10)
    df_feat['SMA_50'] = talib.SMA(df['close'], timeperiod=50)

    df_feat['RSI'] = talib.RSI(df['close'], timeperiod=14)

    df_feat['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)

    df_feat['vol'] = df['close'].pct_change().rolling(10).std()

    df_feat['momentum'] = df['close'] - df['close'].shift(20)

    df_feat = df_feat.dropna()
    return df_feat

def train_model(X: pd.DataFrame, y: pd.Series, model_type: str = 'logreg') -> Tuple[object, Dict]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    if model_type == 'logreg':
        model = LogisticRegression()
    elif model_type == 'rf':
        model = RandomForestClassifier(n_estimators=100)
    else:
        raise ValueError("model_type inválido")

    model.fit(X_scaled, y)
    y_pred = model.predict(X_scaled)

    metrics = {
        'accuracy': accuracy_score(y, y_pred),
        'precision': precision_score(y, y_pred, zero_division=0),
        'recall': recall_score(y, y_pred, zero_division=0)
    }

    joblib.dump({'model': model, 'scaler': scaler}, f'{model_type}_model.pkl')

    return model, metrics

def predict(df: pd.DataFrame, model_path: str = 'logreg_model.pkl') -> pd.Series:
    model_dict = joblib.load(model_path)
    model = model_dict['model']
    scaler = model_dict['scaler']

    X = prepare_features(df)
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    return pd.Series(y_pred, index=X.index)
