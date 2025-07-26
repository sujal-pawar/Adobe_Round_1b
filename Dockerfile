# Use a modern, slim Python image as the base.
FROM python:3.10-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file first. This step is cached, and dependencies
# will only be re-installed if this file changes.
COPY requirements.txt .

# Install the Python dependencies specified in the requirements.txt file.
RUN pip install --no-cache-dir -r requirements.txt

# Download the NLTK 'punkt' tokenizer data. This is also cached.
RUN python -c "import nltk; nltk.download('punkt')"

# Now, copy the rest of your application's source code.
# This includes main.py, refiner.py, and the local_model/ directory.
COPY . .

# Set the entrypoint to run the main script when the container starts.
ENTRYPOINT ["python", "main.py"]
