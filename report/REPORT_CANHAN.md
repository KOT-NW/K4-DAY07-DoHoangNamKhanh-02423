# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đỗ Hoàng Nam Khánh
**Nhóm:** K4-L3A (02423)
**Ngày:** 2026-09-19

> Nộp 1 bản / sinh viên. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
Hai đoạn văn bản có vector embedding cùng hướng — nghĩa là nội dung cùng chủ đề/ý nghĩa, không phụ thuộc độ dài văn bản.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên được mượn tối đa 3 cuốn trong 2 tuần."
- Câu B: "Mỗi sinh viên đại học chỉ được mượn 3 cuốn mỗi lượt kéo dài hai tuần."
- Tại sao tương đồng: khác từ vựng nhưng cùng ý nghĩa — embedding hiểu nghĩa chứ không so khớp từ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Học phí Điều dưỡng 349.650.000 một năm."
- Câu B: "Ký túc xá đóng cửa sau 23h đêm."
- Tại sao khác: một câu về tiền học, một câu về giờ giấc — vector gần trực giao.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
Cosine chỉ đo góc (hướng ngữ nghĩa), bỏ qua độ dài vector — hai văn bản cùng ý nhưng dài ngắn khác nhau vẫn giống nhau; Euclid bị ảnh hưởng bởi độ lớn vector nên phạt văn bản dài.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
Phép tính: `ceil((10000 − 50) / (500 − 50)) = ceil(9950 / 450) = ceil(22.11) = 23`.
Kiểm bằng code: `FixedSizeChunker(chunk_size=500, overlap=50).chunk('a'*10000)` → **23 chunks**.
**Đáp án: 23.**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
Tăng lên **25 chunks** (`ceil(9900/400)`). Overlap lớn giữ được liên kết ngữ cảnh qua ranh giới chunk (câu/số liệu bị cắt dở vẫn còn ở chunk sau), mỗi thông tin có nhiều hơn 1 cơ hội lọt top-k — đánh đổi bằng tốn thêm chunk/lưu trữ.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
Dùng regex lookbehind `(?<=[.!?])\s+` để tách tại khoảng trắng *sau* dấu câu mà vẫn giữ dấu câu trong chunk (split bằng `[.!?]\s+` sẽ nuốt mất dấu). Strip từng câu, gom N câu thành 1 chunk. Edge case đã biết: chữ viết tắt (`TS.`, `v.v.`) và số thập phân bị cắt sai — chấp nhận và ghi nhận thay vì giấu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
Thuật toán 2 chiều: (1) đệ quy xuống — thử separator theo thứ tự `\n\n → \n → ". " → " " → ""`, mảnh nào còn dài hơn `chunk_size` thì gọi lại `_split` với separator còn lại; (2) gom lên — nối các mảnh nhỏ liền kề tới sát `chunk_size` để tránh chunk vụn 5-10 ký tự. Base case: text rỗng → `[]`; ngắn hơn size → `[text]`; hết separator/`""` → cắt cứng theo `chunk_size` (test `separators=[]` đi qua nhánh này).

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
Chỉ dùng in-memory (`_use_chroma=False` cứng để tránh bẫy rẽ nhánh Chroma chưa cài đặt). `_make_record` copy metadata và ép có `metadata["doc_id"]` (fallback = `Document.id`) vì `delete_document` phụ thuộc vào nó; mỗi record giữ `{id, content, metadata, embedding}`. `_search_records` embed query, dot-product với mọi record (vector đã chuẩn hoá nên dot = cosine), sort giảm dần, trả `{content, score, metadata}` không kèm embedding để output sạch. `search` và `search_with_filter` dùng chung `_search_records` nên không lệch nhau.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
Lọc metadata **trước** rồi mới search (lấy top-k rồi mới lọc có thể còn 0 kết quả dù tài liệu hợp lệ vẫn tồn tại vì slot đã bị tài liệu sai chiếm). `filter=None` thì tương đương `search`. `delete_document` xóa mọi chunk có `metadata["doc_id"]` khớp, trả True/False theo có xóa được gì không.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
3 nhịp retrieve → prompt → `llm_fn`. Prompt đánh số chunk `[1][2][3]` kèm nguồn (`doc_id`), yêu cầu model trích dẫn số khi dùng thông tin (tiêu chí Source Traceability) và dặn chỉ dùng ngữ cảnh, không có thì nói rõ không tìm thấy. Store rỗng thì trả câu thông báo, không gọi LLM vô ích.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```
pytest tests/ -v → 42 passed in 0.09s (Python 3.12.10, pytest 9.1.1)
31 failed → 0 failed sau khi code xong; main.py chay end-to-end
voi PYTHONUTF8=1 (console Windows mac dinh ma hoa cp1252 nen can flag
nay khi in tieng Viet, khong phai loi code).
```

