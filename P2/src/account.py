"""
account.py

Defines the Account class.

An Account represents one record loaded from the Current Bank Accounts File.
The front end uses Account objects to check things like:
- Does this account exist?
- Is this account active?
- Who owns this account?
- What is the current balance (in memory for the session)?

"""


class Account:
    """Represents a single bank account in the system."""

    def __init__(self, account_number, account_holder, status, balance):
        """
        Create a new Account object.

        Args:
            account_number: string account number (usually 5 digits)
            account_holder: account holder name
            status: "A" for active or "D" for disabled
            balance: numeric balance for this account
        """
        self.account_number = account_number
        self.account_holder = account_holder
        self.status = status
        self.balance = balance

    def is_active(self):
        """
        Check whether the account is active.

        Returns:
            True if status is "A", otherwise False.
        """
        return self.status == "A"

    def debit(self, amount):
        """
        Subtract money from the account balance (in memory).

        Args:
            amount: numeric amount to subtract
        """
        self.balance = self.balance - amount

    def credit(self, amount):
        """
        Add money to the account balance (in memory).

        Args:
            amount: numeric amount to add
        """
        self.balance = self.balance + amount
