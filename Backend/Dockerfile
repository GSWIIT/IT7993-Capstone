FROM python:3.10

WORKDIR /app

# Install system dependencies for building native extensions
RUN apt-get update && \
    apt-get install -y cmake build-essential python3-dev libgl1 && \
    apt-get clean

# Copy backend source code
COPY Backend/LoginApp/ . .

# Copy blockchain folder
COPY ../BlockChain/. .

# Copy and install dependencies
COPY Backend/Requirements/python_requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r python_requirements.txt

EXPOSE 5000

CMD ["python", "src/app.py"]
