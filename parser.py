import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
from collections import Counter

def is_table_of_contents_entry(text: str) -> bool:
    """Detect if a text block is a Table of Contents entry."""
    clean_text = text.strip()
    if len(clean_text) < 5:
        return False
    
    # Combined regex for various TOC patterns
    toc_patterns = [
        re.compile(r'.{3,}\.{5,}.{0,20}\d+(\s*-\s*\d+)?$'),  # "Title.........5"
        re.compile(r'^\d+(\.\d+)+\s+.+(\s+\.){3,}.+\d+$'),     # "1.1 Title . . . 5"
        re.compile(r'.+\s{3,}\d+\s*$'),                      # "Title      5"
    ]
    if any(p.search(clean_text) for p in toc_patterns):
        return True
    
    # Dot density check
    dot_count = clean_text.count('.')
    if len(clean_text) > 20 and dot_count / len(clean_text) > 0.25:
        return True
        
    return False

def is_header_footer_noise(bbox: Tuple[float, float, float, float], page_height: float) -> bool:
    """Detect headers and footers based on vertical position."""
    _, y0, _, y1 = bbox
    return y0 < page_height * 0.1 or y1 > page_height * 0.9

def is_valid_heading(text: str, font_size: float, is_bold: bool, min_heading_size: float, body_font_size: float) -> bool:
    """Determine if a text block is a valid heading."""
    clean_text = text.strip()
    if len(clean_text) < 3 or len(clean_text) > 200:
        return False
    
    # Must be larger than body text
    if font_size <= body_font_size:
        return False
        
    # Heuristic checks
    words = clean_text.split()
    if len(words) > 15: # Headings are typically short
        return False

    # Matches common heading formats (numbered, all caps, title case)
    if (re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', clean_text) or
        (clean_text.isupper() and len(words) > 1) or
        (clean_text.istitle() and len(words) > 1) or
        is_bold):
        return True
        
    return False

def calculate_font_thresholds(doc: fitz.Document) -> Tuple[float, float]:
    """Analyze document to determine font size thresholds."""
    sizes = [
        span["size"]
        for page in doc
        for block in page.get_text("dict")["blocks"]
        if "lines" in block
        for line in block["lines"]
        for span in line["spans"]
        if span["text"].strip()
    ]
    if not sizes:
        return 12.0, 10.0  # Fallback
        
    body_font_size = Counter(sizes).most_common(1)[0][0]
    min_heading_size = body_font_size + 0.5 # Slightly larger than body
    
    return float(min_heading_size), float(body_font_size)

# In parser.py, replace the entire function with this one:

# In parser.py, replace the entire function with this one:

