"""main.py

Phase 4 Back End Banking System main program.

Overall purpose:
    Read the old master bank accounts file and merged transaction file,
    apply all transactions in order, and write the new master bank accounts file.

Input files:
    1. Old Master Bank Accounts File
    2. Merged Transaction File

Output file:
    1. New Master Bank Accounts File

How to run:
    python3 main.py <old_master_accounts_file> <merged_transaction_file> <new_master_accounts_file>
"""

import sys

from backend_app import BackendApp
from print_error import ErrorLogger


def main() -> None:
    """Validate command-line arguments and run the Phase 4 back-end controller."""
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <old_master_accounts_file> <merged_transaction_file> <new_master_accounts_file>")
        sys.exit(1)

    old_master_accounts_file = sys.argv[1]
    merged_transaction_file = sys.argv[2]
    new_master_accounts_file = sys.argv[3]

    try:
        BackendApp().run(old_master_accounts_file, merged_transaction_file, new_master_accounts_file)
    except FileNotFoundError as error:
        ErrorLogger.log(f"file not found ({error.filename})", error.filename or "input", fatal=True)


if __name__ == "__main__":
    main()