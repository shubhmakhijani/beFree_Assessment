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

            for page in pdf.pages:
                full_doc_text.append(page.extract_text() or "")

            # Check if any page has a squashed table (multiple newlines in data cells)
            is_squashed = False
            for p in pdf.pages:
                tables = p.extract_tables()
                for t in tables:
                    if len(t) < 2:
                        continue
                    for r in t[1:]:
                        for cell in r:
                            if cell and str(cell).count('\n') >= 2:
                                is_squashed = True
                                break
                        if is_squashed:
                            break
                    if is_squashed:
                        break
                if is_squashed:
                    break

            if is_squashed:
                # Use high-precision coordinate layout extractor for unbordered bank PDFs
                raw_rows = cls._extract_by_coordinates(pdf)
            else:
                # Standard bordered table extraction + fallback
                for page_idx, page in enumerate(pdf.pages):
                    page_text = full_doc_text[page_idx]

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
                        text_rows = cls._parse_text_lines(page_text)
                        raw_rows.extend(text_rows)

        # Extract metadata from document text
        combined_text = "\n".join(full_doc_text)
        metadata = MetadataParser.extract_metadata(combined_text)

        # Multi-line row stitching & normalization
        stitched_transactions = RowStitcher.stitch_raw_rows(raw_rows)

        # Enrich metadata from extracted transactions if not present
        if stitched_transactions:
            if metadata.get("statement_period") in [None, "Not Specified"]:
                metadata["statement_period"] = f"{stitched_transactions[0]['date']} to {stitched_transactions[-1]['date']}"
            if metadata.get("closing_balance") is None:
                metadata["closing_balance"] = stitched_transactions[-1].get("balance")
            if metadata.get("opening_balance") is None:
                first_bal = float(stitched_transactions[0].get("balance", 0.0) or 0.0)
                first_dr = float(stitched_transactions[0].get("debit", 0.0) or 0.0)
                first_cr = float(stitched_transactions[0].get("credit", 0.0) or 0.0)
                metadata["opening_balance"] = round(first_bal + first_dr - first_cr, 2)

        return {
            "metadata": metadata,
            "transactions": stitched_transactions,
            "extraction_stats": {
                "pages_processed": total_pages,
                "raw_rows_found": len(raw_rows),
                "stitched_transactions_count": len(stitched_transactions),
                "extraction_mode": "COORDINATE_LAYOUT" if is_squashed else "TEXT_PLUMBER"
            }
        }

    @classmethod
    def _extract_by_coordinates(cls, pdf) -> List[Dict[str, Any]]:
        """
        High-precision coordinate-aware extractor for unbordered or partially-bordered
        bank statements (e.g. HDFC, ICICI, SBI, Standard Chartered) where pdfplumber
        extract_tables collapses rows or table borders are absent.
        """
        MONTHS = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)'
        date_regex = re.compile(r"^(\d{1,2}[\/\-\.][A-Za-z0-9]{1,3}[\/\-\.]\d{2,4})")
        amt_regex = re.compile(r"^[0-9,]+\.[0-9]{2}$")

        # Step 1: Detect column boundaries dynamically from header line across pages
        is_deposit_first = False
        mid_boundary = None
        bal_boundary = None

        for p in pdf.pages:
            words = p.extract_words()
            lines = []
            for w in sorted(words, key=lambda x: (x['top'], x['x0'])):
                if not lines or abs(w['top'] - lines[-1]['top']) > 3.5:
                    lines.append({'top': w['top'], 'words': [w]})
                else:
                    lines[-1]['words'].append(w)

            for l in lines:
                l_txt = " ".join(w['text'] for w in l['words']).upper()
                if ('DATE' in l_txt) and any(k in l_txt for k in ['NARRATION', 'PARTICULARS', 'DESCRIPTION', 'REMARKS', 'DETAILS']):
                    with_w = None
                    dep_w = None
                    bal_w = None
                    for w in l['words']:
                        w_clean = re.sub(r'[^a-zA-Z]', '', w['text'].lower())
                        if 'withdraw' in w_clean or 'debit' in w_clean:
                            with_w = w
                        elif 'deposit' in w_clean or 'credit' in w_clean:
                            dep_w = w
                        elif 'closing' in w_clean or 'balance' in w_clean or 'bal' in w_clean:
                            bal_w = w

                    if with_w and dep_w:
                        is_deposit_first = dep_w['x0'] < with_w['x0']
                        col1 = dep_w if is_deposit_first else with_w
                        col2 = with_w if is_deposit_first else dep_w
                        mid_boundary = col2['x0']
                        bal_boundary = bal_w['x0'] if bal_w else col2['x1'] + 50.0
                        break

            if mid_boundary and bal_boundary:
                break

        raw_rows = []
        current_date = ""

        for p in pdf.pages:
            words = p.extract_words()
            lines = []
            for w in sorted(words, key=lambda x: (x['top'], x['x0'])):
                if not lines or abs(w['top'] - lines[-1]['top']) > 3.5:
                    lines.append({'top': w['top'], 'words': [w]})
                else:
                    lines[-1]['words'].append(w)

            header_top = 0
            for l in lines:
                l_txt = " ".join(w['text'] for w in l['words']).upper()
                if ('DATE' in l_txt or 'TXN DATE' in l_txt) and any(k in l_txt for k in ['NARRATION', 'PARTICULARS', 'DESCRIPTION', 'REMARKS', 'DETAILS']):
                    header_top = l['top']
                    break

            table_lines = [l for l in lines if (l['top'] > header_top if header_top else l['top'] > 180) and l['top'] < 790]

            for l in table_lines:
                lw = sorted(l['words'], key=lambda x: x['x0'])
                if not lw:
                    continue
                full_line = " ".join(w['text'] for w in lw).upper()
                condensed = full_line.replace(" ", "")

                # End of transaction table markers
                if any(k in condensed for k in ["STATEMENTSUMMARY", "PAGENO", "REWARDPOINTS", "CLOSINGBALANCEINCLUDES"]):
                    break
                if full_line.startswith("TOTAL ") or full_line == "TOTAL":
                    break

                # Multi-word (3 tokens e.g. '16 Jun 19') vs single-word ('16/06/2019') date detection
                is_3token = (len(lw) >= 3 and re.match(r'^\d{1,2}$', lw[0]['text']) and 
                             re.match(rf'^{MONTHS}', lw[1]['text'], re.I) and 
                             re.match(r'^\d{2,4}$', lw[2]['text']))
                is_1token = bool(date_regex.match(lw[0]['text']))

                date_val = ""
                content_start_idx = 0

                if is_3token:
                    date_val = f"{lw[0]['text']} {lw[1]['text']} {lw[2]['text']}"
                    current_date = date_val
                    content_start_idx = 3
                    # Check if next 3 words are value date
                    if len(lw) >= 6 and re.match(r'^\d{1,2}$', lw[3]['text']) and re.match(rf'^{MONTHS}', lw[4]['text'], re.I) and re.match(r'^\d{2,4}$', lw[5]['text']):
                        content_start_idx = 6
                elif is_1token:
                    date_val = date_regex.match(lw[0]['text']).group(1)
                    current_date = date_val
                    content_start_idx = 1
                    # Check if next word is value date
                    if len(lw) >= 2 and date_regex.match(lw[1]['text']):
                        content_start_idx = 2

                # Find decimal amount words
                amt_words = [w for w in lw if amt_regex.match(w['text'].replace('Cr', '').replace('Dr', '').strip())]

                debit_val = "0.0"
                credit_val = "0.0"
                bal_val = "0.0"

                if mid_boundary and bal_boundary:
                    for w in amt_words:
                        val_str = w['text'].replace(',', '')
                        if w['x1'] <= mid_boundary:
                            if is_deposit_first:
                                credit_val = val_str
                            else:
                                debit_val = val_str
                        elif w['x1'] <= bal_boundary:
                            if is_deposit_first:
                                debit_val = val_str
                            else:
                                credit_val = val_str
                        else:
                            bal_val = val_str
                else:
                    if len(amt_words) == 2:
                        bal_val = amt_words[1]['text'].replace(',', '')
                        if any(k in full_line for k in ['CR', 'CREDIT', 'DEP', 'SALARY', 'REFUND']):
                            credit_val = amt_words[0]['text'].replace(',', '')
                        else:
                            debit_val = amt_words[0]['text'].replace(',', '')
                    elif len(amt_words) >= 3:
                        debit_val = amt_words[0]['text'].replace(',', '')
                        credit_val = amt_words[1]['text'].replace(',', '')
                        bal_val = amt_words[2]['text'].replace(',', '')

                # Determine if this row represents a new transaction or a continuation
                has_balance = float(bal_val.replace(',', '')) > 0
                has_amt = float(debit_val.replace(',', '')) > 0 or float(credit_val.replace(',', '')) > 0

                desc_words = [w['text'] for w in lw[content_start_idx:] if w not in amt_words and not date_regex.match(w['text']) and not re.match(r"^\d{14,20}$", w['text'])]
                desc_text = " ".join(desc_words)

                # Skip opening balance / balance forward rows from being counted as transactions
                if "BALANCE FORWARD" in desc_text.upper() or "BROUGHT FORWARD" in desc_text.upper():
                    continue

                if date_val or (has_amt and has_balance and current_date):
                    txn_date = date_val if date_val else current_date
                    raw_rows.append({
                        'date': txn_date,
                        'description': desc_text,
                        'debit': debit_val,
                        'credit': credit_val,
                        'balance': bal_val
                    })
                else:
                    raw_rows.append({
                        'date': '',
                        'description': desc_text if desc_text else " ".join(w['text'] for w in lw),
                        'debit': '0.0',
                        'credit': '0.0',
                        'balance': '0.0'
                    })

        return raw_rows

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
