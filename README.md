# Study Chat Bot (RAG App)

Hệ thống Chatbot học tập thông minh sử dụng kiến trúc RAG (Retrieval-Augmented Generation) và tự động hóa quy trình. Dự án kết hợp công nghệ AI đa luồng (Multi-Agent) với các công cụ tự động hóa để cung cấp trải nghiệm cố vấn và chấm bài tập cho người dùng.

## Kiến trúc hệ thống
- **Backend:** FastAPI (Python), quản lý logic chat và Agent.
- **Frontend:** Next.js (React), giao diện người dùng.
- **Cơ sở dữ liệu:**
  - PostgreSQL: Lưu trữ thông tin người dùng và lịch sử chat.
  - Redis: Cache và background jobs.
  - Qdrant: Vector Database lưu trữ ngữ cảnh tài liệu (Document Context) cho mô hình RAG.
- **Tự động hóa:** n8n, hỗ trợ tạo lộ trình học, thiết lập nhắc nhở tự động qua Webhook và Email.
- **AI Models:** Tích hợp mô hình ngôn ngữ lớn (ví dụ: Google Gemini) thông qua kiến trúc Multi-Agent (Mentor Agent & Grader Agent).
- **Deployment:** Cấu hình chuẩn hóa với Docker & Docker Compose.

## Tính năng chính
1. **Chat RAG:** Tải tài liệu lên (PDF, Text) và đặt câu hỏi, AI sẽ tìm kiếm ngữ cảnh chuẩn xác để trả lời.
2. **Cố vấn học tập (Mentor Agent):** Tự động tạo lộ trình học tập, tìm kiếm tài liệu mở (YouTube, Coursera) và gửi email nhắc nhở định kỳ qua n8n.
3. **Giáo viên chấm bài (Grader Agent):** Đánh giá bài làm, góp ý và chấm điểm độc lập dựa trên ngữ cảnh học tập.

## Hướng dẫn cài đặt bằng Docker
Yêu cầu hệ thống phải cài đặt sẵn [Docker](https://docs.docker.com/get-docker/) và Docker Compose.

1. Clone dự án về máy:
```bash
git clone https://github.com/dat28062006/Study_Chat_Bot.git
cd Study_Chat_Bot
```

2. Cấu hình biến môi trường:
Tạo file `.env` từ file mẫu:
```bash
cp .env.example .env
```
Mở file `.env` và điền các API Key cần thiết (ví dụ: `OPENAI_API_KEY`).

3. Khởi chạy toàn bộ hệ thống:
```bash
docker-compose up -d
```

4. Truy cập dịch vụ:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- n8n Automation: `http://localhost:5678`
