# Dockerfile

# ---- Stage 1: Build ----
# Use a slim Python image to install dependencies. We name this stage "builder".
FROM python:3.10-slim as builder

# Set the working directory
WORKDIR /app

# We create a virtual environment to keep dependencies clean and isolated.
# This is a best practice for Python Docker images.
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy only the requirements file to leverage Docker's layer caching.
COPY requirements.txt .

# Install the CPU-ONLY version of PyTorch first, then the rest of your requirements.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ---- Stage 2: Final Image ----
# Start from a fresh, clean base image for the final submission.
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment with all the installed packages from the builder stage.
COPY --from=builder /app/venv /app/venv

# Copy your local models and NLTK data.
COPY local_model/ /app/local_model/
COPY nltk_data/ /app/nltk_data/

# Copy the rest of your application source code.
COPY . .

# Set the environment variables needed for your application to run.
ENV PATH="/app/venv/bin:$PATH"
ENV NLTK_DATA=/app/nltk_data

# --- THIS IS THE UPDATED COMMAND ---
# Define the default command to run your application with the travel PDFs.
CMD ["python", "main.py", "--pdfs", "test_pdfs/SouthofFranceCities.pdf", "test_pdfs/SouthofFranceCuisine.pdf", "test_pdfs/SouthofFranceHistory.pdf", "test_pdfs/SouthofFranceRestaurantsandHotels.pdf",  "--persona", "travel_planner", "--job", "France Travel", "--output", "output/final_test.json"]
