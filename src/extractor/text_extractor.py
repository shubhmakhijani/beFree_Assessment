import io
import re
from typing import List, Dict, Any, Union, Optional
import pdfplumber

from src.extractor.row_stitcher import RowStitcher
from src.extractor.metadata_parser import MetadataParser


class TextBasedExtractor:
    """
    Extracts transaction tables and metadata from native digital/text-based PDFs.
    Uses layout-agnostic column mapping to support varying bank formats.
    """

    COLUMN_SYNONYMS = {
        "date": [
            "date", "txn date", "transaction date", "post date", 
            "posting date", "value date", "val date"
        ],
        "description": [
            "description", "narration", "particulars", "transaction details", 
            "transaction remarks", "details", "remarks"
        ],
        "cheque_ref": [
            "chq no", "cheque no", "ref no", "reference no", 
            "chq/ref no", "utr", "cheque number"
        ],
        "debit": [
            "debit", "withdrawal", "dr", "debit amount", "withdrawal amt", 
            "dr (inr)", "debit (inr)", "withdrawal (inr)", "dr amount"
        ],
        "credit": [
            "credit", "deposit", "cr", "credit amount", "deposit amt", 
            "cr (inr)", "credit (inr)", "deposit (inr)", "cr amount"
        ],
        "balance": [
            "balance", "closing balance", "net balance", "bal", 
            "balance (inr)", "closing bal", "run balance"
        ],
        "amount": [
            "amount", "txn amount", "transaction amount", "amount (inr)"
        ]
    }

    CREDIT_HINTS = [
        "SALARY", "CREDIT", "DEP", "DEPOSIT", "CR", "DIVIDEND", "REFUND", "CASHBACK", "INT.PD", "INTEREST"
    ]

    @classmethod
    def extract(cls, file_source: Union[str, bytes, io.BytesIO], password: Optional[str] = None) -> Dict[str, Any]:
        """
        Main extraction entrypoint for text-based PDFs.
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

        full_doc_text = []
        raw_rows = []

        with pdfplumber.open(io.BytesIO(pdf_bytes), password=password) as pdf:
            total_pages = len(pdf.pages)

            for page_idx, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                full_doc_text.append(page_text)

                # Attempt 1: Explicit bordered tables (gridlines)
                tables = page.extract_tables({
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                    "snap_tolerance": 4,
                    "join_tolerance": 4,
                })

                parsed_table_rows = []
                for table in tables:
                    parsed = cls._parse_table_data(table)
                    parsed_table_rows.extend(parsed)

                # Validate whether table extraction yielded genuine transactions
                has_meaningful_data = any(
                    r.get("date") and r.get("description") and 
                    (RowStitcher.clean_amount(r.get("debit")) > 0 or 
                     RowStitcher.clean_amount(r.get("credit")) > 0 or 
                     RowStitcher.clean_amount(r.get("balance")) > 0)
                    for r in parsed_table_rows
                )

                if has_meaningful_data:
                    raw_rows.extend(parsed_table_rows)
                else:
                    # Robust line-by-line parsing based on bank statement patterns
                    text_rows = cls._parse_text_lines(page_text)
                    raw_rows.extend(text_rows)

        # Extract metadata from document text
        combined_text = "\n".join(full_doc_text)
        metadata = MetadataParser.extract_metadata(combined_text)

        # Multi-line row stitching & normalization
        stitched_transactions = RowStitcher.stitch_raw_rows(raw_rows)

        return {
            "metadata": metadata,
            "transactions": stitched_transactions,
            "extraction_stats": {
                "pages_processed": total_pages,
                "raw_rows_found": len(raw_rows),
                "stitched_transactions_count": len(stitched_transactions),
                "extraction_mode": "TEXT_PLUMBER"
            }
        }

    @classmethod
    def _parse_table_data(cls, table: List[List[Optional[str]]]) -> List[Dict[str, Any]]:
        """
        Identifies column headers dynamically and extracts cell values.
        """
        if not table or len(table) < 2:
            return []

        col_map = None
        data_rows = []

        for row in table:
            cleaned_row = [str(c).strip() if c is not None else "" for c in row]
            if not any(cleaned_row):
                continue

            # Check if this row is the header
            if col_map is None:
                candidate_map = cls._identify_columns(cleaned_row)
                if candidate_map and "date" in candidate_map:
                    col_map = candidate_map
                    continue

            if col_map is not None:
                if RowStitcher.is_header_row(cleaned_row):
                    continue
                row_dict = cls._map_row_to_dict(cleaned_row, col_map)
                if row_dict:
                    data_rows.append(row_dict)

        return data_rows

    @classmethod
    def _identify_columns(cls, header_cells: List[str]) -> Optional[Dict[str, int]]:
        mapping = {}
        for idx, cell in enumerate(header_cells):
            clean_cell = re.sub(r"[^\w\s]", "", cell.lower()).strip()
            if not clean_cell:
                continue

            for canonical_name, synonyms in cls.COLUMN_SYNONYMS.items():
                if canonical_name in mapping:
                    continue
                for syn in synonyms:
                    if syn in clean_cell or clean_cell in syn:
                        mapping[canonical_name] = idx
                        break

        if "date" in mapping:
            return mapping
        return None

    @classmethod
    def _map_row_to_dict(cls, row_cells: List[str], col_map: Dict[str, int]) -> Optional[Dict[str, Any]]:
        def get_val(col_name: str) -> str:
            if col_name in col_map and col_map[col_name] < len(row_cells):
                return row_cells[col_map[col_name]].strip()
            return ""

        date_val = get_val("date")
        desc_val = get_val("description")
        debit_val = get_val("debit")
        credit_val = get_val("credit")
        balance_val = get_val("balance")

        # Single Amount Column handling
        if not debit_val and not credit_val and "amount" in col_map:
            raw_amt_str = get_val("amount")
            cleaned_amt = RowStitcher.clean_amount(raw_amt_str)
            if "DR" in raw_amt_str.upper() or cleaned_amt < 0:
                debit_val = str(abs(cleaned_amt))
                credit_val = "0.0"
            elif "CR" in raw_amt_str.upper() or cleaned_amt > 0:
                credit_val = str(cleaned_amt)
                debit_val = "0.0"

        return {
            "date": date_val,
            "description": desc_val,
            "debit": debit_val,
            "credit": credit_val,
            "balance": balance_val
        }

    @classmethod
    def _parse_text_lines(cls, text: str) -> List[Dict[str, Any]]:
        """
        Stateful regex parser for lines of text or unbordered tables.
        Handles date extraction, amount & balance unpacking, and narration isolation.
        """
        lines = text.split("\n")
        parsed = []

        date_pattern = re.compile(r"^(\d{1,2}[\/\-\.][A-Za-z0-9]{1,3}[\/\-\.]\d{2,4})")
        trailing_two_amounts = re.compile(r"\s+([0-9,]+\.[0-9]{2})\s+([0-9,]+\.[0-9]{2})$")
        trailing_one_amount = re.compile(r"\s+([0-9,]+\.[0-9]{2})$")

        last_seen_balance = None

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            date_match = date_pattern.match(line_str)
            if date_match:
                date_val = date_match.group(1)
                remainder = line_str[len(date_val):].strip()

                # Check for two trailing amounts (Debit/Credit + Balance)
                two_amt_match = trailing_two_amounts.search(remainder)
                if two_amt_match:
                    amt1_str = two_amt_match.group(1)
                    amt2_str = two_amt_match.group(2)
                    desc_val = remainder[:two_amt_match.start()].strip()

                    parsed_amt = RowStitcher.clean_amount(amt1_str)
                    parsed_bal = RowStitcher.clean_amount(amt2_str)

                    # Directional resolution: use mathematical balance delta if previous balance is known
                    if last_seen_balance is not None and abs(parsed_bal - last_seen_balance) > 0.01:
                        if parsed_bal < last_seen_balance:
                            debit_val = amt1_str
                            credit_val = "0.0"
                        else:
                            debit_val = "0.0"
                            credit_val = amt1_str
                    else:
                        # Fallback to semantic keyword hints
                        is_credit = any(kw in desc_val.upper() for kw in cls.CREDIT_HINTS)
                        if is_credit:
                            debit_val = "0.0"
                            credit_val = amt1_str
                        else:
                            debit_val = amt1_str
                            credit_val = "0.0"

                    last_seen_balance = parsed_bal

                    parsed.append({
                        "date": date_val,
                        "description": desc_val,
                        "debit": debit_val,
                        "credit": credit_val,
                        "balance": amt2_str
                    })
                    continue

                # Check for single trailing amount (e.g. Opening Balance)
                one_amt_match = trailing_one_amount.search(remainder)
                if one_amt_match:
                    amt_str = one_amt_match.group(1)
                    desc_val = remainder[:one_amt_match.start()].strip()
                    parsed_bal = RowStitcher.clean_amount(amt_str)
                    last_seen_balance = parsed_bal

                    parsed.append({
                        "date": date_val,
                        "description": desc_val,
                        "debit": "0.0",
                        "credit": "0.0",
                        "balance": amt_str
                    })
                    continue

                # Date found but no trailing amounts
                parsed.append({
                    "date": date_val,
                    "description": remainder,
                    "debit": "0.0",
                    "credit": "0.0",
                    "balance": "0.0"
                })

            else:
                # Continuation text row (no date at start)
                parsed.append({
                    "date": "",
                    "description": line_str,
                    "debit": "0.0",
                    "credit": "0.0",
                    "balance": "0.0"
                })

        return parsed
