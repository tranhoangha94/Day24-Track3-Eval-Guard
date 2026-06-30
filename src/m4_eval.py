from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import math
import os
import sys
import json
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run RAGAS evaluation."""
    # TODO: Implement RAGAS evaluation
    # 1. Wrap trong try/except — RAGAS cần OPENAI_API_KEY và Python 3.11+.
    # 2. from ragas import evaluate
    #    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    #    from datasets import Dataset
    # 3. dataset = Dataset.from_dict({
    #        "question": questions, "answer": answers,
    #        "contexts": contexts, "ground_truth": ground_truths,
    #    })
    # 4. result = evaluate(dataset, metrics=[faithfulness, answer_relevancy,
    #                                        context_precision, context_recall])
    # 5. df = result.to_pandas()
    # 6. per_question = [EvalResult(...) for _, row in df.iterrows()]
    # 7. Return {"faithfulness": ..., "answer_relevancy": ...,
    #            "context_precision": ..., "context_recall": ..., "per_question": [...]}
    zeros = {
        "faithfulness": 0.0,
        "answer_relevancy": 0.0,
        "context_precision": 0.0,
        "context_recall": 0.0,
        "per_question": [],
    }
    try:
        from dotenv import load_dotenv
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from datasets import Dataset

        load_dotenv()

        dataset = Dataset.from_dict({
            "question": questions, "answer": answers,
            "contexts": contexts, "ground_truth": ground_truths,
        })
        result = evaluate(dataset, metrics=[faithfulness, answer_relevancy,
                                            context_precision, context_recall])
        df = result.to_pandas()

        def _safe_float(value) -> float:
            try:
                number = float(value)
            except (TypeError, ValueError):
                return 0.0
            return 0.0 if math.isnan(number) else number

        per_question = [
            EvalResult(
                question=row["question"],
                answer=row["answer"],
                contexts=row["contexts"],
                ground_truth=row["ground_truth"],
                faithfulness=_safe_float(row.get("faithfulness", 0.0)),
                answer_relevancy=_safe_float(row.get("answer_relevancy", 0.0)),
                context_precision=_safe_float(row.get("context_precision", 0.0)),
                context_recall=_safe_float(row.get("context_recall", 0.0)),
            )
            for _, row in df.iterrows()
        ]
        return {
            "faithfulness": _safe_float(df["faithfulness"].mean()) if "faithfulness" in df.columns else 0.0,
            "answer_relevancy": _safe_float(df["answer_relevancy"].mean()) if "answer_relevancy" in df.columns else 0.0,
            "context_precision": _safe_float(df["context_precision"].mean()) if "context_precision" in df.columns else 0.0,
            "context_recall": _safe_float(df["context_recall"].mean()) if "context_recall" in df.columns else 0.0,
            "per_question": per_question,
        }
    except Exception as e:
        print(f"  ⚠️  RAGAS evaluation failed: {e}")
        return zeros
    # return {"faithfulness": 0.0, "answer_relevancy": 0.0,
    #         "context_precision": 0.0, "context_recall": 0.0, "per_question": []}


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    # TODO: Implement failure analysis
    # 1. diagnostic_tree = {
    #        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
    #        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
    #        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    #        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
    #    }
    # 2. For each EvalResult: compute avg of 4 metrics, find worst_metric
    # 3. Sort by avg ascending → take bottom_n
    # 4. Return [{"question": ..., "worst_metric": ..., "score": ...,
    #             "diagnosis": ..., "suggested_fix": ...}]
    # return []
    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
    }

    analyzed = []
    for item in eval_results:
        metrics = {
            "faithfulness": item.faithfulness,
            "answer_relevancy": item.answer_relevancy,
            "context_precision": item.context_precision,
            "context_recall": item.context_recall,
        }
        avg_score = sum(metrics.values()) / len(metrics)
        worst_metric = min(metrics, key=metrics.get)
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        analyzed.append({
            "question": item.question,
            "worst_metric": worst_metric,
            "score": avg_score,
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })

    analyzed.sort(key=lambda row: row["score"])
    return analyzed[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
