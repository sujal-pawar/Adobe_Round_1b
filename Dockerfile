# ---- Stage 1: Build ----
# Use a slim Python image to install dependencies. We name this stage "builder".
FROM python:3.10-slim as builder

WORKDIR /app

# We create a virtual environment to keep dependencies clean and isolated.
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

WORKDIR /app

# Copy the virtual environment with all the installed packages from the builder stage.
COPY --from=builder /app/venv /app/venv

# --- THIS IS THE CRITICAL FIX ---
# Activate the virtual environment for all subsequent commands.
# This line MUST come BEFORE any RUN commands that need the installed packages.
ENV PATH="/app/venv/bin:$PATH"
ENV NLTK_DATA=/app/nltk_data
# --- END OF FIX ---

# Instead of COPYing, we run the download commands directly in the Dockerfile.
# These commands will now use the correct Python from the virtual environment.
RUN mkdir -p local_model && \
    python3 -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('./local_model')"

RUN mkdir -p nltk_data && \
    python3 -c "import nltk; nltk.download('punkt', download_dir='./nltk_data')"

# Copy the rest of your application source code.
COPY . .

# Define the default command to run your application with the travel PDFs.
CMD ["python", "main.py", "--pdfs", "test_pdfs/SouthofFranceCities.pdf", "test_pdfs/SouthofFranceCuisine.pdf", "test_pdfs/SouthofFranceHistory.pdf", "test_pdfs/SouthofFranceRestaurantsandHotels.pdf",  "--persona", "travel_planner", "--job", "France Travel", "--output", "output/final_test.json"]
