import asyncio
import re
from app.config import settings
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service
from app.schemas.chat import ChatMessage
import datetime

class RAGAgent:
    def _clean_response(self, text: str) -> str:
        """Loại bỏ các khối tool_code, thought và code thừa mà Gemini có thể trả về."""
        # Loại bỏ các khối tool_code ... (bao gồm nội dung bên trong)
        text = re.sub(r'tool_code\n.*?\n(?=\w|$)', '', text, flags=re.DOTALL)
        # Loại bỏ các khối thought ...
        text = re.sub(r'thought\n.*?\n(?=\w|$)', '', text, flags=re.DOTALL)
        # Loại bỏ dòng print(default_api....)
        text = re.sub(r'print\(default_api\..*?\)\n?', '', text)
        # Loại bỏ khoảng trắng/dòng trống thừa ở đầu
        text = text.strip()
        return text

    async def answer(self, messages: list[ChatMessage], document_ids: list[str] | None = None, agent_type: str = "mentor"):
        if not messages:
            return
            
        latest_question = messages[-1].content
        model = llm_service.get_model(agent_type)
        
        history = []
        for msg in messages[:-1]:
            role = "user" if msg.role == "user" else "model"
            history.append({"role": role, "parts": [msg.content]})

        # --- BƯỚC 1: TÁI CẤU TRÚC CÂU HỎI (Contextualize Question) ---
        search_query = latest_question
        # Chỉ viết lại nếu có lịch sử chat và câu hỏi đủ dài để mang ý nghĩa
        if history and len(latest_question) > 5:
            rewrite_prompt = f"""Dựa vào lịch sử trò chuyện (từ system/user/model), hãy viết lại câu hỏi cuối cùng của người dùng thành một câu hỏi độc lập (standalone question) rõ ràng và đầy đủ ý nghĩa nhất để có thể dùng để tìm kiếm tài liệu.
Nếu câu hỏi cuối cùng đã rõ nghĩa hoặc không liên quan đến lịch sử, hãy giữ nguyên. KHÔNG ĐƯỢC trả lời câu hỏi, CHỈ viết lại câu hỏi một cách ngắn gọn.

Câu hỏi cuối cùng: {latest_question}"""
            
            # Gọi LLM (sử dụng model hiện tại, tắt function calling để đảm bảo chỉ trả text)
            rewrite_chat = model.start_chat(history=history, enable_automatic_function_calling=False)
            rewrite_response = rewrite_chat.send_message(rewrite_prompt)
            search_query = self._clean_response(rewrite_response.text or "").strip()
            
            if not search_query:
                search_query = latest_question

        # --- BƯỚC 2: TÌM KIẾM TÀI LIỆU DỰA TRÊN CÂU HỎI ĐÃ VIẾT LẠI ---
        # Bỏ qua nhúng (embedding) và tìm kiếm tài liệu nếu câu hỏi quá ngắn (vd: chỉ nhập email hoặc số ngày) để tiết kiệm API Quota
        context_text = ""
        if len(search_query) > 20:
            query_embedding = embedding_service.embed(search_query)
            results = vector_service.search(
                query_embedding=query_embedding,
                document_ids=document_ids,
                top_k=settings.top_k,
            )
            context_chunks = [r["text"] for r in results] if results else []
            context_text = "\n\n---\n\n".join(context_chunks)

        # --- BƯỚC 3: SINH CÂU TRẢ LỜI (Generation) ---
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = f"System Time: {current_time}\n\nDocument Context (Use this if relevant):\n{context_text}\n\nUser Message:\n{latest_question}"

        # Sử dụng chế độ KHÔNG stream để đảm bảo automatic function calling hoạt động đúng
        chat = model.start_chat(history=history, enable_automatic_function_calling=True)
        response = chat.send_message(prompt)

        # Lấy text và lọc bỏ nội dung kỹ thuật thừa
        full_text = self._clean_response(response.text or "")
        
        if not full_text:
            full_text = "Đã hoàn tất!"

        # Chia nhỏ để giả lập streaming cho frontend
        chunk_size = 20
        for i in range(0, len(full_text), chunk_size):
            yield full_text[i:i + chunk_size]
            await asyncio.sleep(0.02)

    async def grade_homework(self, topic: str, homework_content: str, agent_type: str = "mentor") -> str:
        model = llm_service.get_model(agent_type)
        
        prompt = f"""Đóng vai một giáo viên chấm bài xuất sắc, hãy chấm điểm và nhận xét chi tiết bài làm của học viên dựa trên chủ đề bài học.

Chủ đề bài học: {topic}

Bài làm của học viên:
{homework_content}

Yêu cầu nhận xét:
1. Đánh giá chung (Tốt, Khá, Cần cố gắng).
2. Những điểm làm tốt.
3. Những điểm cần cải thiện hoặc sửa lỗi (nếu có).
4. Cho điểm (nếu phù hợp).
"""
        chat = model.start_chat(history=[], enable_automatic_function_calling=False)
        response = chat.send_message(prompt)
        
        full_text = self._clean_response(response.text or "")
        return full_text

rag_agent = RAGAgent()
