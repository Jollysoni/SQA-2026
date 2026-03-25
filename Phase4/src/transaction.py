"""transaction.py

Defines the Transaction class used by the Phase 4 Back End.

A Transaction object represents one fixed-width record from the merged transaction file.
The object is intentionally simple so the processor can focus on applying business rules.
"""


class Transaction:
    """Stores the data fields for one merged-transaction-file record."""

    def __init__(self, code, account_holder, account_number, amount, misc):
        """Create a Transaction from the five fields parsed from one ATF line.

        Args:
            code:           2-character transaction code (e.g. '01')
            account_holder: account holder name from the ATF record
            account_number: 5-digit account number string
            amount:         transaction amount as a float
            misc:           2-character misc field (company code, transfer suffix, or spaces)
        """
        self.code = code
        self.account_holder = account_holder
        self.account_number = account_number
        self.amount = amount
        self.misc = misc

    def is_end_of_session(self):
        """Return True when this record is the end-of-session marker (code '00')."""
        return self.code == "00"