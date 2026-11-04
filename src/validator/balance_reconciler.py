from typing import List, Dict, Any, Tuple


class BalanceReconciler:
    """
    Mathematical Balance Validator:
    Verifies that Balance[i] == Balance[i-1] - Debit[i] + Credit[i].
    Flags OCR reading errors, missing rows, and inverted debit/credit columns.
    """

    TOLERANCE = 0.05  # Floating point tolerance

    @classmethod
    def reconcile(cls, transactions: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Runs row-by-row mathematical audit across the transactions.
        
        Returns:
            - validated_transactions: list with added validation flags
            - reconciliation_summary: dict of overall metrics
        """
        if not transactions:
            return [], {
                "total_transactions": 0,
                "reconciliation_status": "NO_DATA",
                "integrity_score": 100.0,
                "discrepancy_count": 0,
                "total_debits": 0.0,
                "total_credits": 0.0,
                "net_change": 0.0
            }

        validated = []
        discrepancies = 0
        total_debits = 0.0
        total_credits = 0.0

        for i, txn in enumerate(transactions):
            row = dict(txn)
            debit = float(row.get("debit", 0.0) or 0.0)
            credit = float(row.get("credit", 0.0) or 0.0)
            balance = float(row.get("balance", 0.0) or 0.0)

            total_debits += debit
            total_credits += credit

            if i == 0:
                # First transaction row: initial reference point
                row["reconciliation_status"] = "INITIAL_ROW"
                row["expected_balance"] = balance
                row["discrepancy"] = 0.0
                row["is_valid"] = True
            else:
                prev_balance = float(transactions[i - 1].get("balance", 0.0) or 0.0)
                
                # Equation: Current Balance = Previous Balance - Debit + Credit
                expected_balance = prev_balance - debit + credit
                diff = abs(balance - expected_balance)

                if diff <= cls.TOLERANCE or balance == 0.0:
                    row["reconciliation_status"] = "VERIFIED"
                    row["expected_balance"] = round(expected_balance, 2)
                    row["discrepancy"] = round(diff, 2)
                    row["is_valid"] = True
                else:
                    # Mathematical error detected: check for inverted Dr/Cr
                    alt_expected = prev_balance + debit - credit
                    if abs(balance - alt_expected) <= cls.TOLERANCE:
                        status = "DISCREPANCY_INVERTED_DR_CR"
                    else:
                        status = "DISCREPANCY_ARITHMETIC_MISMATCH"

                    discrepancies += 1
                    row["reconciliation_status"] = status
                    row["expected_balance"] = round(expected_balance, 2)
                    row["discrepancy"] = round(diff, 2)
                    row["is_valid"] = False

            validated.append(row)

        total_txns = len(transactions)
        valid_count = total_txns - discrepancies
        integrity_score = round((valid_count / max(total_txns, 1)) * 100.0, 1)

        summary = {
            "total_transactions": total_txns,
            "verified_transactions": valid_count,
            "discrepancy_count": discrepancies,
            "integrity_score": integrity_score,
            "reconciliation_status": "BALANCED" if discrepancies == 0 else "DISCREPANCIES_FOUND",
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "net_change": round(total_credits - total_debits, 2),
            "opening_balance": round(float(transactions[0].get("balance", 0.0) or 0.0), 2) if transactions else 0.0,
            "closing_balance": round(float(transactions[-1].get("balance", 0.0) or 0.0), 2) if transactions else 0.0
        }

        return validated, summary
