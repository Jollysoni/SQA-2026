"""account.py

Defines the Account class used by the Phase 4 Back End.

An Account object represents one record from the old/new master bank accounts file.
The object stores the fixed-width file fields in a clear in-memory form and provides
small helper methods used by the transaction processor.
"""


class Account:
    """Represents one bank account record in the back-end system."""

    def __init__(self, account_number, account_holder, status, balance, total_transactions, plan):
        """Create an Account from the six fields of one BAF record.

        Args:
            account_number:     5-digit zero-padded account number string
            account_holder:     account holder name
            status:             'A' (active) or 'D' (disabled)
            balance:            current account balance as a float
            total_transactions: cumulative transaction count as an int
            plan:               'SP' (student plan) or 'NP' (non-plan)
        """
        self.account_number = account_number
        self.account_holder = account_holder
        self.status = status
        self.balance = balance
        self.total_transactions = total_transactions
        self.plan = plan

    def is_active(self):
        """Return True when the account is active and can accept normal transactions."""
        return self.status == "A"

    def debit(self, amount):
        """Subtract the provided amount from the balance."""
        self.balance -= amount

    def credit(self, amount):
        """Add the provided amount to the balance."""
        self.balance += amount

    def disable(self):
        """Mark the account as disabled."""
        self.status = "D"

    def toggle_plan(self):
        """Switch the account plan between SP and NP."""
        self.plan = "NP" if self.plan == "SP" else "SP"

    def increment_transaction_count(self):
        """Increase the total transaction count by one."""
        self.total_transactions += 1

    def to_record(self):
        """Return the fixed-width 45-character master-account record for this account."""
        account_number = self.account_number.zfill(5)
        account_holder = self.account_holder[:20].ljust(20)
        balance = f"{self.balance:08.2f}"
        total_transactions = str(self.total_transactions).zfill(4)
        return f"{account_number} {account_holder} {self.status} {balance} {total_transactions} {self.plan}"