import numpy as np
import pandas as pd

from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from joblib import dump, load

def pickle_model(model):
    DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data" / "intent_classification_model.joblib"
    dump(model, DATA_DIR)


def create_intent_classification_model():
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    # path = list(Path.cwd().glob('*.csv'))
    DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data" / "labeled_data.csv"

    print("DATA_DIR")
    print(f"{DATA_DIR}")

    with open(f"{DATA_DIR}",'r', newline='', encoding='utf-8') as f:
        df = pd.read_csv(f)
    df = df[df.columns[:2]]
    df = df.dropna()
    X_explore = np.array([list(encoder.encode(x)) for x in df['Utterance']])
    X = np.array([list(encoder.encode(x)) for x in df['Utterance']])
    y = df['Label']
    model = LogisticRegression(class_weight='balanced')
    model.fit(X, y, sample_weight=None)

    print("MODEL")
    print(model)

    pickle_model(model)


def retrieve_intent_classification_model():
    DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data" / "intent_classification_model.joblib"
    model = load(DATA_DIR)
    return model


encoder = SentenceTransformer('all-MiniLM-L6-v2')
# model = retrieve_intent_classification_model()
DATA_DIR = Path(__file__).parent.parent / "mathtext_fastapi" / "data" / "intent_classification_model.joblib"
model = load(DATA_DIR)


def predict_message_intent(message):
    tokenized_utterance = np.array([list(encoder.encode(message))])
    predicted_label = model.predict(tokenized_utterance)
    predicted_probabilities = model.predict_proba(tokenized_utterance)
    confidence_score = predicted_probabilities.max()

    return {"type": "intent", "data": predicted_label[0], "confidence": confidence_score}