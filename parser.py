import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple


def is_table_of_contents_entry(text: str) -> bool:
    """
    Detect if a text block is a Table of Contents entry
    Returns True if text appears to be a TOC entry
    """
    clean_text = text.strip()
    
    if len(clean_text) < 5:
        return False
    
    # Pattern 1: Multiple dots followed by page numbers
    # Examples: "1.19 Class..........................1 - 37"
    #          "Introduction.......................5"
    dot_pattern = re.compile(r'.{3,}\.{5,}.{0,20}\d+(\s*-\s*\d+)?$')
    
    # Pattern 2: Chapter/section numbers with excessive dots/spaces
    # "1.1.3 Introduction . . . . . . . . . . . . . . . . . . . . . . . . 1 - 4"
    spaced_dot_pattern = re.compile(r'^\d+(\.\d+)+\s+.+(\s+\.){3,}.+\d+$')
    
    # Pattern 3: Text ending with "... page_num" format
    page_ref_pattern = re.compile(r'.+\.{3,}\s*\d+\s*$')
    
    # Pattern 4: Specific TOC formatting with dashes
    dash_pattern = re.compile(r'.+\.{5,}.+\d+\s*-\s*\d+$')
    
    # Pattern 5: Lines with excessive dots relative to content
    dot_count = clean_text.count('.')
    if len(clean_text) > 20 and dot_count > len(clean_text) * 0.25:
        return True
    
    # Check against all patterns
    if (dot_pattern.match(clean_text) or 
        spaced_dot_pattern.match(clean_text) or 
        page_ref_pattern.match(clean_text) or 
        dash_pattern.match(clean_text)):
        return True
    
    # Pattern 6: Contains typical TOC keywords with page references
    toc_keywords = ['table of contents', 'contents', 'index', 'chapter', 'section']
    lower_text = clean_text.lower()
    if any(keyword in lower_text for keyword in toc_keywords) and re.search(r'\d+$', clean_text):
        return True
    
    return False


def is_header_footer_noise(text: str, bbox: Tuple[float, float, float, float], page_height: float = 842) -> bool:
    """
    Detect headers, footers, and other noise based on position and content
    """
    x0, y0, x1, y1 = bbox
    
    # Header region (top 10% of page)
    if y0 < page_height * 0.1:
        return True
    
    # Footer region (bottom 10% of page)  
    if y1 > page_height * 0.9:
        return True
    
    # Page numbers (simple digits, optionally with common separators)
    if re.match(r'^[\s\-]*\d{1,4}[\s\-]*$', text.strip()):
        return True
    
    # Common header/footer patterns
    noise_patterns = [
        r'^\s*page\s+\d+\s*$',
        r'^\s*\d+\s*$',
        r'^\s*chapter\s+\d+\s*$',
        r'^\s*section\s+\d+\s*$',
        r'^\s*©.*\d{4}.*$',  # Copyright notices
        r'^\s*www\.',        # URLs
        r'^\s*http',         # URLs
        r'^\s*\d+\s*/\s*\d+\s*$',  # Page X/Y format
    ]
    
    lower_text = text.lower().strip()
    for pattern in noise_patterns:
        if re.match(pattern, lower_text):
            return True
    
    return False


def is_valid_heading(text: str, font_size: float, is_bold: bool, min_heading_size: float) -> bool:
    """
    Determine if a text block is a valid heading based on multiple criteria
    """
    clean_text = text.strip()
    
    # Basic length checks
    if len(clean_text) < 3 or len(clean_text) > 200:
        return False
    
    # Font size check
    if font_size < min_heading_size:
        return False
    
    # Heading regex patterns
    heading_patterns = [
        r'^\d+(\.\d+)*\.?\s+[A-Z][^,;:\n]*$',  # "1. Introduction", "2.1 Methods"
        r'^[A-Z][A-Z\s]{2,}$',                 # "INTRODUCTION", "RELATED WORK"
        r'^[A-Z][a-z]+(\s+[A-Z][a-z]*)*$',     # "Introduction", "Related Work"
        r'^(Abstract|Introduction|Conclusion|References|Acknowledgments?|Bibliography)$',  # Common sections
        r'^(Chapter|Section|Appendix)\s+\d+',  # "Chapter 1", "Section 2"
    ]
    
    # Check if text matches any heading pattern
    matches_pattern = any(re.match(pattern, clean_text) for pattern in heading_patterns)
    
    # Additional heuristics for headings
    words = clean_text.split()
    
    # Short phrases are more likely to be headings
    if len(words) <= 8 and matches_pattern:
        return True
    
    # Bold text with reasonable length
    if is_bold and 2 <= len(words) <= 10:
        return True
    
    # All caps short text
    if clean_text.isupper() and 2 <= len(words) <= 6:
        return True
    
    return matches_pattern


