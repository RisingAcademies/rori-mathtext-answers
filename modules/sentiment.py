from transformers import pipeline

sentiment_obj = pipeline(task="sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def sentiment(text):
    # Returns sentiment value
    return sentiment_obj(text)
