import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
import logging

from app.config import settings

logger = logging.getLogger(__name__)

jobstores = {'default': MemoryJobStore()}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

def send_email_sync(to_email: str, subject: str, body: str, job_id: str = None) -> str:
    """Gửi email thông qua SMTP hoặc Hệ thống Email Ảo."""
    if job_id:
        unsubscribe_link = f"http://localhost:8000/api/cancel/{job_id}"
        body += f"<br><br><hr><p style='color: gray; font-size: 12px;'><i>Để hủy nhận chuỗi email nhắc nhở này, vui lòng <a href='{unsubscribe_link}'>nhấn vào đây</a>.</i></p>"

    if not settings.smtp_username or not settings.smtp_password:
        import os
        from datetime import datetime
        email_dir = "/app/uploads/emails"
        os.makedirs(email_dir, exist_ok=True)
        filename = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(email_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"<h1>Subject: {subject}</h1><h2>To: {to_email}</h2><hr/>{body}")
            
        return f"Đã gửi qua Hệ thống Email Ảo! Người dùng có thể xem tại: http://localhost:8000/uploads/emails/{filename}"

    msg = MIMEMultipart()
    msg['From'] = settings.smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)
        server.quit()
        return f"Đã gửi email thành công tới {to_email}."
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return f"Lỗi khi gửi email: {str(e)}"

def schedule_email(to_email: str, subject: str, body: str, run_date: str) -> str:
    """
    Lên lịch gửi email vào một thời điểm cụ thể.
    run_date phải theo định dạng YYYY-MM-DD HH:MM:SS
    """
    import uuid
    job_id = uuid.uuid4().hex
    try:
        dt = datetime.strptime(run_date, "%Y-%m-%d %H:%M:%S")
        scheduler.add_job(send_email_sync, 'date', run_date=dt, args=[to_email, subject, body, job_id], id=job_id)
        return f"Đã lên lịch gửi email tới {to_email} vào lúc {run_date} (Job ID: {job_id})."
    except Exception as e:
        return f"Lỗi khi lên lịch email: {str(e)}"
