"""
transaction.py

Defines the Transaction class.

A Transaction is created when the front end accepts a command.
Transactions are stored in a list during the session.
On logout, TransactionWriter converts each Transaction into a 40 character record
and writes the Daily Transaction File (Bank Account Transaction File).
"""


class Transaction:
    """Stores data for one accepted transaction (one record in the output file)."""

    def __init__(
        self,
        transaction_code,
        account_holder,
        source_account,
        amount,
        misc="",
        destination_account=""
    ):
        """
        Create a new Transaction object.

        Args:
            transaction_code: 2 digit transaction code as a string (example: "01")
            account_holder: name tied to the transaction
            source_account: main account number for the transaction
            amount: numeric amount for the transaction
            misc: extra info (example: bill company code)
            destination_account: destination account number for transfers
        """
        self.transaction_code = transaction_code
        self.account_holder = account_holder
        self.source_account = source_account
        self.destination_account = destination_account
        self.amount = amount
        self.misc = misc
