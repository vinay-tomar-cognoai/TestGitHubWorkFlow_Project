import pandas as pd
import numpy as np
import re

import nltk
from nltk.corpus import stopwords
import pickle

# from scipy.stats import itemfreq
# from sklearn.model_selection import train_test_split
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import LabelEncoder
# from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer, HashingVectorizer
# from sklearn.metrics import confusion_matrix
from textblob import TextBlob


def predict_sentiment(message):
    # nb_clf = pickle.load(
    #     open("files/sentiment-analysis/emotion_classifier.sav", 'rb'))
    # message_history = []
    # message_history.append(message)
    # pred = nb_clf.predict(np.array(message_history))
    # emotions = ['Anger', 'Fear', 'Happy', 'Hate', 'Love',
    #             'Neutral', 'Sadness', 'Surprise', 'Worry']
    blob = TextBlob(message)
    polarity = blob.sentiment.polarity
    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment
