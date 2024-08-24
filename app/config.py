"""
Configuration module for the application.

This module contains constants and environment variables that define
the configuration of the application.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Now you can access the environment variables
ENVIRONMENT = os.getenv("ENVIRONMENT")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", "8000")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

SECRET_KEY = os.getenv("SECRET_KEY", "local")
ALGORITHM = os.getenv("ALGORITHM", "H256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 3000))

REDIS_URL = os.getenv("REDIS_URL")
REDIS_CACHE_TTL = os.getenv("REDIS_CACHE_TTL")

SAGEMAKER_ENDPOINT = os.getenv("SAGEMAKER_ENDPOINT")

SUMMARIZATION_API_URL = os.getenv("SUMMARIZATION_API_URL")
RECOMMENDATION_API_URL = os.getenv("RECOMMENDATION_API_URL")
