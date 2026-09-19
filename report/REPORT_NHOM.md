# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** K4-L3A (1 thành viên)
**Thành viên:** Đỗ Hoàng Nam Khánh — 02423
**Ngày:** 2026-09-19

> Nộp 1 bản / nhóm. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Dịch vụ / quy định đại học: thư viện, học phí, học bổng, ký túc xá (đúng ràng buộc K4-L3A).

**Tại sao nhóm chọn chủ đề này?**
Chủ đề này có văn bản quy định biên soạn theo mục rõ ràng (phù hợp thử chunking theo heading), số liệu cụ thể để làm gold answer (số cuốn, số tháng, VND, GPA, giờ giấc), và có cặp tài liệu cùng từ vựng nhưng khác đối tượng (SV vs GV) để chứng minh giá trị của metadata filter. Nguồn toàn trang công khai của các trường (VinUni, HUST, NEU), đã làm sạch menu/footer.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|--------------------|----------------------|----------|-----------------|
| 1 | library-borrow-student | https://library.vinuni.edu.vn/services/borrow-and-request/undergraduate-and-staff/ | 2026-09-19 / not-stated | 1296 | audience=student, department=library, category=borrowing, language=vi |
| 2 | library-borrow-faculty | https://library.vinuni.edu.vn/services/borrow-and-request/graduate-faculty-and-instructors/ | 2026-09-19 / not-stated | 1379 | audience=faculty, department=library, category=borrowing, language=vi |
| 3 | library-policy-access | https://policy.vinuni.edu.vn/all-policies/library-policies-for-users/ | 2026-09-19 / 2025-07-09 | 1923 | audience=all, department=library, category=policy, language=vi |
| 4 | tuition-fees-2026 | https://admissions.vinuni.edu.vn/tuition-fee/undergraduate/ | 2026-09-19 / 2026-07-01 | 1294 | audience=all, department=finance, category=tuition, language=vi |
| 5 | scholarship-maintain | https://policy.vinuni.edu.vn/all-policies/criteria-to-maintain-the-entry-scholarship-and-financial-aid-support/ | 2026-09-19 / 2024-11-21 | 1457 | audience=student, department=student-affairs, category=scholarship, language=vi |
| 6 | dormitory-fees | https://policy.vinuni.edu.vn/all-policies/financial-regulations-and-tariff-for-student-2/ | 2026-09-19 / 2025-04-25 | 1446 | audience=student, department=student-affairs, category=housing, language=vi |
| 7 | hust-ktx-gioi-thieu | https://hust.edu.vn/vi/sinh-vien/sinh-vien-hien-tai/ky-tuc-xa-51010.html | 2026-09-19 / 2016-07-11 | 1446 | audience=student, department=student-affairs, category=housing, language=vi |
| 8 | neu-ktx-1001 | https://fbm.neu.edu.vn/1001-su-that-ve-ki-tuc-xa-truong-dai-hoc-kinh-te-quoc-dan/ | 2026-09-19 / 2021-08-05 | 1660 | audience=student, department=student-affairs, category=housing, language=vi |

File `vnu.edu.vn` / `tuyensinh.vnu.edu.vn` bị loại: crawler từ chối vì không verify được `robots.txt` (lỗi SSL), đúng luật lab nên đổi sang HUST/NEU (robots cho phép, đã crawl thử thành công qua `scripts/fetch_public_pages.py`). File `policy.vinuni.edu.vn` cũng bị `disallowed by robots.txt` nên phần VinUni là chép tay phần công khai được phép dùng và đã làm sạch.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|--------------------------------------------|
| audience | enum | student / faculty / all | Tách SV vs GV cùng chủ đề mượn sách (3 cuốn/2 tuần vs 5 cuốn/6 tháng); Q1 bắt buộc filter mới đúng |
| department | string | library / finance / student-affairs | Lọc theo đơn vị quản lý khi câu hỏi thuộc nghiệp vụ cụ thể |
| category | string | borrowing / tuition / scholarship / housing / policy | Lọc theo loại quy định, tránh lẫn học phí với KTX |
| language | string | vi | Sẵn sàng mở rộng corpus song ngữ |
| source_url / retrieved_at / document_version | string/date | URL gốc, 2026-09-19, 2025-07-09… | Truy vết nguồn, kiểm tra độ mới; version `not-stated` khi nguồn không nêu, không bịa |

