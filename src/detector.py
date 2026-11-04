import io
from typing import Dict, Any, Union, Optional
import pdfplumber
import pypdfium2 as pdfium
from pdfminer.pdfdocument import PDFPasswordIncorrect


class PDFTypeDetector:
    """
    Auto-detects whether a bank statement PDF is text-based (digital) or 
    image-based (scanned document), and identifies password-protected statements.
    """

    CHAR_THRESHOLD_PER_PAGE = 50
    WORD_THRESHOLD_PER_PAGE = 8

    @classmethod
    def detect(cls, file_source: Union[str, bytes, io.BytesIO], password: Optional[str] = None) -> Dict[str, Any]:
        """
        Inspects pages of a PDF to determine its type and characteristics.
        Supports encrypted / password-protected bank statements.
        """
        page_analysis = []
        total_chars = 0
        total_words = 0
        total_images = 0

        # Handle different input types
        if isinstance(file_source, bytes):
            pdf_bytes = file_source
        elif isinstance(file_source, io.BytesIO):
            pdf_bytes = file_source.getvalue()
        elif isinstance(file_source, str):
            with open(file_source, "rb") as f:
                pdf_bytes = f.read()
        else:
            if hasattr(file_source, "read"):
                curr_pos = file_source.tell() if hasattr(file_source, "tell") else 0
                pdf_bytes = file_source.read()
                if hasattr(file_source, "seek"):
                    file_source.seek(curr_pos)
            else:
                raise ValueError(f"Unsupported file source type: {type(file_source)}")

        # Primary extraction check using pdfplumber with password support
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes), password=password) as pdf:
                total_pages = len(pdf.pages)
                
                for idx, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    words = page.extract_words() or []
                    images = page.images or []
                    
                    char_count = len(text.strip())
                    word_count = len(words)
                    img_count = len(images)
                    
                    is_page_text = (
                        char_count >= cls.CHAR_THRESHOLD_PER_PAGE or 
                        word_count >= cls.WORD_THRESHOLD_PER_PAGE
                    )

                    page_analysis.append({
                        "page_number": idx + 1,
                        "char_count": char_count,
                        "word_count": word_count,
                        "image_count": img_count,
                        "page_type": "TEXT" if is_page_text else "IMAGE"
                    })

                    total_chars += char_count
                    total_words += word_count
                    total_images += img_count

        except PDFPasswordIncorrect:
            return {
                "doc_type": "PASSWORD_PROTECTED",
                "is_encrypted": True,
                "is_unlocked": False,
                "error_message": "Document is password protected. Enter the password to unlock.",
                "total_pages": 1,
                "total_characters": 0,
                "total_words": 0,
                "avg_chars_per_page": 0,
                "page_analysis": []
            }
        except Exception:
            # Fallback inspection with pypdfium2
            try:
                doc = pdfium.PdfDocument(pdf_bytes, password=password)
                total_pages = len(doc)
                for idx in range(total_pages):
                    page = doc[idx]
                    textpage = page.get_textpage()
                    extracted_text = textpage.get_text_range() or ""
                    char_count = len(extracted_text.strip())
                    words = extracted_text.split()
                    word_count = len(words)
                    
                    is_page_text = (
                        char_count >= cls.CHAR_THRESHOLD_PER_PAGE or 
                        word_count >= cls.WORD_THRESHOLD_PER_PAGE
                    )

                    page_analysis.append({
                        "page_number": idx + 1,
                        "char_count": char_count,
                        "word_count": word_count,
                        "image_count": 0,
                        "page_type": "TEXT" if is_page_text else "IMAGE"
                    })

                    total_chars += char_count
                    total_words += word_count
            except Exception:
                return {
                    "doc_type": "PASSWORD_PROTECTED",
                    "is_encrypted": True,
                    "is_unlocked": False,
                    "error_message": "Document is password protected. Enter the password to unlock.",
                    "total_pages": 1,
                    "total_characters": 0,
                    "total_words": 0,
                    "avg_chars_per_page": 0,
                    "page_analysis": []
                }

        avg_chars = total_chars / max(total_pages, 1)
        text_pages_count = sum(1 for p in page_analysis if p["page_type"] == "TEXT")
        image_pages_count = sum(1 for p in page_analysis if p["page_type"] == "IMAGE")

        # Determine overall document classification
        if text_pages_count > 0 and image_pages_count == 0:
            doc_type = "TEXT_BASED"
        elif text_pages_count == 0 and image_pages_count > 0:
            doc_type = "IMAGE_BASED"
        else:
            doc_type = "TEXT_BASED" if avg_chars >= cls.CHAR_THRESHOLD_PER_PAGE else "IMAGE_BASED"

        is_hybrid = (text_pages_count > 0 and image_pages_count > 0)

        return {
            "doc_type": doc_type,
            "is_encrypted": False,
            "is_unlocked": True,
            "total_pages": total_pages,
            "total_characters": total_chars,
            "total_words": total_words,
            "avg_chars_per_page": round(avg_chars, 1),
            "page_analysis": page_analysis,
            "is_hybrid": is_hybrid
        }
