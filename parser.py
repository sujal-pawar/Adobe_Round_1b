import fitz  # PyMuPDF
import re

def extract_sections(pdf_path):
    """
    Parse the PDF at pdf_path, segment into sections and subsections.
    Returns a list of dicts: {
      "document": filename,
      "page": int,
      "title": str,
      "text": str
    }
    """

    doc = fitz.open(pdf_path)
    sections = []
    current = None

    # Heading regex matching versions like:
    # "1. Introduction"
    # "2. Model Deployment Strategies"
    # "2.1 Batch Inference"
    # "3 Conclusion" (without dot)
    heading_pattern = re.compile(r'^\d+(\.\d+)*\.?\s+[A-Z][^,;:\n]*$')

    # Step 1: Scan all spans to identify the most common top font size for headings
    heading_font_sizes = []
    body_font_sizes = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for line in b["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    if not text:
                        continue
                    if heading_pattern.match(text):
                        heading_font_sizes.append(size)
                    else:
                        body_font_sizes.append(size)

    # Compute threshold font size to distinguish heading and body text
    if heading_font_sizes:
        min_heading_font_size = min(heading_font_sizes)
    else:
        # Fallback threshold if no headings found in scan
        min_heading_font_size = 10  # Relaxed threshold for better extraction

    # To be a heading, font size must be >= min_heading_font_size

    # Step 2: Parse document and extract sections based on regex & font size

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue

            # Combine line spans into a full line text for heading detection robustness
            for line in b["lines"]:
                line_text = ""
                max_font_size = 0
                for span in line["spans"]:
                    txt = span["text"].strip()
                    if not txt:
                        continue
                    line_text += txt + " "
                    if span["size"] > max_font_size:
                        max_font_size = span["size"]

                line_text = line_text.strip()
                if not line_text:
                    continue

                # Heuristic: Is this line a heading?
                # Condition: matches heading pattern AND font size >= threshold
                if (max_font_size >= min_heading_font_size and 
                    heading_pattern.match(line_text) and
                    # Ensure no partial fragments
                    not line_text.endswith((',', ';', ':')) and
                    len(line_text.split()) > 1):
                    # New section detected
                    if current:
                        current["text"] = current["text"].strip()
                        sections.append(current)

                    current = {
                        "document": pdf_path,
                        "page": page_num + 1,
                        "title": line_text,
                        "text": ""
                    }
                elif current:
                    # Append to current section text, normalize whitespace
                    current["text"] += line_text + " "

    # Append final section
    if current:
        current["text"] = current["text"].strip()
        sections.append(current)

    print(f"[DEBUG] Extracted {len(sections)} sections from {pdf_path}")
    return sections