def extract_sections(pdf_path: str) -> List[Dict]:
    """Parse the PDF, segmenting into sections while filtering noise."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        safe_e = str(e).encode('utf-8', 'ignore').decode('utf-8')
        safe_path = pdf_path.encode('utf-8', 'ignore').decode('utf-8')
        print(f"[ERROR] Could not open PDF {safe_path}: {safe_e}")
        return []
    
    sections = []
    current_section = None
    min_heading_size, body_font_size = calculate_font_thresholds(doc)
    
    # Unicode-safe print for thresholds
    print(f"[DEBUG] Font thresholds - Heading: {min_heading_size:.1f}, Body: {body_font_size:.1f}")
    
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        try:
            blocks = page.get_text("dict")["blocks"]
        except KeyError:
            continue # Skip pages with no text blocks
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            for line in block["lines"]:
                # --- START: Defensive checks for malformed data ---
                if not line.get("spans"):
                    continue # Skip lines with no spans
                    
                line_text = "".join(span.get("text", "") for span in line["spans"]).strip()
                if not line_text:
                    continue
                
                try:
                    max_font_size = max(span.get("size", 0) for span in line["spans"])
                    is_bold = any(span.get("flags", 0) & 16 for span in line["spans"])
                    line_bbox = line.get("bbox")
                except (ValueError, KeyError):
                    continue # Skip if essential span data is missing
                
                if not line_bbox:
                    continue
                # --- END: Defensive checks ---

                safe_line_text = line_text.encode('utf-8', 'ignore').decode('utf-8')

                if is_header_footer_noise(line_bbox, page_height) or is_table_of_contents_entry(line_text):
                    continue
                
                if is_valid_heading(line_text, max_font_size, is_bold, min_heading_size, body_font_size):
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        "document": pdf_path,
                        "page": page_num + 1,
                        "title": line_text,
                        "text": ""
                    }
                elif current_section:
                    current_section["text"] += line_text + " "
    
    if current_section:
        sections.append(current_section)
    
    doc.close()
    
    final_sections = [
        sec for sec in sections 
        if sec.get("text") and len(sec["text"].split()) >= 10
    ]
    
    safe_pdf_path = pdf_path.encode('utf-8', 'ignore').decode('utf-8')
    print(f"[DEBUG] Extracted {len(final_sections)} valid sections from {safe_pdf_path}")
    
    return final_sections

    """Parse the PDF, segmenting into sections while filtering noise."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        # Unicode-safe print for errors
        safe_e = str(e).encode('utf-8', 'ignore').decode('utf-8')
        safe_path = pdf_path.encode('utf-8', 'ignore').decode('utf-8')
        print(f"[ERROR] Could not open PDF {safe_path}: {safe_e}")
        return []
    
    sections = []
    current_section = None
    min_heading_size, body_font_size = calculate_font_thresholds(doc)
    
    print(f"[DEBUG] Font thresholds - Heading: {min_heading_size:.1f}, Body: {body_font_size:.1f}")
    
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        # --- THIS LINE IS FIXED ---
        # The 'flags' argument has been removed to ensure compatibility.
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            for line in block["lines"]:
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                if not line_text:
                    continue
                
                max_font_size = max(span["size"] for span in line["spans"])
                is_bold = any(span["flags"] & 16 for span in line["spans"])
                line_bbox = line["bbox"]
                
                # Unicode-safe print for debugging lines
                safe_line_text = line_text.encode('utf-8', 'ignore').decode('utf-8')

                if is_header_footer_noise(line_bbox, page_height) or is_table_of_contents_entry(line_text):
                    # print(f"[DEBUG] Filtered noise/TOC: {safe_line_text[:60]}...")
                    continue
                
                if is_valid_heading(line_text, max_font_size, is_bold, min_heading_size, body_font_size):
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        "document": pdf_path,
                        "page": page_num + 1,
                        "title": line_text,
                        "text": ""
                    }
                    #print(f"[DEBUG] New section: {safe_line_text}")
                elif current_section:
                    current_section["text"] += line_text + " "
    
    if current_section:
        sections.append(current_section)
    
    doc.close()
    
    # Final filtering of sections
    final_sections = [
        sec for sec in sections 
        if sec.get("text") and len(sec["text"].split()) >= 10
    ]
    
    # Unicode-safe print for final counts
    safe_pdf_path = pdf_path.encode('utf-8', 'ignore').decode('utf-8')
    print(f"[DEBUG] Extracted {len(final_sections)} valid sections from {safe_pdf_path}")
    
    return final_sections

    """Parse the PDF, segmenting into sections while filtering noise."""
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"[ERROR] Could not open PDF {pdf_path}: {e}")
        return []
    
    sections = []
    current_section = None
    min_heading_size, body_font_size = calculate_font_thresholds(doc)
    
    # --- Unicode-safe print for thresholds ---
    print(f"[DEBUG] Font thresholds - Heading: {min_heading_size:.1f}, Body: {body_font_size:.1f}".encode('utf-8', 'ignore').decode('utf-8'))
    
    for page_num, page in enumerate(doc):
        page_height = page.rect.height
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_INHIBIT_SPACES)["blocks"]
        
        for block in blocks:
            if "lines" not in block:
                continue
            
            for line in block["lines"]:
                line_text = "".join(span["text"] for span in line["spans"]).strip()
                if not line_text:
                    continue
                
                max_font_size = max(span["size"] for span in line["spans"])
                is_bold = any(span["flags"] & 16 for span in line["spans"])
                line_bbox = line["bbox"]
                
                # --- Unicode-safe print for debugging lines ---
                safe_line_text = line_text.encode('utf-8', 'ignore').decode('utf-8')

                if is_header_footer_noise(line_bbox, page_height) or is_table_of_contents_entry(line_text):
                    # print(f"[DEBUG] Filtered noise/TOC: {safe_line_text[:60]}...")
                    continue
                
                if is_valid_heading(line_text, max_font_size, is_bold, min_heading_size, body_font_size):
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        "document": pdf_path,
                        "page": page_num + 1,
                        "title": line_text,
                        "text": ""
                    }
                    #print(f"[DEBUG] New section: {safe_line_text}")
                elif current_section:
                    current_section["text"] += line_text + " "
    
    if current_section:
        sections.append(current_section)
    
    doc.close()
    
    # Final filtering of sections
    final_sections = [
        sec for sec in sections 
        if sec.get("text") and len(sec["text"].split()) >= 10
    ]
    
    # --- Unicode-safe print for final counts ---
    safe_pdf_path = pdf_path.encode('utf-8', 'ignore').decode('utf-8')
    print(f"[DEBUG] Extracted {len(final_sections)} valid sections from {safe_pdf_path}")
    
    return final_sections

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        sections = extract_sections(test_pdf)
        
        print("\n=== EXTRACTED SECTIONS ===")
        for i, section in enumerate(sections, 1):
            safe_title = section['title'].encode('utf-8', 'ignore').decode('utf-8')
            safe_content = section['text'].encode('utf-8', 'ignore').decode('utf-8')
            print(f"\n{i}. {safe_title} (Page {section['page']})")
            print(f"   Content: {safe_content[:100]}...")
    else:
        print("Usage: python parser.py <path_to_pdf>")

