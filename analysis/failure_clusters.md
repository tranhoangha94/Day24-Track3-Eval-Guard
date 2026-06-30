# Failure Cluster Analysis — Phase A

**Sinh viên:** Lab 24 Student  
**Ngày:** 30/06/2026

---

## 1. Aggregate RAGAS Scores theo Distribution

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 0.975 | 0.413 | 0.700 |
| answer_relevancy | 0.834 | 0.627 | 0.596 |
| context_precision | 0.958 | 0.983 | 0.967 |
| context_recall | 0.800 | 0.829 | 0.683 |
| **avg_score** | **0.892** | **0.713** | **0.737** |

---

## 2. Bottom 10 Questions

| Rank | Distribution | Question | avg_score | worst_metric |
|---|---|---|---|---|
| 1 | adversarial | Bao lâu phải đổi mật khẩu một lần? | 0.375 | faithfulness |
| 2 | adversarial | Nhân viên thử việc có được nghỉ phép năm không? | 0.375 | faithfulness |
| 3 | multi_hop | Manager 12 năm: phụ cấp + phép năm v2024 | 0.375 | faithfulness |
| 4 | adversarial | VPN cá nhân (NordVPN) khi WFH? | 0.417 | faithfulness |
| 5 | multi_hop | Senior 9 năm: phép + lương | 0.483 | answer_relevancy |
| 6 | multi_hop | So sánh mật khẩu v1.0 vs v2.0 | 0.500 | faithfulness |
| 7 | multi_hop | Tạm ứng 8 triệu + phí phạt quá hạn | 0.500 | faithfulness |
| 8 | factual | Mua thiết bị 55 triệu — ai phê duyệt? | 0.536 | context_recall |
| 9 | multi_hop | So sánh bảo hiểm thử việc vs chính thức | 0.563 | answer_relevancy |
| 10 | factual | Bảo hiểm PVI hạn mức bao nhiêu? | 0.591 | context_recall |

---

## 3. Failure Cluster Matrix

| worst_metric | factual | multi_hop | adversarial | Total |
|---|---|---|---|---|
| faithfulness | 0 | 15 | 3 | 18 |
| answer_relevancy | 13 | 4 | 1 | 18 |
| context_precision | 1 | 0 | 0 | 1 |
| context_recall | 6 | 1 | 6 | 13 |

---

## 4. Dominant Failure Analysis

**Dominant distribution:** factual (tied với multi_hop, 20 failures mỗi loại)  
**Dominant metric:** faithfulness (18/50 câu có worst_metric = faithfulness)

**Lý do phân tích:**

Pipeline yếu nhất ở **faithfulness** — LLM thường hallucinate khi cần kết hợp nhiều tài liệu (multi-hop) hoặc khi gặp câu hỏi bẫy (adversarial). Multi-hop có faithfulness trung bình chỉ 0.41 vì cần tính toán/suy luận qua nhiều policy. Adversarial có 3/10 câu worst ở faithfulness (version conflicts mật khẩu, VPN). Factual có answer_relevancy thấp ở nhiều câu do trả lời không đủ chi tiết dù context recall tốt.

---

## 5. Suggested Fixes

| Metric yếu | Root cause | Suggested fix |
|---|---|---|
| faithfulness | LLM hallucinating trên multi-hop/adversarial | Tighten system prompt, lower temperature, cite sources |
| context_recall | Missing relevant chunks (factual) | Improve chunking, thêm metadata filter version |
| context_precision | Too many irrelevant chunks | Đã tốt (0.96+) — giữ reranking |
| answer_relevancy | Answer không khớp câu hỏi đầy đủ | Cải thiện prompt template, yêu cầu trả lời từng phần |

---

## 6. Nhận xét về Adversarial Distribution

Adversarial avg_score (0.737) thấp hơn factual (0.892) nhưng cao hơn multi_hop (0.713). Pipeline bị nhầm bởi version conflicts: Q44 (mật khẩu v1 vs v2), Q50 (VPN cá nhân bị cho phép). 4/10 bottom-10 là adversarial — đúng kỳ vọng stress-test. Cần metadata filter để ưu tiên policy version mới nhất (v2024, v2.0).
