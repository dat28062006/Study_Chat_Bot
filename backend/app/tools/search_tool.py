import logging
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 5) -> str:
    """
    Tìm kiếm thông tin trên web bằng Gemini với Google Search grounding.
    Trả về chuỗi chứa kết quả tìm kiếm.
    """
    try:
        genai.configure(api_key=settings.openai_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        response = model.generate_content(
            f"Hãy tìm kiếm và liệt kê {max_results} khóa học/tài liệu tốt nhất về: {query}. "
            f"Ưu tiên tìm trên Coursera, YouTube, Udemy, và các nền tảng học trực tuyến uy tín. "
            f"Mỗi kết quả cần có: Tên khóa học, Nền tảng (Coursera/YouTube/Udemy), Đường link URL đầy đủ, và Mô tả ngắn gọn.",
            tools="google_search"
        )
        
        return response.text or "Không tìm thấy kết quả nào."
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Không thể tìm kiếm web lúc này. Vui lòng thử lại sau hoặc hãy tự lập kế hoạch dựa trên kiến thức có sẵn."
