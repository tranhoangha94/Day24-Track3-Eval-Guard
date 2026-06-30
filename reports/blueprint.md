# CI/CD Blueprint: RAG Eval + Guardrail Stack

**Sinh viên:** Lab 24 Student  
**Ngày:** 30/06/2026

---

## Guard Stack Architecture

```
User Input
    │
    ▼ (~45ms P95)
[Presidio PII Scan]
    │ block if: VN_CCCD / VN_PHONE / EMAIL detected
    │ action:   return 400 + "PII detected in query"
    ▼ (~2364ms P95)
[NeMo Input Rail]
    │ block if: off-topic / jailbreak / prompt injection
    │ action:   return 503 + refuse message
    ▼
[RAG Pipeline (Day 18)]
    │ M1 Chunk → M2 Search → M3 Rerank → GPT-4o-mini
    ▼
[NeMo Output Rail]
    │ flag if:  PII in response / sensitive content
    │ action:   replace with safe response
    ▼
User Response
```

---

## Latency Budget

| Layer | P50 (ms) | P95 (ms) | P99 (ms) | Budget |
|---|---|---|---|---|
| Presidio PII | 14.37 | 45.15 | 45.15 | <10ms |
| NeMo Input Rail | 0.02 | 2364.07 | 2364.07 | <300ms |
| RAG Pipeline | ~800 | ~1500 | ~2000 | <2000ms |
| NeMo Output Rail | ~200 | ~400 | ~500 | <300ms |
| **Total Guard** | 18.9 | **2380.75** | 2380.75 | **<500ms** |

**Budget OK?** [x] No  
**Comment:** NeMo Input Rail là bottleneck chính (~2.3s P95) do mỗi request gọi LLM API. Tối ưu: cache rails instance, dùng rule-based pre-filter (đã implement) trước NeMo để giảm số lần gọi LLM, hoặc chuyển sang model nhẹ hơn / local classifier.

---

## CI/CD Gates (phải pass trước khi merge to main)

```yaml
# .github/workflows/rag_eval.yml
- name: RAGAS Quality Gate
  run: python src/phase_a_ragas.py
  env:
    MIN_FAITHFULNESS: 0.75
    MIN_AVG_SCORE: 0.65

- name: Guardrail Gate
  run: pytest tests/test_phase_c.py -k "test_adversarial_suite_pass_rate"
  # phải ≥ 15/20 (75%)

- name: Latency Gate
  run: python -c "from src.phase_c_guard import measure_p95_latency; ..."
  # P95 total < 500ms
```

---

## Monitoring Dashboard (production)

| Metric | Alert Threshold | Action |
|---|---|---|
| RAGAS faithfulness (daily sample) | < 0.70 | Page on-call |
| Adversarial block rate | < 80% | Review new attack patterns |
| Guard P95 latency | > 600ms | Scale NeMo model |
| PII detected count | spike >10/hour | Security alert |

---

## Kết quả thực tế từ Lab

| | Kết quả |
|---|---|
| RAGAS avg_score (50q) | 0.78 (factual: 0.89, multi_hop: 0.71, adversarial: 0.74) |
| Worst metric | faithfulness (avg 0.70) |
| Dominant failure distribution | factual / multi_hop (tied) |
| Cohen's κ | 0.0 |
| Adversarial pass rate | 20 / 20 |
| Guard P95 latency | 2380.75 ms |

---

## Nhận xét & Cải tiến

Guard stack hoạt động tốt về mặt bảo mật: Presidio chặn PII nhanh (<50ms), rule-based + NeMo chặn 100% adversarial inputs. RAGAS eval giúp xác định điểm yếu theo distribution (đặc biệt adversarial và multi-hop). Điểm cần cải thiện: latency NeMo vượt budget production, và LLM judge có verbosity bias cao (70%) khi so với baseline ngắn. Trong production thực tế, nên thêm rule-based layer trước NeMo (đã làm), monitor RAGAS hàng ngày trên sample, và dùng swap-and-average cho judge để giảm position bias.
