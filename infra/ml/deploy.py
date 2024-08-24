from sagemaker.sklearn import SKLearnModel

# Assume you have already trained the model and saved it
model_data = "s3://your-bucket/path/to/model.tar.gz"

# Define the SageMaker SKLearnModel
sklearn_model = SKLearnModel(
    model_data=model_data,
    role="your-sagemaker-role",
    entry_point="train.py",  # or the path to your inference script
    framework_version="0.23-1",
)

# Deploy the model
predictor = sklearn_model.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name="recommendation-endpoint",
)

# Example usage: Making predictions using the deployed endpoint
prediction = predictor.predict(["Sci-Fi Asimov Great book about space and robots"])
print(prediction)