Trang thư viện gộp hạn mức SV và GV nên đã tách thành 2 file riêng — nếu để chung 1 file `audience: all` thì filter không có gì để lọc.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` (chunk_size=500):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------------------|----------------|-------------------|--------------------------|
| library-policy-access | FixedSizeChunker (`fixed_size`) | 4 | 446.0 | Trung bình — cắt cứng giữa câu |
| library-policy-access | SentenceChunker (`by_sentences`) | 8 | 202.6 | Tốt ở cấp câu, nhưng vụn, mất cấu trúc mục |
| library-policy-access | RecursiveChunker (`recursive`) | 4 | 407.0 | Khá — ưu tiên ranh giới lớn trước |
| neu-ktx-1001 | FixedSizeChunker (`fixed_size`) | 3 | 483.0 | Trung bình |
| neu-ktx-1001 | SentenceChunker (`by_sentences`) | 6 | 223.3 | Vụn, giá phòng bị tách khỏi loại phòng |
| neu-ktx-1001 | RecursiveChunker (`recursive`) | 4 | 335.8 | Khá |

Nhận xét: `by_sentences` sinh nhiều chunk nhất, ngắn nhất (~200-220 ký tự) — dễ mất ngữ cảnh mục; `fixed_size`/`recursive` ít chunk (3-4), dài (~330-480). Toàn corpus 8 file với HeadingChunker ra 43 chunks (~5.4/file).

### Chiến lược của từng thành viên

**Thành viên 1 — Đỗ Hoàng Nam Khánh (02423)**
- **Loại chiến lược:** custom `HeadingChunker` (chunk theo heading/section, section dài hạ xuống Recursive, gắn lại tiêu đề vào mảnh con).
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy định được biên soạn theo mục (`## Gia han`, `## Gia phong`…), mỗi mục là đơn vị ngữ nghĩa trọn vẹn do người soạn chia sẵn. Tách trước mỗi dòng heading giữ được trọn ý của mục; gắn lại tiêu đề vào mảnh con tránh mất ngữ cảnh "đây là mục nói về cái gì".
- **Code snippet (nếu custom):**
```python
class HeadingChunker:
    def __init__(self, max_len: int = 600) -> None:
        self.max_len = max_len
        self._fallback = RecursiveChunker(chunk_size=max_len)

    def chunk(self, text: str) -> list[str]:
        # Tach truoc moi dong heading ##.., moi section 1 chunk;
        # section dai hon max_len thi cat nho bang Recursive
        # va gan lai tieu de vao tung manh con.
        ...
```

*(Nhóm 1 người nên cột so sánh dưới dùng 3 baseline built-in làm đối chứng thay cho thành viên 2/3.)*

### So Sánh Giữa Các Thành Viên

| Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------------------|----------------------|-----------|----------|
| Heading (custom) | — (đo bằng mock nên chỉ so coherence) | Giữ trọn mục, chunk có tiêu đề, truy vết tốt | Mục quá dài vẫn phải cắt; mục ngắn gây chunk nhỏ |
| FixedSize | — | Đơn giản, đều, có overlap | Cắt giữa câu/mục, lẫn số liệu |
| Recursive | — | Ưu tiên ranh giới lớn, ít vụn | Vẫn có thể tách giá khỏi loại phòng nếu thiếu overlap |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
Heading tốt nhất cho corpus quy định vì đơn vị ngữ nghĩa đã có sẵn trong cấu trúc mục của người soạn — chunk trùng với mục nên vừa mạch lạc vừa dễ truy vết về đúng điều khoản. FixedSize chỉ nên dùng khi văn bản không có cấu trúc.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-----------------|--------------------------------|---------------------------|
| 1 | Tôi là sinh viên, mượn sách thư viện được mấy cuốn, bao lâu, gia hạn thế nào? (cần `filter audience=student`) | SV: tối đa 3 cuốn, mỗi cuốn 2 tuần, gia hạn 1 lần thêm 1 tuần | `library-borrow-student` mục Gia han |
| 2 | Giảng viên VinUni mượn sách được mấy cuốn và bao lâu? | GV: tối đa 5 cuốn, tối đa 6 tháng | `library-borrow-faculty` mục The muon |
| 3 | Học phí 2026-2027 của Điều dưỡng và các ngành cử nhân khác, có trợ cấp gì? | Điều dưỡng 349.650.000/năm; các cử nhân khác 815.850.000/năm; trợ cấp 35% Vingroup | `tuition-fees-2026` mục Bieu phi + Tro cap |
| 4 | Duy trì học bổng Full/100% cần GPA bao nhiêu, học bổng 50-90% cần bao nhiêu? | Full/100%: GPA năm từ 3.2; 50-90%: GPA năm từ 2.5; kèm E.X.C.E.L và kỷ luật tốt | `scholarship-maintain` mục Hoc bong Full / 50-90% |
| 5 | KTX NEU phòng 4 người có điều hòa giá bao nhiêu, giờ giới nghiêm và đăng ký thế nào? | 1.500.000/người/tháng; giới nghiêm 23h (T7-CN 23h30); 2 ảnh 3x4 + cọc 5 tháng tại nhà 5 | `neu-ktx-1001` mục Gia phong / Gio giac / Dang ky |

