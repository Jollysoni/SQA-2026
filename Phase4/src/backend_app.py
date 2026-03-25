"""backend_app.py

Defines BackendApp, the main controller for the Phase 4 Back End.

The controller coordinates the full back-end pipeline:
1. read old master accounts,
2. read merged transactions,
3. process transactions in order,
4. write the new master accounts file.
"""

from process import TransactionProcessor
from read import AccountFileReader
from read_transactions import TransactionFileReader
from write import AccountFileWriter


class BackendApp:
    """Coordinates the back-end file-processing workflow from start to finish."""

    def __init__(self) -> None:
        """Create the reader, processor support, and writer dependencies for one run."""
        self.account_reader = AccountFileReader()
        self.transaction_reader = TransactionFileReader()
        self.account_writer = AccountFileWriter()

    def run(self, old_master_accounts_file: str, merged_transaction_file: str, new_master_accounts_file: str) -> None:
        """Execute the complete back-end workflow using the provided input and output files."""
        accounts = self.account_reader.read_accounts(old_master_accounts_file)
        transactions = self.transaction_reader.read_transactions(merged_transaction_file)
        processor = TransactionProcessor(accounts)
        updated_accounts = processor.process_transactions(transactions)
        self.account_writer.write_accounts(updated_accounts, new_master_accounts_file)