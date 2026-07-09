import io

from pypdf import PdfReader

from app.services.s3_service import s3_service


class PDFService:
    def extract_text(self, s3_key: str) -> str:
        pdf_bytes = s3_service.download_bytes(s3_key)
        reader = PdfReader(io.BytesIO(pdf_bytes))

        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {i + 1}]\n{text.strip()}")

        full_text = "\n\n".join(pages)
        if not full_text.strip():
            raise ValueError("Khong trich xuat duoc text tu PDF (co the la file scan)")

        return full_text

    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
        words = text.split()
        chunks = []
        start = 0

        while start < len(words):
            end = start + chunk_size
            chunk = " ".join(words[start:end])
            chunks.append(chunk)
            start += chunk_size - overlap

        return chunks


pdf_service = PDFService()
