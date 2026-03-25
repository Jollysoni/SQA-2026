"""read_transactions.py

Defines TransactionFileReader for the merged transaction file.

Input file format (40 characters per line):
    CC AAAAAAAAAAAAAAAAAAAA NNNNN BBBBBBBBMM

Output:
    A list of Transaction objects. End-of-session records are ignored after validation.
"""

from print_error import ErrorLogger
from transaction import Transaction


class TransactionFileReader:
    """Reads, validates, and converts merged transaction records into Transaction objects."""

    RECORD_LENGTH = 40
    VALID_CODES = {"00", "01", "02", "03", "04", "05", "06", "07", "08"}

    def read_transactions(self, file_path):
        """Load the merged transaction file into a list of Transaction objects.

        Args:
            file_path: path to the merged ATF file
        Returns:
            list of Transaction objects (end-of-session records excluded)
        """
        transactions = []

        with open(file_path, "r", encoding="utf-8") as source_file:
            for line_number, raw_line in enumerate(source_file, start=1):
                line = raw_line.rstrip("\n")

                if not line.strip():
                    ErrorLogger.log(f"line {line_number}: blank line is not allowed", file_path, fatal=True)

                if len(line) != self.RECORD_LENGTH:
                    ErrorLogger.log(
                        f"line {line_number}: invalid length ({len(line)} chars, expected {self.RECORD_LENGTH})",
                        file_path,
                        fatal=True,
                    )

                transaction = self._parse_transaction_record(line, line_number, file_path)
                if not transaction.is_end_of_session():
                    transactions.append(transaction)

        return transactions

    def _parse_transaction_record(self, line, line_number, file_path):
        """Parse one 40-character transaction record and return the matching Transaction object.

        Args:
            line:        40-character string from the ATF
            line_number: current line number (used in error messages)
            file_path:   path to the ATF file (used in error messages)
        Returns:
            Transaction object
        """
        code = line[0:2]
        account_holder = line[3:23].strip()
        account_number = line[24:29]
        amount_text = line[30:38]
        misc = line[38:40]

        if code not in self.VALID_CODES:
            ErrorLogger.log(f"line {line_number}: invalid transaction code '{code}'", file_path, fatal=True)

        if not account_number.isdigit():
            ErrorLogger.log(f"line {line_number}: account number must be 5 digits", file_path, fatal=True)

        try:
            amount = float(amount_text)
        except ValueError:
            ErrorLogger.log(f"line {line_number}: invalid amount '{amount_text}'", file_path, fatal=True)
            amount = 0.0

        if amount < 0:
            ErrorLogger.log(f"line {line_number}: negative amount is not allowed", file_path, fatal=True)

        self._validate_transaction_fields(code, account_holder, account_number, amount, misc, line_number, file_path)

        return Transaction(
            code=code,
            account_holder=account_holder,
            account_number=account_number,
            amount=amount,
            misc=misc,
        )

    def _validate_transaction_fields(self, code, account_holder, account_number, amount, misc, line_number, file_path):
        """Check transaction fields against the rules implied by each transaction code.

        Args:
            code:           2-character transaction code
            account_holder: account holder name string
            account_number: 5-digit account number string
            amount:         transaction amount as float
            misc:           2-character misc field
            line_number:    current line number (used in error messages)
            file_path:      path to the ATF file (used in error messages)
        """
        if code == "00":
            if account_number != "00000" or amount != 0.0:
                ErrorLogger.log(
                    f"line {line_number}: invalid end-of-session record",
                    file_path,
                    fatal=True,
                )
            return

        if code in {"01", "04", "06", "07", "08"} and misc.strip() != "":
            ErrorLogger.log(f"line {line_number}: misc field must be blank for code {code}", file_path, fatal=True)

        if code == "02":
            if not misc.isdigit():
                ErrorLogger.log(
                    f"line {line_number}: transfer destination suffix must be 2 digits",
                    file_path,
                    fatal=True,
                )

        if code == "03" and misc.strip() not in {"EC", "CQ", "FI"}:
            ErrorLogger.log(
                f"line {line_number}: invalid bill company '{misc}'",
                file_path,
                fatal=True,
            )

        if code == "05":
            if account_number != "00000":
                ErrorLogger.log(
                    f"line {line_number}: create transactions must use account number 00000",
                    file_path,
                    fatal=True,
                )
            if not account_holder:
                ErrorLogger.log(
                    f"line {line_number}: create transactions require an account holder name",
                    file_path,
                    fatal=True,
                )