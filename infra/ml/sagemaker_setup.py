import sagemaker
from sagemaker.sklearn.estimator import SKLearn

# Initialize the SageMaker session
sagemaker_session = sagemaker.Session()

# Set the IAM role
role = "your-sagemaker-execution-role"  # Replace with your SageMaker execution role

# Define the S3 bucket and prefix to store the model and data
bucket = "your-s3-bucket-name"
prefix = "recommendation-model"

# Upload the training data to S3
train_input = sagemaker_session.upload_data(
    "path/to/your/local/data.csv", bucket=bucket, key_prefix=f"{prefix}/data"
)

# Create the SKLearn estimator
sklearn_estimator = SKLearn(
    entry_point="train.py",  # The script name from above
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
sklearn_estimator.fit({"train": train_input})
