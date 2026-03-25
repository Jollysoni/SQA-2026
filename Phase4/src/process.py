"""process.py

Defines TransactionProcessor for the Phase 4 Back End.

Input:
    A list of Account objects and a list of Transaction objects.
Output:
    An updated list of Account objects sorted by account number.
"""

import account
from account import Account
from print_error import ErrorLogger
from transaction import Transaction


class TransactionProcessor:
    """Applies merged transaction records to the in-memory collection of accounts."""

    VALID_BILL_COMPANIES = {"EC", "CQ", "FI"}

    def __init__(self, accounts: list[Account]) -> None:
        """Store the current account set in a dictionary for efficient updates."""
        self.accounts_by_number: dict[str, Account] = {account.account_number: account for account in accounts}

    def process_transactions(self, transactions: list[Transaction]) -> list[Account]:
        """Apply every transaction in order and return the resulting accounts in sorted order."""
        for transaction in transactions:
            self._dispatch_transaction(transaction)
        return self.get_sorted_accounts()

    def get_sorted_accounts(self) -> list[Account]:
        """Return all current accounts sorted by account number."""
        return sorted(self.accounts_by_number.values(), key=lambda account: account.account_number)

    def _dispatch_transaction(self, transaction: Transaction) -> None:
        """Route one transaction object to the correct handler."""
        if transaction.code == "01":
            self._apply_withdrawal(transaction)
        elif transaction.code == "02":
            self._apply_transfer(transaction)
        elif transaction.code == "03":
            self._apply_paybill(transaction)
        elif transaction.code == "04":
            self._apply_deposit(transaction)
        elif transaction.code == "05":
            self._apply_create(transaction)
        elif transaction.code == "06":
            self._apply_delete(transaction)
        elif transaction.code == "07":
            self._apply_disable(transaction)
        elif transaction.code == "08":
            self._apply_change_plan(transaction)
        else:
            ErrorLogger.log(f"unknown transaction code '{transaction.code}'", "transaction processor")

    def _apply_withdrawal(self, transaction: Transaction) -> None:
        """Apply a withdrawal when the account exists, is active, and has enough funds."""
        account = self._get_existing_account(transaction.account_number, "withdrawal")
        if account is None or not self._ensure_active(account, "withdrawal"):
            return
        if account.balance < transaction.amount:
            ErrorLogger.log(f"insufficient funds in account {account.account_number}", "withdrawal")
            return

        account.debit(transaction.amount)
        account.increment_transaction_count()
        self._apply_transaction_fee(account)

    def _apply_transfer(self, transaction: Transaction) -> None:
        """Apply a transfer by debiting the source account and crediting one unique destination account."""
        source_account = self._get_existing_account(transaction.account_number, "transfer")
        if source_account is None or not self._ensure_active(source_account, "transfer"):
            return
        destination_account = self._find_unique_destination_account(transaction.misc)
        if destination_account is None:
            return
        if not self._ensure_active(destination_account, "transfer"):
            return
        if source_account.balance < transaction.amount:
            ErrorLogger.log(f"insufficient funds in account {source_account.account_number}", "transfer")
            return

        source_account.debit(transaction.amount)
        destination_account.credit(transaction.amount)
        source_account.increment_transaction_count()
        destination_account.increment_transaction_count()
        self._apply_transaction_fee(source_account)
        self._apply_transaction_fee(destination_account)


    def _apply_paybill(self, transaction: Transaction) -> None:
        """Apply a bill payment when the company code is valid and funds are available."""
        account = self._get_existing_account(transaction.account_number, "paybill")
        if account is None or not self._ensure_active(account, "paybill"):
            return
        if transaction.misc not in self.VALID_BILL_COMPANIES:
            ErrorLogger.log(f"invalid bill company '{transaction.misc}'", "paybill")
            return
        if account.balance < transaction.amount:
            ErrorLogger.log(f"insufficient funds in account {account.account_number}", "paybill")
            return

        account.debit(transaction.amount)
        account.increment_transaction_count()
        self._apply_transaction_fee(account)

    def _apply_deposit(self, transaction: Transaction) -> None:
        """Apply a deposit when the account exists and is active."""
        account = self._get_existing_account(transaction.account_number, "deposit")
        if account is None or not self._ensure_active(account, "deposit"):
            return

        account.credit(transaction.amount)
        account.increment_transaction_count()
        self._apply_transaction_fee(account)

    def _apply_create(self, transaction: Transaction) -> None:
        """Create a new active account using the lowest unused five-digit account number."""
        new_account_number = self._next_account_number()
        if new_account_number is None:
            ErrorLogger.log("no unused account numbers remain", "create")
            return

        self.accounts_by_number[new_account_number] = Account(
            account_number=new_account_number,
            account_holder=transaction.account_holder,
            status="A",
            balance=transaction.amount,
            total_transactions=0,
            plan="NP",
        )

    def _apply_delete(self, transaction: Transaction) -> None:
        """Delete an existing account from the in-memory account collection."""
        if transaction.account_number not in self.accounts_by_number:
            ErrorLogger.log(f"account {transaction.account_number} not found", "delete")
            return
        del self.accounts_by_number[transaction.account_number]

    def _apply_disable(self, transaction: Transaction) -> None:
        """Disable an existing account so later active-only transactions are rejected."""
        account = self._get_existing_account(transaction.account_number, "disable")
        if account is None:
            return
        account.disable()

    def _apply_change_plan(self, transaction: Transaction) -> None:
        """Toggle the plan for an existing account between SP and NP."""
        account = self._get_existing_account(transaction.account_number, "changeplan")
        if account is None:
            return
        account.toggle_plan()

    def _get_existing_account(self, account_number: str, context: str) -> Account | None:
        """Return the matching account object, or log an error when the account does not exist."""
        account = self.accounts_by_number.get(account_number)
        if account is None:
            ErrorLogger.log(f"account {account_number} not found", context)
        return account

    def _ensure_active(self, account: Account, context: str) -> bool:
        """Return True only when the provided account is active."""
        if not account.is_active():
            ErrorLogger.log(f"account {account.account_number} is disabled", context)
            return False
        return True

    def _find_unique_destination_account(self, suffix: str) -> Account | None:
        """Return the unique account whose number ends with the provided two-digit suffix."""
        matches = [account for account in self.accounts_by_number.values() if account.account_number.endswith(suffix)]
        if not matches:
            ErrorLogger.log(f"destination account ending in '{suffix}' not found", "transfer")
            return None
        if len(matches) > 1:
            ErrorLogger.log(f"destination suffix '{suffix}' matches multiple accounts", "transfer")
            return None
        return matches[0]

    def _next_account_number(self) -> str | None:
        """Return the lowest unused five-digit account number, or None when all are used."""
        for number in range(1, 99999):
            candidate = f"{number:05d}"
            if candidate not in self.accounts_by_number:
                return candidate
        return None
    def _apply_transaction_fee(self, account):
        if account.plan == "SP":
         fee = 0.05
        else:
         fee = 0.10

        if account.balance >= fee:
         account.debit(fee)