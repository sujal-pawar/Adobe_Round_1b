# PDF Section Extraction

A tool for extracting and refining sections from PDF documents using semantic search and natural language processing.

## Features

- Extract sections from PDF documents
- Semantic search using sentence transformers
- Section refinement based on relevance
- JSON output format

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf_section_extraction.git
cd pdf_section_extraction
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data (for sentence tokenization):
```python
python -c "import nltk; nltk.download('punkt')"
```

5. Download and place the sentence-transformers model:
The project uses a lightweight local semantic model (e.g., MiniLM) from the `sentence-transformers` library. All model files are stored in the `local_model/` directory for fully offline operation. No external API calls are made during inference.

**External Models Used:**
- [sentence-transformers](https://www.sbert.net/): MiniLM or similar lightweight transformer model (all files in `local_model/`)
- [NLTK](https://www.nltk.org/): Only the 'punkt' tokenizer is required for sentence splitting

**Note:** Ensure all model files are present in `local_model/` before running offline. If you need to change the model, download it using the sentence-transformers library and copy the files to `local_model/`.

## Usage

1. Place PDF files in `test_pdfs/` directory
2. Run the extraction:
```bash
python main.py --pdfs test_pdfs/sample.pdf --persona "PhD student" --job "Write a review"
```
3. Check results in `output/result.json`

## Project Structure

```
pdf_section_extraction/
├── test_pdfs/          # Input PDF files
├── output/             # Generated JSON results
├── create_sample_pdf.py # PDF generation script
├── refiner.py          # Text refinement module
├── main.py            # Main execution script
├── requirements.txt   # Project dependencies
└── README.md         # Documentation
```

## License

MIT License

## Acknowledgements

This project uses the following open-source libraries and models:
- [sentence-transformers](https://www.sbert.net/) for semantic search and embedding (MiniLM or similar)
- [NLTK](https://www.nltk.org/) for sentence tokenization

We thank the developers and contributors of these projects for their valuable work.