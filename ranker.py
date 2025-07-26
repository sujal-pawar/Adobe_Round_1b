# ranker.py
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def rank_sections(sections, prompt_embedding, embedder, top_k=10, threshold=0.05):
    """
    sections: list of {"title", "text", ...}
    prompt_embedding: single vector
    embedder: Embedder instance
    Returns top_k sections by similarity >= threshold, each with score and rank.
    """
    print(f"[DEBUG] Number of sections received for ranking: {len(sections)}")
    texts = [s["title"] + " " + s["text"] for s in sections]
    embeddings = embedder.embed(texts)
    sims = cosine_similarity(embeddings, prompt_embedding.reshape(1, -1)).flatten()

    ranked = []
    for sec, score in zip(sections, sims):
        print(f"[DEBUG] Section title: '{sec.get('title')}' | Similarity score: {score}")
        if score >= threshold:
            sec_copy = sec.copy()
            sec_copy["score"] = float(score)
            ranked.append(sec_copy)

    ranked.sort(key=lambda x: x["score"], reverse=True)
    print(f"[DEBUG] Number of highlights after ranking: {len(ranked)}")
    return ranked[:top_k]
