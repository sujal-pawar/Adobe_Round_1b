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

4. Download NLTK data:
```python
python -c "import nltk; nltk.download('punkt')"
```

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