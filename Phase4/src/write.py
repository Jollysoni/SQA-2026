"""write.py

Defines AccountFileWriter for the new master bank accounts file.

Output file format (45 characters per line):
    NNNNN AAAAAAAAAAAAAAAAAAAA S BBBBBBBB TTTT PP
"""

from account import Account


class AccountFileWriter:
    """Formats and writes Account objects to the new master-account output file."""

    def write_accounts(self, accounts, file_path):
        """Write all account records followed by the END_OF_FILE sentinel record.

        Args:
            accounts:  list of Account objects to write
            file_path: output path for the new master bank accounts file
        """
        with open(file_path, "w", encoding="utf-8") as output_file:
            for account in accounts:
                output_file.write(account.to_record() + "\n")
            output_file.write(self._end_of_file_record() + "\n")

    def _end_of_file_record(self):
        """Return the fixed-width END_OF_FILE sentinel record."""
        return "00000 END_OF_FILE          A 00000.00 0000 NP"