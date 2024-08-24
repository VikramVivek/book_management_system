import logging
import os
import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_recommendation_model(input_data_path, model_output_dir):
    """
    Train a recommendation model using the input data and save the model to the
    specified output directory.

    Args:
        input_data_path (str): Path to the input CSV file containing book data.
        model_output_dir (str): Directory where the trained model and vectorizer
                                will be saved.

    Returns:
        dict: A dictionary containing a success message.
    """
    logger.info(f"Loading data from: {input_data_path}")

    # Load data (Assume a CSV with 'id', 'genre', 'author', 'summary', 'content')
    data = pd.read_csv(input_data_path)

    logger.info("Preparing data for training...")
    # Prepare the data
    book_data = [
        f"{row['genre']} {row['author']} {row['summary']} {row['content']}"
        for _, row in data.iterrows()
    ]

    # Train a simple model using TF-IDF and Nearest Neighbors
    logger.info("Training the TF-IDF and Nearest Neighbors model...")
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(book_data)

    model = NearestNeighbors(n_neighbors=10, algorithm="auto").fit(X)

    # Save the model and vectorizer to a file
    model_path = os.path.join(model_output_dir, "model.pkl")
    logger.info(f"Saving trained model to: {model_path}")
    with open(model_path, "wb") as model_file:
        pickle.dump((model, vectorizer, data["id"].tolist()), model_file)

    logger.info("Model training completed successfully.")
    return {"detail": "Model trained successfully"}


if __name__ == "__main__":
    # SageMaker passes the input data path and output model path via
    # environment variables
    input_data_path = os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train")
    model_output_dir = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")

    logger.info("Starting model training...")
    train_recommendation_model(input_data_path, model_output_dir)
