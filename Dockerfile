# Dockerfile - Final Hyper-Optimized Version

# ---- Stage 1: Build & Data Preparation ----
# Use a slim Python image to build dependencies and download data.
FROM python:3.10-slim as builder

WORKDIR /app

# Create and activate a virtual environment.
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies (CPU-only PyTorch + requirements).
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# --- THIS IS THE KEY FIX ---
# Download the models and data INSIDE this temporary builder stage.
RUN mkdir -p /app/model_data/local_model && \
    python3 -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('/app/model_data/local_model')"

RUN mkdir -p /app/model_data/nltk_data && \
    python3 -c "import nltk; nltk.download(['punkt', 'punkt_tab'], download_dir='/app/model_data/nltk_data')"
# --- END OF KEY FIX ---

# ---- Stage 2: Final Production Image ----
# Start from a fresh, clean base image.
FROM python:3.10-slim

WORKDIR /app

# Copy the clean virtual environment from the builder stage.
COPY --from=builder /app/venv /app/venv

# --- COPY ONLY THE FINAL, CLEAN DATA ---
# Copy the prepared model and NLTK data from the builder stage.
# This leaves all download cache and temporary files behind.
COPY --from=builder /app/model_data/local_model/ /app/local_model/
COPY --from=builder /app/model_data/nltk_data/ /app/nltk_data/

# Copy your application source code.
COPY . .

# Activate the virtual environment for the final image.
ENV PATH="/app/venv/bin:$PATH"
ENV NLTK_DATA=/app/nltk_data

# Define the default command to run your application.
CMD ["python", "main.py", "--pdfs", "test_pdfs/SouthofFranceCities.pdf", "test_pdfs/SouthofFranceCuisine.pdf", "test_pdfs/SouthofFranceHistory.pdf", "test_pdfs/SouthofFranceRestaurantsandHotels.pdf",  "--persona", "travel_planner", "--job", "France Travel", "--output", "output/final_test.json"]
