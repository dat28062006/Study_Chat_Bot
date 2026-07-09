import os
import json
import requests
from datetime import datetime
from app.config import settings

def export_plan_to_n8n(to_email: str, subject: str, plan_json: str) -> str:
    """
    Đóng gói kế hoạch học tập thành JSON và xuất sang n8n qua Webhook.
    plan_json BẮT BUỘC phải là một chuỗi JSON hợp lệ (list of dictionaries).
    Mỗi ngày học phải có ĐẦY ĐỦ các key sau:
    [
      {
        "ngay": <số nguyên>,
        "chu_de": "<tên chủ đề>",
        "muc_tieu": "<mục tiêu của bài học>",
        "tai_lieu": "<đường link tài liệu>",
        "video": "<đường link video>",
        "bai_tap": "<mô tả bài tập>"
      }
    ]
    """
    try:
        plan_data = json.loads(plan_json)
    except json.JSONDecodeError:
        return "Lỗi: plan_json không phải là định dạng JSON hợp lệ. Vui lòng định dạng lại."

    payload = {
        "to_email": to_email,
        "subject": subject,
        "schedule": plan_data,
        "timestamp": datetime.now().isoformat()
    }

    if settings.n8n_webhook_url:
        try:
            response = requests.post(settings.n8n_webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return f"Đã xuất dữ liệu thành công sang n8n (Webhook URL: {settings.n8n_webhook_url})."
        except Exception as e:
            return f"Gặp lỗi khi gửi Webhook sang n8n: {str(e)}"
    else:
        # Nếu chưa cấu hình Webhook, lưu thành file JSON để người dùng test/setup
        export_dir = "/app/uploads/n8n_payloads"
        os.makedirs(export_dir, exist_ok=True)
        filename = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
            
        return f"Vì chưa cấu hình N8N_WEBHOOK_URL, dữ liệu JSON giả lập n8n đã được lưu tại: http://localhost:8000/uploads/n8n_payloads/{filename}. Bạn có thể tải về để làm dữ liệu mẫu (Mock Data) trên n8n."
