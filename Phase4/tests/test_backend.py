import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.account import Account
from src.transaction import Transaction
from src.process import TransactionProcessor


# METHOD 1: _apply_deposit()
# (Statement Coverage)

def test_deposit_valid_student():
    acc = Account("12345", "Test User", "A", 100.00, 0, "SP")
    txn = Transaction("04", "Test User", "12345", 50.00, "")

    processor = TransactionProcessor([acc])
    processor._apply_deposit(txn)

    # 100 + 50 - 0.05 fee
    assert round(acc.balance, 2) == 149.95


def test_deposit_valid_non_student():
    acc = Account("12345", "Test User", "A", 100.00, 0, "NP")
    txn = Transaction("04", "Test User", "12345", 50.00, "")

    processor = TransactionProcessor([acc])
    processor._apply_deposit(txn)

    # 100 + 50 - 0.10 fee
    assert round(acc.balance, 2) == 149.90


def test_deposit_disabled_account():
    acc = Account("12345", "Test User", "D", 100.00, 0, "SP")
    txn = Transaction("04", "Test User", "12345", 50.00, "")

    processor = TransactionProcessor([acc])
    processor._apply_deposit(txn)

    # No change
    assert acc.balance == 100.00


def test_deposit_account_not_found():
    acc = Account("11111", "User", "A", 100.00, 0, "SP")
    txn = Transaction("04", "User", "99999", 50.00, "")

    processor = TransactionProcessor([acc])
    processor._apply_deposit(txn)

    assert acc.balance == 100.00


# -----------------------------
# METHOD 2: process_transactions()
# (Decision + Loop Coverage)
# -----------------------------

def test_multiple_transactions():
    acc = Account("12345", "User", "A", 100.00, 0, "SP")

    txns = [
        Transaction("04", "User", "12345", 50.00, ""),  # deposit
        Transaction("01", "User", "12345", 20.00, "")   # withdrawal
    ]

    processor = TransactionProcessor([acc])
    updated = processor.process_transactions(txns)

    # deposit: 100 + 50 - 0.05 = 149.95
    # withdraw: 149.95 - 20 - 0.05 = 129.90
    assert round(updated[0].balance, 2) == 129.90


def test_empty_transactions():
    acc = Account("12345", "User", "A", 100.00, 0, "SP")

    processor = TransactionProcessor([acc])
    updated = processor.process_transactions([])

    assert updated[0].balance == 100.00


def test_invalid_account_transaction():
    acc = Account("12345", "User", "A", 100.00, 0, "SP")

    txns = [
        Transaction("01", "User", "99999", 50.00, "")
    ]

    processor = TransactionProcessor([acc])
    updated = processor.process_transactions(txns)

    assert updated[0].balance == 100.00