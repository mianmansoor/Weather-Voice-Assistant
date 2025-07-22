import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Load dataset
df = pd.read_csv("weather_chatbot_data.csv")

# Split into X and y
X = df["sentence"]
y = df["intent"]

# Create pipeline for intent classification
intent_pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", LogisticRegression(max_iter=1000))
])

# Train
intent_pipeline.fit(X, y)

# Save the model
joblib.dump(intent_pipeline, "intent_model.pkl")

print("✅ Intent classifier trained and saved as intent_model.pkl")
