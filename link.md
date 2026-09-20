Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web
Used tool: search_web

Để phục vụ tối ưu cho một bài **Lab về Vector RAG (Retrieval-Augmented Generation)**, việc chọn nguồn dữ liệu chất lượng là yếu tố quyết định:
1. **Tránh mâu thuẫn dữ liệu (Fact Conflicts):** Nếu bạn crawl nhiều trường khác nhau mà không gắn tag định danh trường, mô hình LLM sẽ bị "nhiễu" vì mỗi trường có quy định riêng (học phí, hạn đăng ký, lệ phí phúc khảo khác nhau).
2. **Khuyến nghị tốt nhất cho bài Lab:** Nên chọn **1 hệ sinh thái đồng nhất** (ví dụ: **Đại học Quốc gia TP.HCM**, tiêu biểu là **UIT + KTX ĐHQG + Thư viện Trung tâm**) hoặc **Đại học Bách Khoa Hà Nội (HUST)** làm bộ dữ liệu chính. Dưới đây là danh sách link đã được phân loại theo 6 dịch vụ/quy định, kèm gợi ý nguồn tài liệu tổng hợp và script crawl mẫu.

---

### I. Danh sách URL chất lượng cao theo từng chủ đề

#### 1. Đăng ký học phần (Course Registration)
*Nội dung trích xuất: Điều kiện tiên quyết, số tín chỉ tối thiểu/tối đa, các đợt đăng ký, quy định hủy/rút môn, xử lý trùng lịch.*
* **UIT (ĐHQG-HCM):**
  * Hướng dẫn & Quy định ĐKHP: [https://daa.uit.edu.vn](https://daa.uit.edu.vn) (chuyên mục *Quy chế, Quy định đào tạo đại học* & *Thông báo ĐKHP*).
  * Quy chế đào tạo tín chỉ: [https://ctsv.uit.edu.vn/content/so-tay-sinh-vien](https://ctsv.uit.edu.vn/content/so-tay-sinh-vien) (Phần Quy chế học vụ).
* **Đại học Bách khoa Hà Nội (HUST):**
  * Cổng thông tin đào tạo SIS: [https://ctt-sis.hust.edu.vn](https://ctt-sis.hust.edu.vn) (Mục *Quy chế đào tạo* & *Hướng dẫn đăng ký học tập*).
  * Phòng Đào tạo HUST: [https://daotao.hust.edu.vn](https://daotao.hust.edu.vn)
* **HCMUT (ĐH Bách Khoa - ĐHQG-HCM):**
  * Quy định học vụ và đào tạo đại học: [https://aao.hcmut.edu.vn](https://aao.hcmut.edu.vn)

---

#### 2. Học phí & Chế độ chính sách (Tuition & Financial Aid)
*Nội dung trích xuất: Đơn giá tín chỉ, các đợt thu học phí, phương thức thanh toán, chính sách miễn/giảm học phí, gia hạn nợ học phí.*
* **UIT (ĐHQG-HCM):**
  * Phòng Kế hoạch - Tài chính: [https://khtc.uit.edu.vn](https://khtc.uit.edu.vn) (Thông báo định mức và thời hạn đóng học phí).
  * Quy định miễn giảm học phí / trợ cấp xã hội: [https://ctsv.uit.edu.vn/bai-viet/che-do-chinh-sach-mien-giam-hoc-phi](https://ctsv.uit.edu.vn/bai-viet/che-do-chinh-sach-mien-giam-hoc-phi)
* **Đại học Kinh tế Quốc dân (NEU):**
  * Cổng thông tin tài chính - học phí: [https://daotao.neu.edu.vn](https://daotao.neu.edu.vn)
* **Đại học Bách khoa Hà Nội (HUST):**
  * Học phí & Hỗ trợ tài chính: [https://hust.edu.vn](https://hust.edu.vn) (Mục *Sinh viên* -> *Học phí*)

---

#### 3. Học bổng (Scholarships)
*Nội dung trích xuất: Điều kiện GPA/ĐRL để xét học bổng Khuyến khích học tập (KKHT), định mức các loại (Khá, Giỏi, Xuất sắc), học bổng doanh nghiệp tài trợ, quy trình nộp hồ sơ.*
* **UIT (ĐHQG-HCM):**
  * Chuyên mục Học bổng P.CTSV: [https://ctsv.uit.edu.vn/danh-muc/hoc-bong](https://ctsv.uit.edu.vn/danh-muc/hoc-bong)
  * Quy định học bổng KKHT: [https://ctsv.uit.edu.vn/bai-viet/quy-dinh-lien-quan-den-hoc-bong-sinh-vien](https://ctsv.uit.edu.vn/bai-viet/quy-dinh-lien-quan-den-hoc-bong-sinh-vien)
* **HUST (Bách Khoa Hà Nội):**
  * Ban Công tác Sinh viên HUST: [https://ctsv.hust.edu.vn](https://ctsv.hust.edu.vn) (Chuyên mục *Học bổng KKHT* và *Học bổng Tài trợ*).

---

#### 4. Thư viện (Library Services & Regulations)
*Nội dung trích xuất: Nội quy mượn trả tài liệu, số lượng sách tối đa, thời hạn mượn, mức phạt trễ hạn, hướng dẫn truy cập cơ sở dữ liệu số (IEEE, ScienceDirect).*
* **Thư viện Trung tâm ĐHQG-HCM (VNU-LIC):**
  * Trang chủ: [https://www.vnulib.edu.vn](https://www.vnulib.edu.vn)
  * Chính sách mượn - trả tài liệu & tiền thế chân: [https://www.vnulib.edu.vn/index.php/dich-vu/muon-tra-tai-lieu](https://www.vnulib.edu.vn/index.php/dich-vu/muon-tra-tai-lieu)
* **Thư viện UIT:**
  * Hướng dẫn & Dịch vụ thư viện: [https://thuvien.uit.edu.vn](https://thuvien.uit.edu.vn)
* **Thư viện Tạ Quang Bửu (HUST):**
  * Nội quy & Dịch vụ bạn đọc: [https://library.hust.edu.vn](https://library.hust.edu.vn)

---

#### 5. Ký túc xá (Dormitory)
*Nội dung trích xuất: Đối tượng ưu tiên xét nội trú, quy trình đăng ký phòng online, đơn giá phòng ở các loại (phòng 2/4/6/8 người), nội quy an ninh trật tự, quy định ra/vào.*
* **Ký túc xá ĐHQG-HCM (Hệ thống KTX lớn nhất Việt Nam):**
  * Trang thông tin chính: [https://ktx.vnuhcm.edu.vn](https://ktx.vnuhcm.edu.vn)
  * Cổng đăng ký phòng ở sinh viên: [https://sv.ktxhcm.edu.vn](https://sv.ktxhcm.edu.vn)
  * Cổng hướng dẫn thủ tục, biểu mẫu, quy chế: [https://huongdan.ktxhcm.edu.vn](https://huongdan.ktxhcm.edu.vn)
* **Ký túc xá Bách Khoa Hà Nội:**
  * Trang thông tin KTX HUST: [https://ktx.hust.edu.vn](https://ktx.hust.edu.vn)

---

#### 6. Phúc khảo & Khiếu nại điểm (Grade Appeal)
*Nội dung trích xuất: Thời hạn nộp đơn sau khi công bố điểm, lệ phí phúc khảo/môn, trường hợp nào được sửa đổi điểm số, quy trình nhận đơn.*
* **UIT (ĐHQG-HCM):**
  * Quy trình & Thông báo phúc khảo: [https://daa.uit.edu.vn](https://daa.uit.edu.vn)
  * Cổng sinh viên đăng ký phúc khảo online: [https://student.uit.edu.vn](https://student.uit.edu.vn)
* **NEU (ĐH Kinh tế Quốc dân):**
  * Phòng Quản lý Đào tạo (Quy chế khảo thí & học vụ): [https://daotao.neu.edu.vn](https://daotao.neu.edu.vn)
* **HUST (Bách Khoa Hà Nội):**
  * Quy định kiểm tra, thi và phúc khảo: [https://ctt-sis.hust.edu.vn](https://ctt-sis.hust.edu.vn)

---

### II. "Nguồn vàng" cho RAG Lab: Sổ tay sinh viên (Student Handbook)

Thay vì crawl hàng trăm bài viết lẻ tẻ dễ bị nhiễu và đứt gãy cấu trúc, **Sổ tay sinh viên** là tài liệu chuẩn mực nhất vì đã được biên tập trọn vẹn cả 6 chủ đề trên:
* **UIT Sổ tay sinh viên:** [https://ctsv.uit.edu.vn/content/so-tay-sinh-vien](https://ctsv.uit.edu.vn/content/so-tay-sinh-vien)
* **HCMUT Sổ tay sinh viên:** Tìm mục *Sổ tay sinh viên* tại [https://ctsv.hcmut.edu.vn](https://ctsv.hcmut.edu.vn)

---

### III. Gợi ý kỹ thuật phục vụ bài Lab Vector RAG

#### 1. Bộ Metadata cần lưu khi crawl
Để xây dựng một pipeline RAG chuyên nghiệp (hỗ trợ **Metadata Filtering / Hybrid Search**), mỗi chunk văn bản khi crawl về nên có schema như sau:
```json
{
  "doc_id": "uit_hocphi_01",
  "source_url": "https://khtc.uit.edu.vn/...",
  "university": "UIT",
  "category": "hoc_phi",  // 1 trong 6 nhãn: dang_ky_hoc_phan, hoc_phi, hoc_bong, thu_vien, ky_tuc_xa, phuc_khao
  "title": "Quy định về việc thu học phí học kỳ 1 năm học...",
  "content": "Sinh viên có trách nhiệm hoàn thành học phí trước ngày..."
}
```

#### 2. Thư viện Crawl khuyến nghị
* Dùng **`trafilatura`**: Thư viện Python chuyên trích xuất text bài viết (bỏ qua menu, header, footer, quảng cáo) sạch hơn nhiều so với `BeautifulSoup` thuần.
  ```bash
  pip install trafilatura requests
  ```
* Script mẫu trích xuất text sạch:
  ```python
  import trafilatura

  def extract_clean_text(url: str) -> str:
      downloaded = trafilatura.fetch_url(url)
      text = trafilatura.extract(
          downloaded,
          include_comments=False,
          include_tables=True,       # Rất quan trọng vì học phí/điểm thưởng thường nằm trong bảng
          output_format='markdown'    # Giữ định dạng markdown giúp chunking tốt hơn
      )
      return text or ""
  ```

#### 3. Chiến lược Chunking cho văn bản quy chế
* Văn bản quy định đại học luôn có định dạng pháp lý: **Chương > Điều > Khoản > Điểm**.
* **Tránh:** Cắt cứng `chunk_size=500` không theo ngữ cảnh (sẽ làm mất quan hệ điều kiện của câu quy định).
* **Khuyến nghị:** Dùng `RecursiveCharacterTextSplitter` với các điểm phân tách:
  ```python
  separators = ["\nĐiều ", "\nChương ", "\n\n", "\n- ", "\n", " "]
  ```