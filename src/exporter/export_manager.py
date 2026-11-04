import io
import html
import pandas as pd
from typing import List, Dict, Any


class ExportManager:
    """
    Handles exporting processed and classified bank statement data
    into professional formats:
      - Multi-tab Styled Excel (.xlsx) with Forensic Audit Sheet
      - Standard Clean CSV (.csv)
      - Tally Prime / ERP 9 Voucher XML (.xml)
      - QuickBooks / Xero Universal Bank Feed CSV (.csv)
    """

    @classmethod
    def to_csv(cls, transactions: List[Dict[str, Any]]) -> str:
        """
        Converts transactions list into clean standard CSV format.
        """
        df = pd.DataFrame(transactions)
        
        desired_cols = [
            "date", "clean_counterparty", "description", "payment_channel", "reference_number",
            "debit", "credit", "balance", "category", "confidence", "reconciliation_status", "risk_level"
        ]
        cols_to_use = [c for c in desired_cols if c in df.columns]
        export_df = df[cols_to_use] if not df.empty else pd.DataFrame(columns=desired_cols)
        
        col_rename = {
            "date": "Date",
            "clean_counterparty": "Counterparty / Vendor",
            "description": "Raw Narration",
            "payment_channel": "Payment Channel",
            "reference_number": "Reference / UTR",
            "debit": "Debit (INR)",
            "credit": "Credit (INR)",
            "balance": "Balance (INR)",
            "category": "Assigned Category",
            "confidence": "Classification Confidence",
            "reconciliation_status": "Reconciliation Status",
            "risk_level": "Forensic Risk Level"
        }
        export_df = export_df.rename(columns=col_rename)
        return export_df.to_csv(index=False)

    @classmethod
    def to_quickbooks_csv(cls, transactions: List[Dict[str, Any]]) -> str:
        """
        Generates universal QuickBooks Online / Xero bank feed CSV.
        Format: Date, Description, Payee, Amount (Negative for Debit, Positive for Credit)
        """
        rows = []
        for t in transactions:
            debit = float(t.get("debit", 0.0) or 0.0)
            credit = float(t.get("credit", 0.0) or 0.0)
            net_amt = credit - debit
            rows.append({
                "Date": t.get("date", ""),
                "Description": t.get("description", ""),
                "Payee": t.get("clean_counterparty", "N/A"),
                "Amount": round(net_amt, 2),
                "Category": t.get("category", "Uncategorized")
            })
        df_qb = pd.DataFrame(rows)
        return df_qb.to_csv(index=False)

    @classmethod
    def to_tally_xml(cls, transactions: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """
        Generates standard Tally Prime / Tally ERP 9 XML Voucher import format.
        Can be directly imported into Tally via Gateway of Tally > Import Data > Vouchers.
        """
        bank_name = metadata.get("bank_name", "Bank Account")
        
        xml_lines = [
            '<ENVELOPE>',
            '  <HEADER>',
            '    <TALLYREQUEST>Import Data</TALLYREQUEST>',
            '  </HEADER>',
            '  <BODY>',
            '    <IMPORTDATA>',
            '      <REQUESTDESC>',
            '        <REPORTNAME>Vouchers</REPORTNAME>',
            '      </REQUESTDESC>',
            '      <REQUESTDATA>'
        ]

        for i, t in enumerate(transactions, start=1):
            date_str = str(t.get("date", "")).replace("-", "").replace("/", "")
            # Convert DDMMYYYY to YYYYMMDD if needed
            if len(date_str) == 8 and date_str[:2].isdigit():
                tally_date = f"{date_str[4:]}{date_str[2:4]}{date_str[:2]}"
            else:
                tally_date = "20260401"

            debit = float(t.get("debit", 0.0) or 0.0)
            credit = float(t.get("credit", 0.0) or 0.0)
            narration = html.escape(str(t.get("description", "")))
            category = html.escape(str(t.get("category", "General Expense")))
            counterparty = html.escape(str(t.get("clean_counterparty", category)))

            if debit > 0:
                vch_type = "Payment"
                primary_ledger = counterparty
                amt = debit
                sign_1 = ""
                sign_2 = "-"
            else:
                vch_type = "Receipt"
                primary_ledger = counterparty
                amt = credit
                sign_1 = "-"
                sign_2 = ""

            xml_lines.extend([
                f'        <TALLYMESSAGE xmlns:UDF="TallyUDF">',
                f'          <VOUCHER VCHTYPE="{vch_type}" ACTION="Create">',
                f'            <DATE>{tally_date}</DATE>',
                f'            <NARRATION>{narration}</NARRATION>',
                f'            <VOUCHERTYPENAME>{vch_type}</VOUCHERTYPENAME>',
                f'            <VOUCHERNUMBER>{i}</VOUCHERNUMBER>',
                f'            <ALLLEDGERENTRIES.LIST>',
                f'              <LEDGERNAME>{primary_ledger}</LEDGERNAME>',
                f'              <ISDEEMEDPOSITIVE>{"Yes" if debit > 0 else "No"}</ISDEEMEDPOSITIVE>',
                f'              <AMOUNT>{sign_1}{amt:.2f}</AMOUNT>',
                f'            </ALLLEDGERENTRIES.LIST>',
                f'            <ALLLEDGERENTRIES.LIST>',
                f'              <LEDGERNAME>{bank_name}</LEDGERNAME>',
                f'              <ISDEEMEDPOSITIVE>{"No" if debit > 0 else "Yes"}</ISDEEMEDPOSITIVE>',
                f'              <AMOUNT>{sign_2}{amt:.2f}</AMOUNT>',
                f'            </ALLLEDGERENTRIES.LIST>',
                f'          </VOUCHER>',
                f'        </TALLYMESSAGE>'
            ])

        xml_lines.extend([
            '      </REQUESTDATA>',
            '    </IMPORTDATA>',
            '  </BODY>',
            '</ENVELOPE>'
        ])
        return "\n".join(xml_lines)

    @classmethod
    def to_excel_bytes(
        cls, 
        transactions: List[Dict[str, Any]], 
        metadata: Dict[str, Any], 
        summary: Dict[str, Any],
        anomalies: Dict[str, Any] = None
    ) -> bytes:
        """
        Builds a multi-tab formatted Excel workbook:
          1. Account Summary & KPIs
          2. Classified Transaction Ledger
          3. Forensic Audit & Anomaly Intelligence
        """
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            workbook = writer.book

            title_fmt = workbook.add_format({"bold": True, "font_size": 15, "font_color": "#0052CC", "align": "left"})
            sub_title_fmt = workbook.add_format({"italic": True, "font_color": "#64748B", "font_size": 9})
            section_fmt = workbook.add_format({"bold": True, "font_size": 11, "bg_color": "#0052CC", "font_color": "#FFFFFF", "border": 1})
            table_header_fmt = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#0052CC", "align": "center", "valign": "vcenter", "border": 1})
            currency_fmt = workbook.add_format({"num_format": "₹#,##0.00", "border": 1})
            date_fmt = workbook.add_format({"align": "center", "border": 1})
            border_fmt = workbook.add_format({"border": 1})
            bold_label_fmt = workbook.add_format({"bold": True, "border": 1, "bg_color": "#F8FAFC", "font_color": "#0F172A"})

            # ==========================================
            # SHEET 1: Financial Summary & KPIs
            # ==========================================
            summary_sheet = workbook.add_worksheet("Account Summary")
            summary_sheet.hide_gridlines(2)
            summary_sheet.set_column("A:A", 24)
            summary_sheet.set_column("B:B", 36)
            summary_sheet.set_column("D:D", 26)
            summary_sheet.set_column("E:E", 22)

            summary_sheet.write("A1", "befree. | Financial Statement Processing Platform", title_fmt)
            summary_sheet.write("A2", "Autonomous Multi-Bank Ledger Audit & Reconciliation Report", sub_title_fmt)

            summary_sheet.write("A4", "Account Information", section_fmt)
            summary_sheet.write("B4", "", section_fmt)

            meta_rows = [
                ("Bank Name", metadata.get("bank_name", "N/A")),
                ("Account Holder", metadata.get("account_holder", "N/A")),
                ("Account Number", metadata.get("account_number", "N/A")),
                ("IFSC / Branch Code", metadata.get("ifsc_code", "N/A")),
                ("Statement Period", metadata.get("statement_period", "N/A")),
                ("Account Type", metadata.get("account_type", "Standard Retail / Current")),
            ]
            for idx, (label, val) in enumerate(meta_rows, start=5):
                summary_sheet.write(f"A{idx}", label, bold_label_fmt)
                summary_sheet.write(f"B{idx}", val, border_fmt)

            summary_sheet.write("D4", "Financial Health & Audit KPIs", section_fmt)
            summary_sheet.write("E4", "", section_fmt)

            kpi_rows = [
                ("Total Transactions", summary.get("total_transactions", 0), False),
                ("Verified Transactions", summary.get("verified_transactions", 0), False),
                ("Audit Discrepancies", summary.get("discrepancy_count", 0), False),
                ("Ledger Integrity Score", f"{summary.get('integrity_score', 100.0)}%", False),
                ("Reconciliation Status", summary.get("reconciliation_status", "N/A"), False),
                ("Total Credits (Inflow)", summary.get("total_credits", 0.0), True),
                ("Total Debits (Outflow)", summary.get("total_debits", 0.0), True),
                ("Net Cash Flow", summary.get("net_change", 0.0), True),
                ("Opening Balance", summary.get("opening_balance", 0.0), True),
                ("Closing Balance", summary.get("closing_balance", 0.0), True),
            ]
            for idx, (label, val, is_curr) in enumerate(kpi_rows, start=5):
                summary_sheet.write(f"D{idx}", label, bold_label_fmt)
                if is_curr:
                    summary_sheet.write(f"E{idx}", val, currency_fmt)
                else:
                    summary_sheet.write(f"E{idx}", val, border_fmt)

            # ==========================================
            # SHEET 2: Classified Ledger
            # ==========================================
            ledger_sheet = workbook.add_worksheet("Classified Ledger")
            ledger_sheet.set_column("A:A", 12)  # Date
            ledger_sheet.set_column("B:B", 22)  # Counterparty
            ledger_sheet.set_column("C:C", 38)  # Narration
            ledger_sheet.set_column("D:D", 14)  # Channel
            ledger_sheet.set_column("E:E", 14)  # Debit
            ledger_sheet.set_column("F:F", 14)  # Credit
            ledger_sheet.set_column("G:G", 16)  # Balance
            ledger_sheet.set_column("H:H", 24)  # Category
            ledger_sheet.set_column("I:I", 12)  # Confidence
            ledger_sheet.set_column("J:J", 16)  # Audit Status

            headers = [
                "Date", "Counterparty / Vendor", "Particulars / Narration", "Channel",
                "Debit (₹)", "Credit (₹)", "Balance (₹)", "Assigned Category", "Confidence", "Audit Status"
            ]
            for col_idx, h in enumerate(headers):
                ledger_sheet.write(0, col_idx, h, table_header_fmt)

            for row_idx, txn in enumerate(transactions, start=1):
                ledger_sheet.write(row_idx, 0, txn.get("date", ""), date_fmt)
                ledger_sheet.write(row_idx, 1, txn.get("clean_counterparty", "N/A"), border_fmt)
                ledger_sheet.write(row_idx, 2, txn.get("description", ""), border_fmt)
                ledger_sheet.write(row_idx, 3, txn.get("payment_channel", "OTHER"), border_fmt)
                ledger_sheet.write(row_idx, 4, float(txn.get("debit", 0.0) or 0.0), currency_fmt)
                ledger_sheet.write(row_idx, 5, float(txn.get("credit", 0.0) or 0.0), currency_fmt)
                ledger_sheet.write(row_idx, 6, float(txn.get("balance", 0.0) or 0.0), currency_fmt)
                ledger_sheet.write(row_idx, 7, txn.get("category", "General"), border_fmt)
                
                conf = txn.get("confidence", 1.0)
                conf_str = f"{float(conf)*100:.1f}%" if conf is not None else "100.0%"
                ledger_sheet.write(row_idx, 8, conf_str, border_fmt)
                ledger_sheet.write(row_idx, 9, txn.get("reconciliation_status", "VERIFIED"), border_fmt)

            # ==========================================
            # SHEET 3: Forensic Audit & Risk Intelligence
            # ==========================================
            if anomalies:
                audit_sheet = workbook.add_worksheet("Forensic Audit")
                audit_sheet.set_column("A:A", 12)
                audit_sheet.set_column("B:B", 35)
                audit_sheet.set_column("C:C", 14)
                audit_sheet.set_column("D:D", 14)
                audit_sheet.set_column("E:E", 30)
                audit_sheet.set_column("F:F", 16)

                audit_headers = ["Date", "Narration", "Amount (₹)", "Risk Level", "Anomaly Flags", "Tax Tag"]
                for c_idx, ah in enumerate(audit_headers):
                    audit_sheet.write(0, c_idx, ah, table_header_fmt)

                flagged_rows = [t for t in transactions if t.get("has_anomaly")]
                for r_idx, t in enumerate(flagged_rows, start=1):
                    d_amt = float(t.get("debit", 0.0) or 0.0) or float(t.get("credit", 0.0) or 0.0)
                    audit_sheet.write(r_idx, 0, t.get("date", ""), date_fmt)
                    audit_sheet.write(r_idx, 1, t.get("description", ""), border_fmt)
                    audit_sheet.write(r_idx, 2, d_amt, currency_fmt)
                    audit_sheet.write(r_idx, 3, t.get("risk_level", "LOW"), border_fmt)
                    audit_sheet.write(r_idx, 4, ", ".join(t.get("anomaly_flags", [])), border_fmt)
                    audit_sheet.write(r_idx, 5, t.get("tax_tag") or "N/A", border_fmt)

        output.seek(0)
        return output.getvalue()
