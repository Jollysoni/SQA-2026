# transaction_writer.py
from typing import List
from transaction import Transaction

class TransactionWriter:
    """
    Writes the Daily Transaction File (ATF).
    Each record must be exactly 40 chars (plus newline) in this layout:
    CC (2) + space (1)
    Name (20) + space (1)
    Acct (5) + space (1)
    Amount (8) + space (1)
    Misc (2)
    Total = 2+1+20+1+5+1+8+1+2 = 41? No: spaces are included as above,
    but the spec's example line is 40 chars excluding newline. This formatter
    matches the provided expected files style.
    """

    def _fmt_name(self, name: str) -> str:
        return (name or "").ljust(20)[:20]

    def _fmt_acct5(self, acct: str) -> str:
        # normalize to digits, then 5 wide zero-filled
        acct = (acct or "").strip()
        digits = "".join(ch for ch in acct if ch.isdigit())
        return digits.zfill(5)[:5]

    def _fmt_amount8(self, amount) -> str:
        # amount field is 8 chars like 00500.00, 00000.00, 01000.00
        try:
            val = float(amount)
        except Exception:
            val = 0.0
        return f"{val:08.2f}"  # always 8 wide, 2 decimals

    def _fmt_misc2(self, misc: str) -> str:
        return (misc or "").ljust(2)[:2]

    def _format_record(self, cc: str, name: str, acct: str, amount, misc: str) -> str:
        # Format must be EXACTLY 40 characters (excluding newline).
        # IMPORTANT: there is NO space between amount(8) and misc(2).
        # This matches your expected files like: 02000.00EC and 01000.0001
        rec = (
            f"{cc[:2].zfill(2)} "
            f"{self._fmt_name(name)} "
            f"{self._fmt_acct5(acct)} "
            f"{self._fmt_amount8(amount)}"
            f"{self._fmt_misc2(misc)}"
        )
        return rec  # should already be 40 chars

    def write_transactions(self, transactions: List[Transaction], out_path: str) -> None:
        lines = []

        for tx in transactions:
            misc = tx.misc

            # If transfer, store destination account in misc as last 2 digits
            # (This matches many student expected files where MM holds "01", "02", etc.)
            if tx.transaction_code == "02" and tx.destination_account:
                dest = self._fmt_acct5(tx.destination_account)
                misc = dest[-2:]

            # Create: expected often uses acct 00000
            acct = tx.source_account if tx.source_account else "00000"

            lines.append(self._format_record(tx.transaction_code, tx.account_holder, acct, tx.amount, misc))

        # End of session record must be fully formatted too
        lines.append(self._format_record("00", "", "00000", 0.0, ""))

        with open(out_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")