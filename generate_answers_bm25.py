"""Quick answers generator using BM25-only (no Qdrant/Docker required)."""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    from openai import OpenAI
    from src.m1_chunking import load_documents, chunk_hierarchical
    from src.m2_search import BM25Search
    from src.m3_rerank import CrossEncoderReranker
    from config import OPENAI_API_KEY, RERANK_TOP_K

    print("Building BM25 index...")
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        _, children = chunk_hierarchical(doc["text"], metadata=doc["metadata"])
        for child in children:
            all_chunks.append({"text": child.text, "metadata": child.metadata})

    search = BM25Search()
    search.index(all_chunks)
    reranker = CrossEncoderReranker()
    client = OpenAI()

    with open("test_set_50q.json", encoding="utf-8") as f:
        test_set = json.load(f)

    answers = []
    t0 = time.time()
    for i, item in enumerate(test_set):
        results = search.search(item["question"], top_k=20)
        docs_list = [{"text": r.text, "score": r.score, "metadata": r.metadata} for r in results]
        reranked = reranker.rerank(item["question"], docs_list, top_k=RERANK_TOP_K)
        contexts = [r.text for r in reranked] if reranked else [r.text for r in results[:3]]

        ctx = "\n\n".join(contexts)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Trả lời CHỈ dựa trên context. Nếu không có → nói 'Không tìm thấy.'"},
                {"role": "user", "content": f"Context:\n{ctx}\n\nCâu hỏi: {item['question']}"},
            ],
        )
        answer = resp.choices[0].message.content
        answers.append({
            "id": item["id"],
            "distribution": item["distribution"],
            "question": item["question"],
            "answer": answer,
            "contexts": contexts,
            "ground_truth": item["ground_truth"],
        })
        if (i + 1) % 10 == 0:
            print(f"  [{i+1}/50] done ({time.time()-t0:.0f}s)")

    with open("answers_50q.json", "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)
    print(f"Saved answers_50q.json ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