| Nhóm test | Kết quả |
|-----------|---------|
| ProjectStructure (2) + Interfaces (2) + FixedSize (7) | 11 passed (baseline) |
| SentenceChunker (4) + Recursive (4) + Similarity (4) + Compare (3) | 15 passed (CP3) |
| EmbeddingStore (8) + Filter (3) + Delete (3) + Agent (2) | 16 passed (CP4) |
| **Tổng** | **42 / 42** |

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Embed bằng `_mock_embed` rồi `compute_similarity` (mock băm MD5 nên không có ngữ nghĩa — số liệu chỉ để minh họa cơ chế):

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được mượn tối đa 3 cuốn trong 2 tuần. | Mỗi SV đại học chỉ được mượn 3 cuốn mỗi lượt kéo dài hai tuần. | cao | 0.0766 | Sai |
| 2 | Sinh viên được mượn tối đa 3 cuốn trong 2 tuần. | Giảng viên được mượn tối đa 5 cuốn trong 6 tháng. | thấp | -0.0688 | Đúng dấu nhưng sát 0 |
| 3 | Học phí Điều dưỡng 349.650.000 một năm. | KTX NEU phòng 4 người điều hòa 1.500.000 một tháng. | thấp | 0.1327 | Đúng (thấp) |
| 4 | Duy trì học bổng Full cần GPA từ 3.2. | Học bổng 100% yêu cầu GPA năm đạt 3.2 trở lên. | cao | 0.1634 | Sai (quá thấp) |
| 5 | Thư viện mở cửa 8h đến 21h thứ 2 đến thứ 6. | Ký túc xá đóng cửa sau 23h đêm. | thấp | -0.0946 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
Cặp 1 và 4 gây bất ngờ nhất: hai câu cùng nghĩa (viết lại) mà điểm mock chỉ 0.08-0.16, ngang với cặp khác nghĩa. Điều này chứng minh mock embedder (băm MD5 → số giả) không mã hoá ngữ nghĩa — muốn benchmark có ý nghĩa phải bật embedder thật (local đa ngữ). Với embedding thật, cặp cùng nghĩa phải gần 1.0.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chiến lược của tôi: `HeadingChunker` (chi tiết ở REPORT_NHOM mục 2). Chạy `bench.py` trên 8 file / 43 chunks.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Mượn sách SV (filter audience=student) | scholarship-maintain (sai); chunk SV đúng ở rank 3 (Gia han) | 0.297 | Một phần (top-3 có) | Agent-mock trích context rank 1 (sai do mock) |
| 2 | Mượn sách GV | library-borrow-student Dat truoc (sai section) | 0.344 | Sai section | Sai theo |
| 3 | Học phí 2026-2027 | library-borrow-faculty Thiet bi (sai) | 0.271 | Không (doc đúng ở rank 2) | Sai theo |
| 4 | GPA học bổng | dormitory-fees Gia phong (sai) | 0.374 | Không | Sai theo — failure case |
| 5 | KTX NEU | tuition-fees Tro cap (sai) | 0.363 | Không | Sai theo |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 1 / 5 (ở mức keyword; 3/5 ở mức doc_id — chênh lệch này chính là phát hiện "đúng tài liệu ≠ đúng chunk").

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
Chưa có nhóm khác để so; bài học lớn nhất là từ chính A/B của mình: cùng 1 câu hỏi, thêm `metadata_filter` biến 0 chunk đúng thành 1 chunk đúng — thiết kế corpus (tách file theo audience) quan trọng không kém thuật toán chunking.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 9 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 4 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 7 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |
