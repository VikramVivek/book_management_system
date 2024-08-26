# Book Management System

## Overview

The Book Management System is a web application designed to manage books, reviews, and recommendations using advanced machine learning models. It integrates with AWS for scalable deployment, leverages FastAPI for the backend, and includes machine learning models deployed on AWS SageMaker for book recommendations. The application also provides summarization services for book content and reviews using language models.

## Features

- **User Management**: Register, login, and manage user preferences.
- **Book Management**: Create, view, update, and delete books.
- **Review Management**: Add, edit, and delete reviews for books.
- **Book Summarization**: Automatically generate summaries for books and reviews.
- **Book Recommendations**: Provide personalized book recommendations based on user preferences.
- **Admin Panel**: Admin access, Manage users, reviews, build recommendation model and data.

## Technologies

- **Backend**: FastAPI, PostgreSQL (Amazon RDS)
- **Frontend**: React (for future development)
- **Machine Learning**: AWS SageMaker for recommendation models, Transformers library for summarization
- **Caching**: AWS ElastiCache (Redis)
- **Deployment**: AWS EC2, RDS, SageMaker, ElastiCache

## Prerequisites

- **Python 3.9.13**
- **Docker** (for containerized deployment)
- **PostgreSQL**
- **Node.js and npm** (for frontend development)
- **AWS Account** with access to EC2, RDS, SageMaker, and ElastiCache

## Local Setup

1. **Clone the Repository**:
   bash
   git clone https://github.com/yourusername/book-management-system.git
   cd book-management-system
2. **Create a Virtual Environment**:
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. **Install Backend Dependencies**:
    bash
    Copy code
    pip install -r requirements.txt
    pip install -r requirements-dev.txt  # For development and testing
4. **Set Up Environment Variables**:
    Create a .env file in the project root and fill in the necessary environment variables. Use .env.example as a template.
    ```
    # Default
    ENVIRONMENT=dev
    LOG_LEVEL=DEBUG

    # Server
    HOST=0.0.0.0
    PORT=8000
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database
    DATABASE_URL=postgresql://postgres:T3sting@db/book_management

    # Auth
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

    # Redis
    REDIS_URL=redis://redis:6379/0
    REDIS_CACHE_TTL=3600
    USE_MOCK_REDIS=True

    # ML
    SAGEMAKER_ENDPOINT=recommendation-endpoint
    USE_SAGEMAKER=False
    ```
## Docker Setup

1. **Build the Docker Image**:
    ```
    docker-compose build
    ```
2. **Run the Application**:
    ```
    docker-compose up
    ```

## Access the API

-  **http://127.0.0.1:8000/docs#/**

## AWS Deployment
    
1. **Set Up PostgreSQL on RDS**:
    Create an RDS instance with PostgreSQL and update your .env file with the connection string.
2. **Deploy Summarization Service on EC2**:
    Launch an EC2 instance, install necessary dependencies, and deploy the summarization service.
3. **Deploy Recommendation Service on SageMaker**:
    Train and deploy your machine learning model using AWS SageMaker.
4. **Implement Caching with ElastiCache**:
    Set up a Redis cluster on ElastiCache for caching recommendations.
5. **Connect to AWS Services**: 
    Update your application to connect to the deployed AWS services.

## Running Tests

1. **Unit Tests**:
    Run tests using pytest to verify the functionality of the backend services.
    ```
    pip install -r requirements-dev.txt
    pytest
    ```

## Known Issues and Limitations

1. **AWS Integration**:
    Integration with AWS services like S3 and SageMaker is planned but not yet implemented..
2. **Future Enhancements**:
    The summarization service and recommendation service will be developed as separate modules and integrated later.

## Contributing

1. **Fork the Repository**:
    Create a fork of the project repository.
2. **Create a Feature Branch**:
    Create a branch for your feature or bug fix.
    git checkout -b feature/your-feature-name
3. **Commit Your Changes**:
    Make your changes and commit them to your branch.
    git commit -m "Add new feature"
4. **Push to GitHub**:
    Push your changes to GitHub.
    git push origin feature/your-feature-name
5. **Create a Pull Request**:
    Submit a pull request to the main branch for review.

### License
This project is licensed under the MIT License. See the LICENSE file for more details.

### Contact
Author: Vikram Vivek
GitHub: VikramVivek
