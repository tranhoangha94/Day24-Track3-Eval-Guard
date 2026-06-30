# LLM Judge Bias Report — Phase B

**Sinh viên:** Lab 24 Student  
**Ngày:** 30/06/2026  
**Judge model:** gpt-4o-mini

---

## 1. Pairwise Judge Results

| # | Question (tóm tắt) | Winner | Reasoning tóm tắt |
|---|---|---|---|
| 1 | Nghỉ phép khi kết hôn | A | Answer A chính xác theo chính sách |
| 2 | Mua thiết bị 55 triệu | A | Answer A có thông tin cụ thể hơn baseline |
| 3 | Thưởng Tết tối thiểu | A | Answer A đúng và đầy đủ |
| 4 | Senior 9 năm: phép + lương | A | Answer A tính đúng cả hai phần |
| 5 | Hoàn trả khóa học 25 triệu | A | Answer A trả lời đúng chính sách |
| 6 | Tạm ứng 8 triệu + phí phạt | A | Answer A có chi tiết hơn |
| 7 | Manager 12 năm: phụ cấp + phép | A | Answer A đầy đủ |
| 8 | Số ngày phép năm | A | Answer A có số liệu cụ thể |
| 9 | Thử việc có nghỉ phép? | A | Answer A trả lời đúng |
| 10 | VPN cá nhân khi WFH | A | Answer A có nội dung (dù sai fact) |

---

## 2. Swap-and-Average Results

| # | Pass 1 Winner | Pass 2 Winner | Final | Position Consistent? |
|---|---|---|---|---|
| 1 | A | A | A | Yes |
| 2 | A | A | A | Yes |
| 3 | A | A | A | Yes |
| 4 | A | A | A | Yes |
| 5 | A | A | A | Yes |
| 6 | A | A | A | Yes |
| 7 | A | A | A | Yes |
| 8 | A | A | A | Yes |
| 9 | A | A | A | Yes |
| 10 | A | A | A | Yes |

**Position bias rate:** 0% (= 0/10 case NOT consistent)

---

## 3. Cohen's κ Analysis

**Human labels:** `human_labels_10q.json` (10 câu, 5 label=1, 5 label=0)  
**Judge labels:** So sánh model_answer vs baseline "Tôi không có thông tin..."

| Question ID | Human Label | Judge Label | Agree? |
|---|---|---|---|
| 1 | 1 | 1 | Yes |
| 5 | 0 | 1 | No |
| 12 | 1 | 1 | Yes |
| 21 | 1 | 1 | Yes |
| 23 | 1 | 1 | Yes |
| 29 | 0 | 1 | No |
| 33 | 1 | 1 | Yes |
| 41 | 0 | 1 | No |
| 46 | 1 | 1 | Yes |
| 50 | 0 | 1 | No |

**Cohen's κ:** 0.0  
**Interpretation:** poor — judge luôn chọn model answer (A) vì baseline quá ngắn, không phản ánh chất lượng thực tế

---

## 4. Verbosity Bias

Trong các case có winner rõ ràng (không phải tie):
- A thắng + A dài hơn B: 7 / 10 cases
- B thắng + B dài hơn A: 0 / 10 cases  
- **Verbosity bias rate:** 70%

**Kết luận:** LLM có xu hướng mạnh chọn answer dài hơn (70%), kể cả khi answer dài nhưng sai fact (Q41, Q50). Đây là vấn đề nghiêm trọng khi dùng judge làm quality gate.

---

## 5. Nhận xét chung

κ = 0.0 — LLM judge chưa đáng tin khi so với human labels vì baseline comparison quá đơn giản. Position bias thấp (0%) nhờ swap-and-average ổn định. Verbosity bias cao (70%) — judge ưu tiên độ dài hơn độ chính xác. Swap-and-average giúp giảm position bias nhưng không giải quyết verbosity bias. Trong production: nên dùng judge với rubric chi tiết + ground truth, không so với baseline ngắn; kết hợp RAGAS metrics thay vì chỉ dựa vào pairwise judge.