def calculate_font_thresholds(doc: fitz.Document) -> Tuple[float, float]:
    """
    Analyze document to determine font size thresholds for heading detection
    """
    all_font_sizes = []
    heading_candidates = []
    
    # First pass: collect all font sizes
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    size = span["size"]
                    
                    if not text or len(text) < 3:
                        continue
                    
                    all_font_sizes.append(size)
                    
                    # Check if this looks like a heading candidate
                    if (re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', text) or 
                        text.isupper() or 
                        bool(span["flags"] & 16)):  # Bold flag
                        heading_candidates.append(size)
    
    if not all_font_sizes:
        return 12.0, 10.0  # Default fallback
    
    # Calculate body text size (most common size)
    from collections import Counter
    size_counts = Counter(all_font_sizes)
    body_font_size = size_counts.most_common(1)[0][0]
    
    # Calculate heading threshold
    if heading_candidates:
        min_heading_size = min(heading_candidates)
    else:
        min_heading_size = body_font_size + 1  # At least 1pt larger than body
    
    return float(min_heading_size), float(body_font_size)


def extract_sections(pdf_path: str) -> List[Dict]:
    """
    Parse the PDF at pdf_path, segment into sections and subsections.
    Returns a list of dicts: {
      "document": filename,
      "page": int,
      "title": str, 
      "text": str
    }
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[ERROR] Could not open PDF {pdf_path}: {e}")
        return []
    
    sections = []
    current_section = None
    
    # Calculate font size thresholds
    min_heading_size, body_font_size = calculate_font_thresholds(doc)
    print(f"[DEBUG] Font thresholds - Heading: {min_heading_size:.1f}, Body: {body_font_size:.1f}")
    
    # Process each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_height = page.rect.height
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            # Process each line in the block
            for line in block["lines"]:
                line_text = ""
                max_font_size = 0
                is_bold = False
                line_bbox = None
                
                # Combine spans into a complete line
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text:
                        continue
                    
                    line_text += text + " "
                    max_font_size = max(max_font_size, span["size"])
                    is_bold = is_bold or bool(span["flags"] & 16)
                    
                    if line_bbox is None:
                        line_bbox = span["bbox"]
                    else:
                        # Expand bbox to include this span
                        x0, y0, x1, y1 = line_bbox
                        sx0, sy0, sx1, sy1 = span["bbox"]
                        line_bbox = (min(x0, sx0), min(y0, sy0), max(x1, sx1), max(y1, sy1))
                
                line_text = line_text.strip()
                if not line_text or not line_bbox:
                    continue
                
                # Filter out noise (headers, footers, page numbers)
                if is_header_footer_noise(line_text, line_bbox, page_height):
                    continue
                
                # Filter out table of contents entries
                if is_table_of_contents_entry(line_text):
                    print(f"[DEBUG] Filtered TOC entry: {line_text[:60]}...")
                    continue
                
                # Check if this line is a heading
                if is_valid_heading(line_text, max_font_size, is_bold, min_heading_size):
                    # Save previous section if exists
                    if current_section:
                        current_section["text"] = current_section["text"].strip()
                        if current_section["text"]:  # Only add sections with content
                            sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "document": pdf_path,
                        "page": page_num + 1,
                        "title": line_text,
                        "text": ""
                    }
                    print(f"[DEBUG] New section: {line_text}")
                
                elif current_section:
                    # Add to current section content
                    current_section["text"] += line_text + " "
    
    # Add final section
    if current_section:
        current_section["text"] = current_section["text"].strip()
        if current_section["text"]:
            sections.append(current_section)
    
    doc.close()
    
    # Post-processing: Remove very short sections (likely noise)
    filtered_sections = []
    for section in sections:
        if len(section["text"].split()) >= 10:  # At least 10 words of content
            filtered_sections.append(section)
        else:
            print(f"[DEBUG] Filtered short section: {section['title']}")
    
    print(f"[DEBUG] Extracted {len(filtered_sections)} valid sections from {pdf_path}")
    return filtered_sections


def extract_section_text_around_heading(page, heading_bbox, max_chars=2000):
    """
    Extract text content around a detected heading for better context
    """
    page_text = page.get_text()
    
    # Find the heading text in the page text
    heading_start = page_text.find(heading_bbox)
    if heading_start == -1:
        return ""
    
    # Extract text following the heading
    start_pos = heading_start + len(heading_bbox)
    end_pos = min(start_pos + max_chars, len(page_text))
    
    section_text = page_text[start_pos:end_pos].strip()
    
    # Clean up the text
    # Remove excessive whitespace
    section_text = re.sub(r'\s+', ' ', section_text)
    
    # Remove incomplete sentences at the end
    sentences = section_text.split('. ')
    if len(sentences) > 1:
        section_text = '. '.join(sentences[:-1]) + '.'
    
    return section_text


if __name__ == "__main__":
    # Test the parser
    import sys
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        sections = extract_sections(test_pdf)
        
        print(f"\n=== EXTRACTED SECTIONS ===")
        for i, section in enumerate(sections, 1):
            print(f"\n{i}. {section['title']} (Page {section['page']})")
            print(f"   Content: {section['text'][:100]}...")
    else:
        print("Usage: python parser.py <pdf_file>")
