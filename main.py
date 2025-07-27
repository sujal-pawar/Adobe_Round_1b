import argparse
import json
import time
from datetime import datetime
from parser import extract_sections
from embedder import Embedder
from ranker import rank_sections
from refiner import refine_subsections

def convert_rank_to_relevance_score(rank, max_rank=5):
    """Convert rank (1=best) to relevance score (1.0=best)"""
    return round(1.0 - ((rank - 1) / max_rank), 2)

def main(pdf_list, persona, job, output_json):
    start = time.time()
    embedder = Embedder()
    prompt = f"{persona} {job}"
    prompt_emb = embedder.embed([prompt])[0]

    all_sections = []
    for pdf in pdf_list:
        secs = extract_sections(pdf)
        print(f"[DEBUG] {pdf}: {len(secs)} sections extracted")
        all_sections.extend(secs)
    print(f"[DEBUG] Total sections from all PDFs: {len(all_sections)}")

    extracted_sections = []
    subsection_analysis = []
    
    top_k_per_pdf = 5
    
    for pdf in pdf_list:
        # --- START: Add try...except block to handle problematic PDFs ---
        try:
            pdf_sections = [sec for sec in all_sections if sec["document"] == pdf]
            if not pdf_sections:
                print(f"[DEBUG] No sections to rank for {pdf}, skipping.")
                continue
                
            ranked_secs = rank_sections(pdf_sections, prompt_emb, embedder, top_k=top_k_per_pdf)
            print(f"[DEBUG] Ranked sections for {pdf}: {len(ranked_secs)}")
            
            for idx, sec in enumerate(ranked_secs, start=1):
                extracted_sections.append({
                    "document": sec["document"],
                    "page": sec["page"],
                    "section_title": sec["title"],
                    "importance_rank": idx
                })
                
                subs = refine_subsections(sec, prompt_emb, embedder)
                
                for sub in subs:
                    subsection_analysis.append({
                        "document": sec["document"],
                        "page": sec["page"],
                        "refined_text": sub["refined_text"],
                        "relevance_score": convert_rank_to_relevance_score(sub["rank"])
                    })
        except Exception as e:
            # Gracefully handle the error and continue to the next document
            safe_pdf_path = pdf.encode('utf-8', 'ignore').decode('utf-8')
            print(f"⚠️ [WARNING] Failed to process document '{safe_pdf_path}'. Error: {e}. Skipping this document.")
            continue
        # --- END: try...except block ---

    metadata = {
        "input_documents": pdf_list,
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.now().isoformat() + "Z"
    }

    output = {
        "metadata": metadata,
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"[INFO] Processing completed in {time.time() - start:.2f}s")
    print(f"[INFO] Output saved to {output_json}")
    print(f"[INFO] Extracted {len(extracted_sections)} sections and {len(subsection_analysis)} subsections")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Section Relevance Extraction")
    parser.add_argument("--pdfs", nargs="+", required=True, help="List of PDF files")
    parser.add_argument("--persona", type=str, required=True, help="User persona description")
    parser.add_argument("--job", type=str, required=True, help="Job to be done")
    parser.add_argument("--output", type=str, required=True, help="Output JSON path")
    args = parser.parse_args()

    main(args.pdfs, args.persona, args.job, args.output)
