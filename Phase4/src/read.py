"""read.py

Defines AccountFileReader for the old master bank accounts file.

Input file format (45 characters per line):
    NNNNN AAAAAAAAAAAAAAAAAAAA S BBBBBBBB TTTT PP

Output:
    A list of Account objects.
"""

from account import Account
from print_error import ErrorLogger


class AccountFileReader:
    """Reads, validates, and converts old master-account records into Account objects."""

    RECORD_LENGTH = 45

    def read_accounts(self, file_path: str) -> list[Account]:
        """Load the old master bank accounts file into a list of Account objects."""
        accounts: list[Account] = []
        seen_account_numbers: set[str] = set()

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

                account = self._parse_account_record(line, line_number, file_path)

                if account.account_holder == "END_OF_FILE":
                    return accounts

                if account.account_number in seen_account_numbers:
                    ErrorLogger.log(
                        f"line {line_number}: duplicate account number {account.account_number}",
                        file_path,
                        fatal=True,
                    )

                seen_account_numbers.add(account.account_number)
                accounts.append(account)

        ErrorLogger.log("missing END_OF_FILE sentinel record", file_path, fatal=True)
        return accounts

    def _parse_account_record(self, line: str, line_number: int, file_path: str) -> Account:
        """Parse one 45-character account record and return the matching Account object."""
        account_number = line[0:5]
        account_holder = line[6:26].strip()
        status = line[27]
        balance_text = line[29:37]
        transaction_count_text = line[38:42]
        plan = line[43:45]

        if not account_number.isdigit():
            ErrorLogger.log(f"line {line_number}: account number must be 5 digits", file_path, fatal=True)

        if status not in {"A", "D"}:
            ErrorLogger.log(f"line {line_number}: invalid account status '{status}'", file_path, fatal=True)

        if len(balance_text) != 8:
            ErrorLogger.log(f"line {line_number}: invalid balance width '{balance_text}'", file_path, fatal=True)

        try:
            balance = float(balance_text)
        except ValueError:
            ErrorLogger.log(f"line {line_number}: invalid balance '{balance_text}'", file_path, fatal=True)
            balance = 0.0

        if balance < 0:
            ErrorLogger.log(f"line {line_number}: negative balance is not allowed", file_path, fatal=True)

        if not transaction_count_text.isdigit():
            ErrorLogger.log(
                f"line {line_number}: transaction count must be 4 digits",
                file_path,
                fatal=True,
            )

        if plan not in {"SP", "NP"}:
            ErrorLogger.log(f"line {line_number}: invalid plan '{plan}'", file_path, fatal=True)

        return Account(
            account_number=account_number,
            account_holder=account_holder,
            status=status,
            balance=balance,
            total_transactions=int(transaction_count_text),
            plan=plan,
        )