"""
account_store.py

Defines AccountStore, which loads and stores all accounts for the session.

AccountStore reads the Current Bank Accounts File and builds Account objects.
Then the front end can quickly look up accounts by account number.

This keeps file parsing in one place and makes the rest of the code easier to read.
"""

from account import Account


class AccountStore:
    """Loads accounts from file and provides lookup helper methods."""

    def __init__(self):
        """
        Create an empty AccountStore.

        accounts is a dictionary:
            key: account number (string)
            value: Account object
        """
        self.accounts = {}

    def load_accounts(self, file_path):
        """
        Read the current accounts file and store each account in memory.

        Args:
            file_path: path to the Current Bank Accounts File

        Notes:
            Stops reading when it reaches the END_OF_FILE record.
            Ignores blank lines.
        """
        self.accounts = {}

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line == "":
                    continue

                # Stop reading at END_OF_FILE
                name_field = line[6:26].strip()
                if name_field == "END_OF_FILE":
                    break

                # Parse fixed width fields (simple parsing for Phase 2)
                account_number = line[0:5].strip()
                name = line[6:26].strip()
                status = line[27].strip()
                balance_text = line[29:].strip()

                balance = float(balance_text) if balance_text else 0.0

                account = Account(account_number, name, status, balance)
                self.accounts[account_number] = account

    def find_account(self, account_number):
        """
        Find an account by account number.

        Args:
            account_number: string account number to search for

        Returns:
            Account object if found, otherwise None.
        """
        return self.accounts.get(account_number)

    def account_exists(self, account_number):
        """
        Check if an account number exists in memory.

        Args:
            account_number: string account number to check

        Returns:
            True if present, otherwise False.
        """
        return account_number in self.accounts

    def is_owner(self, user_name, account_number):
        """
        Check if the given user name matches the owner of the account.

        Args:
            user_name: account holder name from the current session
            account_number: account number to check ownership for

        Returns:
            True if the account exists and belongs to the user, otherwise False.
        """
        account = self.find_account(account_number)
        if account is None:
            return False

            return account.account_holder == user_name
    
        def is_disabled(self, account_number):
            """
            Returns True if the account exists and its status is Disabled (D).
            If the account does not exist, treat it as disabled for safety.
            """
            acct = self.find_account(account_number)
            if acct is None:
                return True
            return acct.status == "D"

    def get_balance(self, account_number):
        """
        Get the current in-memory balance for an account.
        Returns None if the account does not exist.
        """
        acct = self.find_account(account_number)
        if acct is None:
            return None
        return acct.balance

    def set_balance(self, account_number, new_balance):
        """
        Update the in-memory balance for an account.
        Does nothing if the account does not exist.
        """
        acct = self.find_account(account_number)
        if acct is None:
            return
        acct.balance = float(new_balance)

    def owner_name(self, account_number):
        """
        Return the owner name for an account, or None if not found.
        """
        acct = self.find_account(account_number)
        if acct is None:
            return None
        return acct.account_holder