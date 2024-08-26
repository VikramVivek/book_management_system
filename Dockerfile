# Use an official Python runtime as a parent image
FROM python:3.9.13

# Set the working directory in the container
WORKDIR /bms

# Copy the requirements file into the container
COPY requirements.txt requirements-dev.txt ./

# Install dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir psycopg2

# Copy the current directory contents into the container at /bms
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Command to run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
