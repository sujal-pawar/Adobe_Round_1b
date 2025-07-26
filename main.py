# main.py
import argparse
import json
import time
from parser import extract_sections
from embedder import Embedder
from ranker import rank_sections
from refiner import refine_subsections

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

    highlights = []
    top_k_per_pdf = 5  # Change this value for more/fewer highlights per PDF
    for pdf in pdf_list:
        pdf_sections = [sec for sec in all_sections if sec["document"] == pdf]
        if not pdf_sections:
            print(f"[DEBUG] No sections to rank for {pdf}, skipping.")
            continue
        ranked_secs = rank_sections(pdf_sections, prompt_emb, embedder, top_k=top_k_per_pdf)
        print(f"[DEBUG] Ranked sections for {pdf}: {len(ranked_secs)}")
        for idx, sec in enumerate(ranked_secs, start=1):
            subs = refine_subsections(sec, prompt_emb, embedder)
            highlights.append({
                "document": sec["document"],
                "page": sec["page"],
                "title": sec["title"],
                "rank": idx,
                "subsections": [
                    {
                        "document": sec["document"],
                        "page": sec["page"],
                        "title": None,
                        "rank": sub["rank"],
                        "refined_text": sub["refined_text"]
                    } for sub in subs
                ]
            })

    metadata = {
        "documents": pdf_list,
        "persona": persona,
        "job": job,
        "processing_time": f"{time.time() - start:.2f}s"
    }

    output = {
        "metadata": metadata,
        "highlights": highlights
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Section Relevance Extraction")
    parser.add_argument("--pdfs", nargs="+", required=True, help="List of PDF files")
    parser.add_argument("--persona", type=str, required=True, help="User persona description")
    parser.add_argument("--job", type=str, required=True, help="Job to be done")
    parser.add_argument("--output", type=str, required=True, help="Output JSON path")
    args = parser.parse_args()

    main(args.pdfs, args.persona, args.job, args.output)
