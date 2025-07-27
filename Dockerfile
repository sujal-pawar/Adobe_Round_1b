# Dockerfile - The "Surgical Copy" Final Version

# ---- Stage 1: Build & Data Preparation ----
# This stage prepares all our dependencies and data. It can be as large as it needs to be.
FROM python:3.10-slim as builder

WORKDIR /app

# Create and use a virtual environment for a clean dependency install.
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install all dependencies into the venv.
COPY requirements.txt .
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Download the models and data into a dedicated folder.
RUN mkdir -p /app/model_data/local_model && \
    python3 -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('/app/model_data/local_model')"

RUN mkdir -p /app/model_data/nltk_data && \
    python3 -c "import nltk; nltk.download(['punkt', 'punkt_tab'], download_dir='/app/model_data/nltk_data')"


# ---- Stage 2: Final Production Image ----
# This stage builds the minimal final image, taking only what it needs.
FROM python:3.10-slim

WORKDIR /app

# --- THE ULTIMATE FIX: SURGICAL COPY ---
# Instead of copying the whole venv, copy ONLY the installed packages
# directly from the builder's venv into the final image's main Python path.
# This is the key to eliminating all bloat.
COPY --from=builder /app/venv/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy the prepared model and NLTK data from the builder stage.
COPY --from=builder /app/model_data/local_model/ /app/local_model/
COPY --from=builder /app/model_data/nltk_data/ /app/nltk_data/
# --- END OF ULTIMATE FIX ---

# Copy your application source code.
COPY . .

# Set the environment variable for NLTK.
# We don't need to set the PATH anymore, as we installed directly to the system Python.
ENV NLTK_DATA=/app/nltk_data

# Define the default command to run your application.
CMD ["python", "main.py", "--pdfs", "test_pdfs/SouthofFranceCities.pdf", "test_pdfs/SouthofFranceCuisine.pdf", "test_pdfs/SouthofFranceHistory.pdf", "test_pdfs/SouthofFranceRestaurantsandHotels.pdf",  "--persona", "travel_planner", "--job", "France Travel", "--output", "output/final_test.json"]
