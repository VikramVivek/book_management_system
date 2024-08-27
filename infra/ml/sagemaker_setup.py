import logging

import sagemaker
from sagemaker.sklearn.estimator import SKLearn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_sagemaker_training():
    """
    Set up and launch a SageMaker training job for a scikit-learn model.

    This function initializes a SageMaker session, uploads training data to S3,
    and configures a scikit-learn estimator to run the training job on AWS SageMaker.

    Returns:
        sklearn_estimator: The SageMaker SKLearn estimator object.
    """
    logger.info("Initializing SageMaker session...")
    sagemaker_session = sagemaker.Session()

    # Set the IAM role
    role = "your-sagemaker-execution-role"  # Replace with your SageMaker execution role
    logger.info(f"Using IAM role: {role}")

    # Define the S3 bucket and prefix to store the model and data
    bucket = "your-s3-bucket-name"
    prefix = "recommendation-model"
    logger.info(f"Using S3 bucket: {bucket} with prefix: {prefix}")

    # Upload the training data to S3
    train_input = sagemaker_session.upload_data(
        "path/to/your/local/data.csv", bucket=bucket, key_prefix=f"{prefix}/data"
    )
    logger.info(f"Training data uploaded to: {train_input}")

    # Create the SKLearn estimator
    logger.info("Creating SKLearn estimator...")
    sklearn_estimator = SKLearn(
        entry_point="train.py",  # The script name for training
        role=role,
        instance_count=1,
        instance_type="ml.m5.large",
        framework_version="0.23-1",  # You can choose another sklearn version if needed
        py_version="py3",
        script_mode=True,  # Use script mode to directly use your script
        output_path=f"s3://{bucket}/{prefix}/output",  # Where to save the model
        hyperparameters={  # Optional: Add any hyperparameters for your script here
            "epochs": 10,
            "batch-size": 32,
        },
    )

    # Launch the training job
    logger.info("Launching SageMaker training job...")
    sklearn_estimator.fit({"train": train_input})
    logger.info("SageMaker training job launched successfully.")

    return sklearn_estimator


if __name__ == "__main__":
    setup_sagemaker_training()
