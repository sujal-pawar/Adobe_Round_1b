# PDF Section Extraction: Persona-Driven Document Intelligence

A robust solution for extracting and refining relevant sections and subsections from PDF documents based on a specific persona and job-to-be-done, leveraging semantic search and natural language processing.

## Table of Contents
- [Features](#features)
- [Hackathon Submission: Build & Run Instructions](#hackathon-submission-build--run-instructions)
- [Models and Offline Operation](#models-and-offline-operation)
- [Output Format and Scoring](#output-format-and-scoring)
- [Performance Validation](#performance-validation)
- [Project Structure](#project-structure)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Local Setup (Manual)](#local-setup-manual)

---

## Features

- **Persona-Driven Relevance:** Extracts and ranks document sections based on a defined user persona and a specific job-to-be-done.
- **Robust PDF Processing:** Handles diverse PDF formats (e.g., academic papers, travel guides, financial reports) by relaxing traditional heading detection for improved extraction.
- **Semantic Search & Embedding:** Utilizes a pre-trained sentence-transformer model for accurate semantic understanding and relevance scoring.
- **Granular Subsection Refinement:** Further refines and scores subsections for precise analysis, crucial for the "Sub-Section Relevance" criteria.
- **Fully Offline Operation:** Guarantees no external API calls or network access during execution, meeting a critical hackathon constraint.
- **Containerized Deployment:** Provided with a `Dockerfile` for reproducible and consistent execution in any Docker environment.
- **Standardized JSON Output:** Generates results in the hackathon's specified JSON format, including metadata, extracted sections, and detailed subsection analysis with relevance scores.

---

## Hackathon Submission: Build & Run Instructions

**This section details the exact commands that will be used by the Adobe Hackathon evaluators to build and run your solution.**

### **Prerequisites**
- [Docker](https://www.docker.com/get-started) must be installed and running on an `amd64` (x86_64) Linux environment (e.g., Ubuntu via WSL).

### **Step 1: Build the Docker Image**

From the root of the project directory (e.g., `~/final_build/` in your Ubuntu WSL environment), execute the following command. This will build the Docker image with the correct platform specification.

```sh
docker build --platform linux/amd64 -t ps1b-submission .
```

*(This command creates an image named `ps1b-submission`.)*

### **Step 2: Run the Docker Container (Offline & Volume Mounts)**

The solution is designed to automatically process input PDFs found within the container's `/app/test_pdfs` directory and save its JSON output to `/app/output`. To facilitate this, the evaluators will typically mount external directories.

Here is the exact command as per the hackathon's "Expected Execution" (adapted for Round 1B input/output pattern):

```sh
docker run --rm \
    --platform linux/amd64 \
    --network none \
    -v "$(pwd)/output:/app/output" \
    ps1b-submission
```

*(**Note:** For the actual evaluation, input PDFs will likely be provided directly into the container or mounted as a volume. The `CMD` instruction in the `Dockerfile` specifies the demo execution using the `test_pdfs` included in the repository. The example `docker run` command will execute `main.py` using these internal test PDFs and output to your mounted `output` folder.)*

- `--rm`: Automatically removes the container after it finishes.
- `--platform linux/amd64`: Ensures compatibility with the evaluation environment.
- `--network none`: **Crucial for testing offline capability.** This confirms all models and data are self-contained.
- `-v "$(pwd)/output:/app/output"`: Mounts your local `output` directory to the container's `/app/output`, allowing you to retrieve the generated `final_test.json`.

Upon successful execution, a `final_test.json` file containing the extracted sections and subsection analysis will be generated in your local `output/` directory.

---

## Models and Offline Operation

This project is engineered for **100% offline operation** with **no internet access required** during execution, fully complying with hackathon constraints.

- **Semantic Embedding Model:** The core of the relevance ranking is powered by `all-MiniLM-L6-v2`, a lightweight sentence-transformer model. This model's files (approx. 120MB) are downloaded and stored within the Docker image during the build process, ensuring it's available without any network calls at runtime.
- **NLTK Tokenizer:** The `punkt` and `punkt_tab` tokenizers from the NLTK library are used for efficient text processing. Like the semantic model, these are pre-downloaded and bundled into the Docker image.

All necessary model and data files reside within the final Docker image, guaranteeing robust performance in a constrained environment.

---

## Output Format and Scoring

The application generates a JSON output file (`output/final_test.json`) conforming to the specified Round 1B schema.

Key aspects for scoring:
- **`extracted_sections`:** Provides a ranked list of relevant sections from input documents.
- **`subsection_analysis`:** Offers granular details for highly relevant subsections, including a `relevance_score` for each. This score (ranging from 0.0 to 1.0) directly quantifies the quality and ranking of granular subsection extraction, addressing the "Sub-Section Relevance" criteria (40 points).

---

## 📊 Performance Validation

The solution has been rigorously tested to meet Adobe's Round 1B performance constraints for CPU-only execution on `amd64` architecture.

- **Model Size:** The largest model used (`all-MiniLM-L6-v2`) is approximately **120MB**, well within the hackathon's **1GB model size limit**.
- **Processing Time:**
        - Processes a collection of **3-5 documents in well under 60 seconds.**

### Test Summary (using included `test_pdfs`)
- `2_pdfs_minimum`: ~19.02 seconds (2 PDFs) - ✅ PASS
- `3_pdfs_standard`: ~19.58 seconds (3 PDFs) - ✅ PASS
- `5_pdfs_maximum`: ~21.36 seconds (5 PDFs) - ✅ PASS

*For detailed test execution and methodology, please refer to `test_performance.py`.*

---

## Project Structure

```
pdf_section_extraction/
├── Dockerfile                 # Docker configuration for containerization
├── local_model/               # Stores offline sentence-transformer model files
├── nltk_data/                 # Stores offline NLTK data (punkt, punkt_tab)
├── test_pdfs/                 # Directory for input PDF files (contains sample PDFs)
├── output/                    # Directory for generated JSON results
├── create_sample_pdf.py       # Utility script to generate a sample PDF
├── embedder.py                # Module for generating text embeddings
├── main.py                    # Main execution script and CLI interface
├── parser.py                  # Module for PDF parsing and section extraction
├── ranker.py                  # Module for ranking sections based on relevance
├── refiner.py                 # Module for refining and scoring subsections
├── requirements.txt           # Python project dependencies
├── test_performance.py        # Script to validate performance against constraints
└── README.md                  # Project documentation (this file)
```

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements

This project uses the following open-source libraries and models:
- [sentence-transformers](https://www.sbert.net/) for semantic search and embedding.
- [NLTK](https://www.nltk.org/) for sentence tokenization.
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for efficient PDF parsing.
- [PyTorch](https://pytorch.org/) as the underlying deep learning framework.

We extend our sincere gratitude to the developers and contributors of these projects for their invaluable work.

---

## Local Setup (Manual)

*(Keep this section for local development, but place it lower in the README as the Hackathon focus is on Docker.)*

Follow these instructions if you prefer to run the project directly on your machine without Docker.

1. **Clone the repository:**
        ```sh
        git clone https://github.com/yourusername/pdf_section_extraction.git
        cd pdf_section_extraction
        ```

2. **Create and activate a virtual environment:**
        ```sh
        python -m venv venv

        # For Windows
        .\venv\Scripts\activate

        # For Linux/macOS
        source venv/bin/activate
        ```

3. **Install dependencies:**
        ```sh
        pip install -r requirements.txt
        ```

4. **Download NLTK data:**
        Run the following command in your terminal to download the 'punkt' and 'punkt_tab' tokenizers needed for sentence splitting.
        ```sh
        python -c "import nltk; nltk.download(['punkt', 'punkt_tab'], download_dir='./nltk_data')"
        ```

5. **Download the Sentence Transformer Model:**
        Run the following command to download the `all-MiniLM-L6-v2` model into your `local_model` directory:
        ```sh
        python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('./local_model')"
        ```

6. **Run the script:**
        Place your PDF files in the `test_pdfs/` directory and run the main script.
        ```sh
        python main.py --pdfs test_pdfs/SouthofFranceCities.pdf test_pdfs/SouthofFranceCuisine.pdf --persona "travel planner" --job "France Travel" --output output/final_test.json
        ```
        Check the `output/` directory for the `final_test.json` file.
