import numpy as np
import pandas as pd

from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import joblib

from mathtext_fastapi.constants import DATA_DIR

DEFAULT_MODEL_FILENAME="intent_classification_model.joblib"
DEFAULT_LABELED_DATA="labeled_data.csv"


def create_intent_classification_model(
    model_path=DATA_DIR / DEFAULT_MODEL_FILENAME,
    labeled_data_path=DATA_DIR / DEFAULT_LABELED_DATA
):
    encoder = SentenceTransformer('all-MiniLM-L6-v2')
    # path = list(Path.cwd().glob('*.csv'))

    labeled_data_path = Path(labeled_data_path)

    with labeled_data_path.open('r', newline='', encoding='utf-8') as f:
        df = pd.read_csv(f)
    df = df[df.columns[:2]]
    df = df.dropna()
    X_explore = np.array([list(encoder.encode(x)) for x in df['Utterance']])
    X = np.array([list(encoder.encode(x)) for x in df['Utterance']])
    y = df['Label']
    model = LogisticRegression(class_weight='balanced')
    model.fit(X, y, sample_weight=None)

    joblib.dump(model, model_path)


def retrieve_intent_classification_model(
        model_path=DATA_DIR / DEFAULT_MODEL_FILENAME
):
    model = joblib.load(model_path)
    return model


encoder = SentenceTransformer('all-MiniLM-L6-v2')
# model = retrieve_intent_classification_model()
model = joblib.load(DATA_DIR / DEFAULT_MODEL_FILENAME)


def predict_message_intent(message):
    tokenized_utterance = np.array([list(encoder.encode(message))])
    predicted_label = model.predict(tokenized_utterance)
    predicted_probabilities = model.predict_proba(tokenized_utterance)
    confidence_score = predicted_probabilities.max()

    return {"type": "intent", "data": predicted_label[0], "confidence": confidence_score}