### Tổng hợp chất lượng truy xuất của nhóm

Chạy `bench.py` (HeadingChunker, mock embedder — không có ngữ nghĩa, số liệu bị chi phối bởi mock):

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|--------------------------------|---------------------------------|---------|
| 1 | Mượn sách SV | heading + filter | Có (rank 3, chunk Gia han) với filter; không filter thì mất | A/B: có filter keyword-hit 1/3, không filter 0/3 |
| 2 | Mượn sách GV | — (mock nhiễu) | Có doc đúng ở rank 3 nhưng sai section (Dat truoc thay vì The muon) | Đúng tài liệu ≠ đúng chunk chứa đáp án |
| 3 | Học phí | — (mock nhiễu) | Có doc đúng ở rank 2 nhưng keyword-hit 0/3 | Chunk Bieu phi không lọt top-3 |
| 4 | Học bổng | — (mock nhiễu) | Không — top-1 là dormitory-fees (score 0.374) | Failure case chính (xem dưới) |
| 5 | KTX NEU | — (mock nhiễu) | Không — top-3 toàn tuition/library/scholarship | Mock đo ký tự, không đo nghĩa |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
Có, ở Q1. Cùng câu hỏi mượn sách, corpus có 2 tài liệu cùng từ vựng nhưng khác đối tượng và khác đáp án (SV 3 cuốn/2 tuần vs GV 5 cuốn/6 tháng). Chạy không filter, top-3 không có chunk SV nào; chạy `filter audience=student`, chunk Gia han của SV lọt top-3. Đây là bằng chứng filter có việc thật — nhờ đã tách file theo audience từ đầu.

### Phân tích lỗi (Failure Analysis)

**Câu hỏi hỏng:** Q4 (GPA duy trì học bổng Full/100%).
**Vì sao:** Top-1 là `dormitory-fees` (chunk Gia phong, score 0.374) dù hỏi về học bổng — cosine trên mock embedding đo độ giống ký tự/chủ đề chung ("sinh viên", số tiền VND), không đo mật độ thông tin trả lời được. Chunk đúng (`scholarship-maintain` mục Hoc bong Full) không lọt top-3. Đây cũng là minh họa cho chênh lệch 2 mức chấm: kể cả khi doc đúng lọt top-3 (như Q2/Q3), chunk lọt vào vẫn có thể là section sai.
**Đề xuất:** bật embedder thật (local đa ngữ) để có ngữ nghĩa; thêm overlap để mỗi thông tin có >1 cơ hội lọt top-k; lọc `category=scholarship` khi câu hỏi đã rõ nghiệp vụ; chấm ở mức nội dung (keyword phải xuất hiện trong chunk) thay vì chỉ chấm doc_id.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. Tách file theo `audience` khiến metadata filter có việc thật — demo A/B Q1 có/không filter.
2. Đúng tài liệu ≠ đúng chunk: Q2/Q3 lọt doc đúng nhưng sai section — phải chấm ở mức nội dung.
3. Mock embedder phá hỏng mọi số liệu retrieval — phân tích chuyển sang count/avg_length/coherence khi buộc dùng mock.

**Bài học rút ra khi so sánh trong nhóm:**
Cùng tài liệu nhưng chiến lược khác nhau cho số chunk và độ dài trung bình khác hẳn (by_sentences 6-8 chunk ngắn ~200 ký tự vs fixed/recursive 3-4 chunk dài ~400 ký tự) — chunk ngắn dễ mất ngữ cảnh mục, chunk dài dễ lẫn số liệu.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
Cài embedder thật (local) từ đầu buổi để tải nền; thêm overlap cho HeadingChunker ở các mục chứa số liệu; bổ sung thêm 1-2 file `audience=faculty/staff` để filter có nhiều việc hơn.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 9 / 10 |
| Thiết kế chiến lược (Strategy Design) | 13 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 7 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **33 / 40** |
