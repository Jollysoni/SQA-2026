"""
frontend_app.py

Front End Banking System - Phase 2 Prototype

Purpose:
This console program simulates an ATM style front end. It reads transaction
commands from standard input, applies basic session rules, and records accepted
transactions. When the user logs out, it writes the Daily Transaction File
(also called the Bank Account Transaction File).

Inputs:
- Standard input: transaction commands (one per line)
- Current Bank Accounts File: loaded into memory after login

Outputs:
- Standard output: prompts and error or success messages
- Daily Transaction File / Bank Account Transaction File: written on logout

How to run:
python3 frontend_app.py <current_accounts_file> <output_transaction_file> < input.txt > output.txt
"""

import sys
from session import Session
from account_store import AccountStore
from transaction import Transaction
from transaction_writer import TransactionWriter


class FrontEndApp:
    """Main controller class for the front end application."""

    def __init__(self, accounts_file_path, output_tx_file_path):
        """
        Create a new FrontEndApp.

        Args:
            accounts_file_path: path to the Current Bank Accounts File
            output_tx_file_path: path to the Daily Transaction File output
        """
        self.accounts_file_path = accounts_file_path
        self.output_tx_file_path = output_tx_file_path

        # Session tracks login state and mode (standard or admin).
        self.session = Session()

        # AccountStore holds accounts loaded from the accounts file.
        self.account_store = AccountStore()

        # Keep accepted transactions in memory until logout.
        self.transactions = []
                # Track how much the standard user has done in this session.
        # Limits from the spec:
        # withdrawal max $500, transfer max $1000, paybill max $2000 (standard mode only).
        self.session_withdraw_total = 0.0
        self.session_transfer_total = 0.0
        self.session_paybill_total = 0.0

        # Track “available balance” during this session.
        # Deposits do NOT increase this value (deposit not available until next session).
        self.available_balances = {}

        # Track deleted accounts (once deleted, nothing else should work on them).
        self.deleted_accounts = set()

        # TransactionWriter writes the output transaction file on logout.
        self.tx_writer = TransactionWriter()

    def run(self):
        """
        Main program loop.

        Reads one command per line from standard input.
        Each command is dispatched to a handler method.
        """
        while True:
            code = sys.stdin.readline()
            if code == "":
                # End of input stream
                break

            code = code.strip().lower()
            if code == "":
                # Ignore blank lines
                continue

            self.dispatch_transaction(code)

    def dispatch_transaction(self, code):
        """
        Route a transaction code to the correct handler.

        Args:
            code: lowercase command string like "login" or "withdrawal"
        """
        if code == "login":
            self.handle_login()
        elif code == "logout":
            self.handle_logout()
        elif code == "withdrawal":
            self.handle_withdrawal()
        elif code == "deposit":
            self.handle_deposit()
        elif code == "transfer":
            self.handle_transfer()
        elif code == "paybill":
            self.handle_paybill()
        elif code == "create":
            self.handle_create()
        elif code == "delete":
            self.handle_delete()
        elif code == "disable":
            self.handle_disable()
        elif code == "changeplan":
            self.handle_changeplan()
        else:
            print("ERROR: Unknown transaction.")

    def handle_login(self):
        """
        Handle the login command.

        Steps:
        - Ask for session type (standard or admin)
        - If standard, ask for the account holder name
        - Load the accounts file into memory
        - Mark the session as started
        """
        if self.session.logged_in:
            print("ERROR: Already logged in.")
            return

        print("Enter session type (standard/admin):")
        mode = sys.stdin.readline().strip().lower()

        user = ""
        if mode == "standard":
            print("Enter account holder name:")
            user = sys.stdin.readline().strip()

        if mode not in ["standard", "admin"]:
            print("ERROR: Invalid session type.")
            return

        # Start session first so later logic can check state.
        self.session.start(mode, user)

        try:
            self.account_store.load_accounts(self.accounts_file_path)
        except Exception:
            print("ERROR: Could not load accounts file.")
            self.session.end()
            return

        print("Login successful.")
                # Reset per-session totals
        self.session_withdraw_total = 0.0
        self.session_transfer_total = 0.0
        self.session_paybill_total = 0.0
        self.deleted_accounts = set()

        # Build a quick lookup for available balances at session start
        self.available_balances = {}
        for acct_num, acct_obj in self.account_store.accounts.items():
            self.available_balances[acct_num] = float(acct_obj.balance)

    def handle_logout(self):
        """
        Handle the logout command.

        Writes all stored transactions to the output transaction file,
        adds an end of session record, then ends the session.
        """
        if not self.session.logged_in:
            print("ERROR: Not logged in.")
            return

        self.tx_writer.write_transactions(self.transactions, self.output_tx_file_path)
        self.session.end()
        print("Logged out.")

    def handle_withdrawal(self):
        """
        Handle a withdrawal transaction.

        Reads:
        - account holder name (admin only)
        - account number
        - amount

        Records the transaction in memory.
        """
        if not self.session.can_perform("withdrawal"):
            print("ERROR: Not allowed.")
            return

        name = self.get_name_if_admin()

        print("Enter account number:")
        acct = sys.stdin.readline().strip()

        print("Enter amount:")
        amount = self.read_amount()

        if not self.session.is_admin():
            if self.session_withdraw_total + amount > 500.0:
                print("ERROR: Standard withdrawal limit exceeded.")
                return

        if self._reject_if_invalid_account_for_user(name, acct):
            return

        if self._reject_if_insufficient_available_funds(acct, amount):
            return

        # If we reached here, accept the transaction
        tx = Transaction("01", name, acct, amount)
        self.transactions.append(tx)

        # Update session totals and available balance
        if not self.session.is_admin():
            self.session_withdraw_total += amount

        self.available_balances[acct] -= amount

        print("Withdrawal recorded.")

    def handle_deposit(self):
        """
        Handle a deposit transaction.

        Reads:
        - account holder name (admin only)
        - account number
        - amount
        Validates account first.
        Deposit is recorded but does NOT increase available balance in this session.
        """
        if not self.session.can_perform("deposit"):
            print("ERROR: Not allowed.")
            return

        name = self.get_name_if_admin()

        print("Enter account number:")
        acct = sys.stdin.readline().strip()

        print("Enter amount:")
        amount = self.read_amount()

        # --- Validation ---

        # Must be valid account, not deleted, not disabled,
        # and owned by user if standard mode
        if self._reject_if_invalid_account_for_user(name, acct):
            return

        # --- Accepted: record transaction ---
        tx = Transaction("04", name, acct, amount)
        self.transactions.append(tx)

        # IMPORTANT:
        # We do NOT update self.available_balances here.
        # Deposited funds are not available in this session.

        print("Deposit recorded.")
    def handle_transfer(self):
        """
        Handle a transfer transaction.

        Reads:
        - account holder name (admin only)
        - from account number
        - to account number
        - amount

        Records the transaction in memory.
        """
        if not self.session.can_perform("transfer"):
            print("ERROR: Not allowed.")
            return

        name = self.get_name_if_admin()

        print("Enter from account number:")
        from_acct = sys.stdin.readline().strip()

        print("Enter to account number:")
        to_acct = sys.stdin.readline().strip()

        print("Enter amount:")
        amount = self.read_amount()

               # Standard mode limit: max $1000 per session
        if not self.session.is_admin():
            if self.session_transfer_total + amount > 1000.0:
                print("ERROR: Standard transfer limit exceeded.")
                return

        # Source account must be valid for user
        if self._reject_if_invalid_account_for_user(name, from_acct):
            return

        # Destination must exist in the bank system (spec requirement)
        if not self.account_store.account_exists(to_acct):
            print("ERROR: Destination account does not exist.")
            return

        # Source must not go negative
        if self._reject_if_insufficient_available_funds(from_acct, amount):
            return

        tx = Transaction("02", name, from_acct, amount, destination_account=to_acct)
        self.transactions.append(tx)

        if not self.session.is_admin():
            self.session_transfer_total += amount

        # Money leaves source immediately in this session view
        self.available_balances[from_acct] -= amount

        # We do not need to add to destination available balance for these tests
        # because deposits are not usable anyway and adding cannot cause negative.
        print("Transfer recorded.")

    def handle_paybill(self):
        """
        Handle a paybill transaction.

        Reads:
        - account holder name (admin only)
        - account number
        - company code (example: EC, CQ, FI)
        - amount

        Records the transaction in memory.
        """
        if not self.session.can_perform("paybill"):
            print("ERROR: Not allowed.")
            return

        name = self.get_name_if_admin()

        print("Enter account number:")
        acct = sys.stdin.readline().strip()

        print("Enter company code (EC/CQ/FI):")
        company = sys.stdin.readline().strip().upper()

        print("Enter amount:")
        amount = self.read_amount()

                # Company must be one of EC/CQ/FI
        if company not in ["EC", "CQ", "FI"]:
            print("ERROR: Invalid bill company.")
            return

        # Standard mode limit: max $2000 per session
        if not self.session.is_admin():
            if self.session_paybill_total + amount > 2000.0:
                print("ERROR: Standard paybill limit exceeded.")
                return

        if self._reject_if_invalid_account_for_user(name, acct):
            return

        if self._reject_if_insufficient_available_funds(acct, amount):
            return

        tx = Transaction("03", name, acct, amount, misc=company)
        self.transactions.append(tx)

        if not self.session.is_admin():
            self.session_paybill_total += amount

        self.available_balances[acct] -= amount

        print("Paybill recorded.")

    def handle_create(self):
        """
        Handle the create transaction (admin only).

        Reads:
        - new account holder name
        - initial balance

        Records the transaction in memory.
        """
        if not self.session.can_perform("create"):
            print("ERROR: Not allowed.")
            return

        print("Enter new account holder name:")
        name = sys.stdin.readline().strip()

        print("Enter initial balance:")
        amount = self.read_amount()

        tx = Transaction("05", name, "", amount)
        self.transactions.append(tx)

        print("Create recorded.")

    def handle_delete(self):
        """
        Handle the delete transaction (admin only).

        Reads:
        - account holder name
        - account number

        Records the transaction in memory.
        """
        if not self.session.can_perform("delete"):
            print("ERROR: Not allowed.")
            return

        print("Enter account holder name:")
        name = sys.stdin.readline().strip()

        print("Enter account number:")
        acct = sys.stdin.readline().strip()

        tx = Transaction("06", name, acct, 0)
        self.transactions.append(tx)

        print("Delete recorded.")

    def handle_disable(self):
        """
        Handle the disable transaction (admin only).

        Reads:
        - account holder name
        - account number

        Records the transaction in memory.
        """
        if not self.session.can_perform("disable"):
            print("ERROR: Not allowed.")
            return

        print("Enter account holder name:")
        name = sys.stdin.readline().strip()

        print("Enter account number:")
        acct = sys.stdin.readline().strip()

        tx = Transaction("07", name, acct, 0)
        self.transactions.append(tx)

        print("Disable recorded.")

    def handle_changeplan(self):
        """
        Handle the changeplan transaction (admin only).

        Reads:
        - account holder name
        - account number

        Records the transaction in memory.
        """
        if not self.session.can_perform("changeplan"):
            print("ERROR: Not allowed.")
            return

        print("Enter account holder name:")
        name = sys.stdin.readline().strip()

        print("Enter account number:")
        acct = sys.stdin.readline().strip()

        tx = Transaction("08", name, acct, 0)
        self.transactions.append(tx)

        print("Changeplan recorded.")

    def get_name_if_admin(self):
        """
        Get the account holder name for the transaction.

        In admin mode, the system asks for the account holder name.
        In standard mode, it uses the logged in user name.

        Returns:
            The account holder name string.
        """
        if self.session.is_admin():
            print("Enter account holder name:")
            return sys.stdin.readline().strip()
        return self.session.current_user

    def read_amount(self):
        """
        Read an amount from standard input and convert it to float.

        Returns:
            float value of the input, or 0.0 if parsing fails.
        """
        text = sys.stdin.readline().strip()
        try:
            return float(text)
        except Exception:
            return 0.0

    def _reject_if_invalid_account_for_user(self, name, acct_num):
        """
        Returns True if validation failed (and prints the error).
        This checks:
        - account exists
        - not deleted
        - not disabled
        - belongs to the user if in standard mode
        """
        if not self.account_store.account_exists(acct_num):
            print("ERROR: Account does not exist.")
            return True

        if acct_num in self.deleted_accounts:
            print("ERROR: Account was deleted this session.")
            return True

        if self.account_store.is_disabled(acct_num):
            print("ERROR: Account is disabled.")
            return True

        # If standard session, user can only use their own accounts
        if not self.session.is_admin():
            if not self.account_store.is_owner(self.session.current_user, acct_num):
                print("ERROR: Account does not belong to the logged in user.")
                return True
        else:
            # Admin session: still validate that the provided name matches the owner
            # This matches the idea of "withdrawal should ask for account holder’s name (admin only)"
            actual_owner = self.account_store.owner_name(acct_num)
            if actual_owner is not None and actual_owner != name:
                print("ERROR: Account holder name does not match that account.")
                return True

        return False

    def _reject_if_insufficient_available_funds(self, acct_num, amount):
        """
        Returns True if the withdrawal/transfer/paybill would make balance negative.
        We use available_balances, which updates during session.
        Deposits do not increase available funds.
        """
        current = self.available_balances.get(acct_num, None)
        if current is None:
            print("ERROR: Account does not exist.")
            return True

        if current - amount < 0.0:
            print("ERROR: Insufficient funds (would go negative).")
            return True

        return False


def main():
    """
    Program entry point.

    Expects exactly 2 command line arguments:
    1) current accounts file path
    2) output transaction file path
    """
    if len(sys.argv) != 3:
        print("Usage: python3 frontend_app.py <current_accounts_file> <output_transaction_file>")
        return

    accounts_file = sys.argv[1]
    output_file = sys.argv[2]

    app = FrontEndApp(accounts_file, output_file)
    app.run()


if __name__ == "__main__":
    main()
