# PDF Section Extraction & Highlighting

## Overview
This project automatically extracts, ranks, and summarizes the most relevant sections from one or more PDF files based on your study goal or query. It uses AI-powered semantic search to find the best highlights for your needs (e.g., "Study OOPs").

---

## How It Works

### 1. **PDF Parsing**
- The system opens each PDF and scans for headings (section titles) using font size and text patterns.
- Each heading and its associated text are grouped as a "section."
- If headings are not detected, you may need to adjust the heading detection logic in `parser.py`.

### 2. **Embedding & Semantic Search**
- Each section and your study prompt (e.g., "Student Study OOPs") are converted into vector embeddings using a local AI model (`sentence-transformers`).
- These embeddings allow the system to measure how closely each section matches your study goal.

### 3. **Ranking**
- The system calculates similarity scores between your prompt and each section using cosine similarity.
- The most relevant sections (highest scores) are selected as highlights.
- By default, the top highlights per PDF are included in the output.

### 4. **Refinement**
- Each highlight can be further broken down into smaller, focused subsections for easier reading.

### 5. **Output**
- The results are saved in a JSON file, including:
  - PDF name
  - Page number
  - Section title
  - Ranked highlights and refined text

---

## Usage

### Command Line Example
```powershell
python main.py --pdfs test_pdfs/OOP1.pdf test_pdfs/OOP2.pdf --persona "Student" --job "Study OOPs" --output output/result.json
```
- `--pdfs`: List one or more PDF files to process
- `--persona`: Describe the user (e.g., "Student")
- `--job`: Describe the study goal (e.g., "Study OOPs")
- `--output`: Path to save the result JSON

### Output Example
The output JSON will contain the most relevant sections and their highlights for each PDF.

---

## Project Structure
- `main.py`: Orchestrates the workflow, handles arguments, and writes output
- `parser.py`: Extracts sections from PDFs using heading detection
- `embedder.py`: Converts text to embeddings using a local AI model
- `ranker.py`: Ranks sections by relevance to your study goal
- `refiner.py`: Further breaks down highlights into focused subsections
- `output/result.json`: Final output with all highlights
- `local_model/`: Contains the local sentence-transformers model for offline inference

---

## Troubleshooting
- **No sections extracted:**
  - Check if your PDF headings match the expected style (numbering, font size, capitalization)
  - Adjust the heading regex or font size threshold in `parser.py`
- **No highlights for a PDF:**
  - The content may not match your study prompt
  - Lower the ranking threshold in `ranker.py`
- **Model errors:**
  - Ensure all files in `local_model/` are present for offline inference

---

## Customization
- Change the number of highlights per PDF in `main.py` (`top_k_per_pdf`)
- Adjust heading detection logic in `parser.py` for different document styles
- Use different study prompts to get highlights tailored to your needs

---

## Example Use Cases
- Quickly find the most important sections for exam revision
- Summarize technical PDFs for research or study
- Extract code examples and explanations from programming textbooks

---

## Requirements
- Python 3.x
- PyMuPDF
- sentence-transformers
- scikit-learn
- numpy

---

## Credits
Developed for the Adobe India Hackathon.

---

## License
MIT License
