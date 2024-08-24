import logging

from sagemaker.sklearn import SKLearnModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def deploy_model():
    """
    Deploy a pre-trained scikit-learn model on AWS SageMaker.

    This function assumes that the model is already trained and stored in an S3 bucket.
    It then deploys the model to a SageMaker endpoint which can be used for inference.

    Returns:
        predictor: The deployed SageMaker predictor object, which can be used to make
                   predictions.
    """
    model_data = "s3://your-bucket/path/to/model.tar.gz"
    logger.info(f"Using model data from: {model_data}")

    # Define the SageMaker SKLearnModel
    sklearn_model = SKLearnModel(
        model_data=model_data,
        role="your-sagemaker-role",  # IAM role with SageMaker permissions
        entry_point="train.py",  # Path to the script or inference code
        framework_version="0.23-1",  # scikit-learn version
    )

    logger.info("Deploying the model to SageMaker endpoint...")

    # Deploy the model
    predictor = sklearn_model.deploy(
        initial_instance_count=1,  # Number of instances to deploy the model to
        instance_type="ml.m5.large",  # Type of instance to use for deployment
        endpoint_name="recommendation-endpoint",  # Name of the endpoint
    )

    logger.info("Model deployed successfully to endpoint: recommendation-endpoint")

    return predictor


def make_prediction(predictor, input_data):
    """
    Make a prediction using the deployed SageMaker endpoint.

    Args:
        predictor: The SageMaker predictor object returned from the deployment.
        input_data (list): List of input data for making predictions.

    Returns:
        prediction: The prediction result from the model.
    """
    logger.info(f"Making prediction for input: {input_data}")
    prediction = predictor.predict(input_data)
    logger.info(f"Prediction result: {prediction}")
    return prediction


if __name__ == "__main__":
    predictor = deploy_model()

    # Example usage: Making predictions using the deployed endpoint
    input_data = ["Sci-Fi Asimov Great book about space and robots"]
    prediction = make_prediction(predictor, input_data)
    print(prediction)
