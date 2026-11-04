import os
import io
import re
import numpy as np
from typing import List, Dict, Any, Union
from PIL import Image, ImageEnhance, ImageFilter
import pypdfium2 as pdfium

from src.extractor.row_stitcher import RowStitcher
from src.extractor.metadata_parser import MetadataParser


class OCRExtractor:
    """
    Extracts text, metadata, and transaction tables from Image-Based / Scanned PDFs.
    Uses EasyOCR (PyTorch computer vision) with fallback to pytesseract / image filters.
    """

    _reader = None

    @classmethod
    def get_easyocr_reader(cls):
        """
        Lazy-loads the EasyOCR Reader instance with local model storage.
        """
        if cls._reader is None:
            try:
                import easyocr
                import torch
                has_cuda = torch.cuda.is_available()
                local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models", "easyocr"))
                os.makedirs(local_dir, exist_ok=True)
                cls._reader = easyocr.Reader(
                    ["en"], 
                    gpu=has_cuda,
                    model_storage_directory=local_dir,
                    user_network_directory=local_dir
                )
            except Exception as e:
                print(f"Warning: EasyOCR initialization error: {e}")
                cls._reader = None
        return cls._reader

    @classmethod
    def extract(cls, file_source: Union[str, bytes, io.BytesIO]) -> Dict[str, Any]:
        """
        Main extraction entrypoint for image-based/scanned PDFs.
        """
        if isinstance(file_source, bytes):
            pdf_bytes = file_source
        elif isinstance(file_source, io.BytesIO):
            pdf_bytes = file_source.getvalue()
        elif isinstance(file_source, str):
            with open(file_source, "rb") as f:
                pdf_bytes = f.read()
        else:
            if hasattr(file_source, "read"):
                curr = file_source.tell() if hasattr(file_source, "tell") else 0
                pdf_bytes = file_source.read()
                if hasattr(file_source, "seek"):
                    file_source.seek(curr)
            else:
                raise ValueError("Unsupported file source type")

        # Render PDF pages to PIL Images using pypdfium2
        doc = pdfium.PdfDocument(pdf_bytes)
        total_pages = len(doc)
        page_images = []
        
        for idx in range(total_pages):
            page = doc[idx]
            # Render at 2.5x scale (~180-200 DPI) for optimal OCR quality
            bitmap = page.render(scale=2.5)
            pil_image = bitmap.to_pil()
            page_images.append(pil_image)

        # Preprocess images
        preprocessed_images = [cls._preprocess_for_ocr(img) for img in page_images]

        reader = cls.get_easyocr_reader()
        full_extracted_text = []
        raw_rows = []
        extraction_mode = "EASYOCR_ENGINE"

        if reader is not None:
            for pil_img in preprocessed_images:
                img_np = np.array(pil_img)
                ocr_results = reader.readtext(img_np)
                
                # Group OCR text boxes by vertical y-coordinate into lines
                lines = cls._group_ocr_boxes_into_lines(ocr_results)
                page_text = "\n".join(lines)
                full_extracted_text.append(page_text)

                parsed_lines = cls._parse_ocr_text_lines(page_text)
                raw_rows.extend(parsed_lines)
        else:
            # Fallback to pytesseract if EasyOCR is unavailable
            try:
                import pytesseract
                for pil_img in preprocessed_images:
                    txt = pytesseract.image_to_string(pil_img, config="--psm 6")
                    full_extracted_text.append(txt)
                    raw_rows.extend(cls._parse_ocr_text_lines(txt))
                extraction_mode = "TESSERACT_OCR"
            except Exception:
                # Basic token inspection fallback
                for idx in range(total_pages):
                    page = doc[idx]
                    tp = page.get_textpage()
                    raw_t = tp.get_text_range() or ""
                    if raw_t.strip():
                        full_extracted_text.append(raw_t)
                        raw_rows.extend(cls._parse_ocr_text_lines(raw_t))
                extraction_mode = "OCR_FALLBACK_ENGINE"

        combined_text = "\n".join(full_extracted_text)
        metadata = MetadataParser.extract_metadata(combined_text)
        stitched_transactions = RowStitcher.stitch_raw_rows(raw_rows)

        return {
            "metadata": metadata,
            "transactions": stitched_transactions,
            "extraction_stats": {
                "pages_processed": total_pages,
                "images_rendered": len(page_images),
                "raw_rows_found": len(raw_rows),
                "stitched_transactions_count": len(stitched_transactions),
                "extraction_mode": extraction_mode,
                "easyocr_active": reader is not None
            }
        }

    @classmethod
    def _preprocess_for_ocr(cls, image: Image.Image) -> Image.Image:
        """
        Enhances image for OCR:
        1. Grayscale
        2. Contrast enhancement
        3. Sharpening
        """
        gray = image.convert("L")
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(1.8)
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        return sharpened

    @classmethod
    def _group_ocr_boxes_into_lines(cls, ocr_results: List[Any], y_threshold: int = 15) -> List[str]:
        """
        Groups bounding boxes from EasyOCR into left-to-right lines based on vertical overlap.
        ocr_results format: [ ( [ [x1,y1], [x2,y2], [x3,y3], [x4,y4] ], text, confidence ), ... ]
        """
        if not ocr_results:
            return []

        # Calculate bounding box centers
        boxes = []
        for bbox, text, conf in ocr_results:
            text_str = str(text).strip()
            if not text_str:
                continue
            y_center = (bbox[0][1] + bbox[2][1]) / 2.0
            x_left = bbox[0][0]
            boxes.append((y_center, x_left, text_str))

        # Sort primarily by y_center
        boxes.sort(key=lambda b: b[0])

        lines = []
        curr_line = []
        curr_y = None

        for y_c, x_l, text in boxes:
            if curr_y is None:
                curr_y = y_c
                curr_line.append((x_l, text))
            elif abs(y_c - curr_y) <= y_threshold:
                curr_line.append((x_l, text))
            else:
                # Sort line items left to right
                curr_line.sort(key=lambda item: item[0])
                line_str = " ".join(item[1] for item in curr_line)
                lines.append(line_str)

                curr_y = y_c
                curr_line = [(x_l, text)]

        if curr_line:
            curr_line.sort(key=lambda item: item[0])
            line_str = " ".join(item[1] for item in curr_line)
            lines.append(line_str)

        return lines

    @classmethod
    def _parse_ocr_text_lines(cls, text: str) -> List[Dict[str, Any]]:
        """
        Parses OCR text output lines into candidate transaction rows.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        rows = []

        date_pattern = re.compile(r"^(\d{1,2}[\/\-\.][A-Za-z0-9]{1,3}[\/\-\.]\d{2,4})")
        trailing_two_amounts = re.compile(r"\s+([0-9,]+\.[0-9]{2})\s+([0-9,]+\.[0-9]{2})$")
        trailing_one_amount = re.compile(r"\s+([0-9,]+\.[0-9]{2})$")

        CREDIT_HINTS = ["SALARY", "CREDIT", "DEP", "DEPOSIT", "CR", "DIVIDEND", "REFUND"]
        last_seen_balance = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Normalize common OCR decimal and spacing artifacts (e.g. "420 . 00" -> "420.00")
            line_str = re.sub(r"(\d+)\s*\.\s*(\d{2})\b", r"\1.\2", line_str)
            line_str = re.sub(r"(\d+)\s+(\d{2})\b", r"\1.\2", line_str)

            date_match = date_pattern.match(line_str)
            if date_match:
                date_val = date_match.group(1)
                remainder = line_str[len(date_val):].strip()

                # Extract all financial numbers with 2 decimals from the line
                currency_amounts = re.findall(r"\b[0-9,]+\.[0-9]{2}\b", remainder)

                if len(currency_amounts) >= 2:
                    amt1_str = currency_amounts[-2]
                    amt2_str = currency_amounts[-1]

                    # Find where amt1 starts in remainder to get description
                    amt1_pos = remainder.rfind(amt1_str)
                    desc_val = remainder[:amt1_pos].strip()

                    parsed_amt = RowStitcher.clean_amount(amt1_str)
                    parsed_bal = RowStitcher.clean_amount(amt2_str)

                    if last_seen_balance is not None and abs(parsed_bal - last_seen_balance) > 0.01:
                        if parsed_bal < last_seen_balance:
                            debit_val = amt1_str
                            credit_val = "0.0"
                        else:
                            debit_val = "0.0"
                            credit_val = amt1_str
                    else:
                        is_credit = any(kw in desc_val.upper() for kw in CREDIT_HINTS)
                        if is_credit:
                            debit_val = "0.0"
                            credit_val = amt1_str
                        else:
                            debit_val = amt1_str
                            credit_val = "0.0"

                    last_seen_balance = parsed_bal

                    rows.append({
                        "date": date_val,
                        "description": desc_val,
                        "debit": debit_val,
                        "credit": credit_val,
                        "balance": amt2_str
                    })
                    continue

                elif len(currency_amounts) == 1:
                    amt_str = currency_amounts[0]
                    amt_pos = remainder.rfind(amt_str)
                    desc_val = remainder[:amt_pos].strip()
                    parsed_bal = RowStitcher.clean_amount(amt_str)
                    last_seen_balance = parsed_bal

                    rows.append({
                        "date": date_val,
                        "description": desc_val,
                        "debit": "0.0",
                        "credit": "0.0",
                        "balance": amt_str
                    })
                    continue

                rows.append({
                    "date": date_val,
                    "description": remainder,
                    "debit": "0.0",
                    "credit": "0.0",
                    "balance": "0.0"
                })

            else:
                rows.append({
                    "date": "",
                    "description": line_str,
                    "debit": "0.0",
                    "credit": "0.0",
                    "balance": "0.0"
                })

        return rows
