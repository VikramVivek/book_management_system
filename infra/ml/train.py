# train.py
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors


def train_recommendation_model(input_data_path, model_output_dir):
    # Load data (Assume a CSV with 'id', 'genre', 'author', 'summary', 'content')
    import pandas as pd

    data = pd.read_csv(input_data_path)

    # Prepare the data
    book_data = [
        f"{row['genre']} {row['author']} {row['summary']} {row['content']}"
        for _, row in data.iterrows()
    ]

    # Train a simple model using TF-IDF and Nearest Neighbors
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(book_data)

    model = NearestNeighbors(n_neighbors=10, algorithm="auto").fit(X)

    # Save the model and vectorizer to a file
    with open(os.path.join(model_output_dir, "model.pkl"), "wb") as model_file:
        pickle.dump((model, vectorizer, data["id"].tolist()), model_file)

    return {"detail": "Model trained successfully"}


if __name__ == "__main__":
    # SageMaker passes the input data path and output model path via
    # environment variables
    input_data_path = os.environ.get("SM_CHANNEL_TRAIN")
    model_output_dir = os.environ.get("SM_MODEL_DIR")

    train_recommendation_model(input_data_path, model_output_dir)
