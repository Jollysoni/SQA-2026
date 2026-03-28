from pathlib import Path
import sys

# Make Phase4/src importable when pytest is run from the Phase4 folder.
SRC_DIR = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC_DIR))

from account import Account
from transaction import Transaction
from process import TransactionProcessor


# ============================================================
# METHOD 1: _apply_deposit()
# Coverage type: STATEMENT COVERAGE
#
# Every executable statement in _apply_deposit() and the
# _apply_transaction_fee() helper it calls must be reached
# by at least one test.
#
# Statements identified:
#   S1  line 110 - _get_existing_account() called
#   S2  line 111 - if account is None or not active → guard check
#   S3  line 112 - return (guard fires: account missing OR disabled)
#   S4  line 114 - account.credit(transaction.amount)
#   S5  line 115 - account.increment_transaction_count()
#   S6  line 116 - _apply_transaction_fee(account) called
#   S7  line 188 - if account.plan == "SP" → fee = 0.05
#   S8  line 191 - else → fee = 0.10
#   S9  line 193 - if account.balance >= fee (evaluates True)
#   S10 line 194 - account.debit(fee) — fee is deducted
#   S11 line 193 - if account.balance >= fee (evaluates False, fee skipped)
#
# Test case table:
# +----+----------------------------------+---------+------+---------+------------------------------+
# | TC | Description                      | Status  | Plan | Balance | Expected                     |
# +----+----------------------------------+---------+------+---------+------------------------------+
# |  1 | Active SP account, normal deposit| Active  | SP   | 100.00  | 149.95, tx count = 1         |
# |  2 | Active NP account, normal deposit| Active  | NP   | 100.00  | 149.90, tx count = 1         |
# |  3 | Disabled account                 | Disabled| SP   | 100.00  | unchanged, tx count = 0      |
# |  4 | Account number not found         | N/A     | N/A  | 100.00  | unchanged, tx count = 0      |
# |  5 | Balance too low to cover fee     | Active  | SP   | 0.03    | 0.03, tx count = 1, fee skip |
# +----+----------------------------------+---------+------+---------+------------------------------+
# ============================================================


def test_apply_deposit_active_student_account_credits_amount_and_applies_sp_fee():
    """TC1 - Covers S1, S2(false), S4, S5, S6, S7, S9(true), S10.
    Deposit into an active SP account. The amount is credited and the
    student fee of 0.05 is deducted. Transaction count increments to 1."""
    account = Account('12345', 'Test User', 'A', 100.00, 0, 'SP')
    transaction = Transaction('04', 'Test User', '12345', 50.00, '')

    processor = TransactionProcessor([account])
    processor._apply_deposit(transaction)

    # 100.00 + 50.00 - 0.05 fee = 149.95
    assert round(account.balance, 2) == 149.95
    assert account.total_transactions == 1


def test_apply_deposit_active_non_student_account_applies_np_fee():
    """TC2 - Covers S8 (NP else branch in _apply_transaction_fee).
    Deposit into an active NP account. The non-student fee of 0.10 is
    deducted instead of the student fee. Transaction count increments to 1."""
    account = Account('12345', 'Test User', 'A', 100.00, 0, 'NP')
    transaction = Transaction('04', 'Test User', '12345', 50.00, '')

    processor = TransactionProcessor([account])
    processor._apply_deposit(transaction)

    # 100.00 + 50.00 - 0.10 fee = 149.90
    assert round(account.balance, 2) == 149.90
    assert account.total_transactions == 1


def test_apply_deposit_disabled_account_is_rejected():
    """TC3 - Covers S2(true) and S3 via the disabled branch.
    Deposit into a disabled account is silently rejected.
    Balance and transaction count must remain unchanged."""
    account = Account('12345', 'Test User', 'D', 100.00, 0, 'SP')
    transaction = Transaction('04', 'Test User', '12345', 50.00, '')

    processor = TransactionProcessor([account])
    processor._apply_deposit(transaction)

    assert account.balance == 100.00
    assert account.total_transactions == 0


def test_apply_deposit_unknown_account_number_does_nothing():
    """TC4 - Covers S2(true) and S3 via the account-not-found branch.
    The transaction references account 99999, which does not exist.
    The existing account 11111 must be completely unaffected."""
    account = Account('11111', 'Someone Else', 'A', 100.00, 0, 'SP')
    transaction = Transaction('04', 'Test User', '99999', 50.00, '')

    processor = TransactionProcessor([account])
    processor._apply_deposit(transaction)

    assert account.balance == 100.00
    assert account.total_transactions == 0


def test_apply_deposit_fee_is_skipped_when_balance_is_below_fee():
    """TC5 - Covers S9(false) / S11: the fee debit inside _apply_transaction_fee
    is not executed because the post-credit balance of 0.03 is less than the
    SP fee of 0.05. The credit and transaction count still apply normally."""
    account = Account('12345', 'Test User', 'A', 0.03, 0, 'SP')
    transaction = Transaction('04', 'Test User', '12345', 0.00, '')

    processor = TransactionProcessor([account])
    processor._apply_deposit(transaction)

    # 0.03 + 0.00 = 0.03; fee 0.05 > balance 0.03, so fee is skipped
    assert round(account.balance, 2) == 0.03
    assert account.total_transactions == 1


# ============================================================
# METHOD 2: process_transactions()
# Coverage type: DECISION AND LOOP COVERAGE
#
# The assignment requires a method with AT LEAST two decisions
# and one loop. process_transactions() contains:
#
#   LOOP L1  (line 28) - for transaction in transactions
#     Must test: zero iterations, one iteration, two+ iterations
#
#   DECISION D1  (line 38) - code == "01"  true → withdrawal
#   DECISION D2  (line 40) - code == "02"  true → transfer
#   DECISION D3  (line 42) - code == "03"  true → paybill
#   DECISION D4  (line 44) - code == "04"  true → deposit
#   DECISION D5  (line 46) - code == "05"  true → create
#   DECISION D6  (line 48) - code == "06"  true → delete
#   DECISION D7  (line 50) - code == "07"  true → disable
#   DECISION D8  (line 52) - code == "08"  true → change plan
#   DECISION D9  (line 54) - else           true → unknown code
#
# For decision coverage every branch (true AND false) must be
# taken. The if/elif chain means:
#   - D1 true  is covered by any "01" test
#   - D1 false is covered by any test where code != "01"
#   - Each subsequent elif is only reached when all earlier
#     conditions are false, so covering the true side of each
#     Dn automatically covers the false side of D1..D(n-1)
#
# Test case table:
# +----+--------------------------------------+------+-----+-------+------------------------------+
# | TC | Description                          | Loop | D#  | Code  | Expected                     |
# +----+--------------------------------------+------+-----+-------+------------------------------+
# |  6 | Empty list - loop body never entered | L1=0 |  -  |  -    | accounts unchanged, sorted   |
# |  7 | Single deposit - loop runs once      | L1=1 | D4  | 04    | balance up, tx count = 1     |
# |  8 | Deposit then withdraw - 2 iterations | L1=2 |D4,D1| 04,01 | correct net balance          |
# |  9 | Withdrawal dispatched (code 01)      | L1=1 | D1  | 01    | balance down, tx count = 1   |
# | 10 | Transfer dispatched (code 02)        | L1=1 | D2  | 02    | src down, dst up, counts = 1 |
# | 11 | Paybill dispatched (code 03)         | L1=1 | D3  | 03    | balance down, tx count = 1   |
# | 12 | Create dispatched (code 05)          | L1=1 | D5  | 05    | account count up, new exists |
# | 13 | Delete dispatched (code 06)          | L1=1 | D6  | 06    | account count down, gone     |
# | 14 | Disable dispatched (code 07)         | L1=1 | D7  | 07    | status = D, balance same     |
# | 15 | Change plan dispatched (code 08)     | L1=1 | D8  | 08    | plan = NP, balance same      |
# | 16 | Unknown code hits else branch        | L1=1 | D9  | 99    | balance and count unchanged  |
# +----+--------------------------------------+------+-----+-------+------------------------------+
# ============================================================


def test_process_transactions_empty_list_does_not_enter_loop():
    """TC6 - L1=0: loop body never executes.
    With an empty transaction list the accounts are returned sorted by account
    number and completely unmodified."""
    first = Account('54321', 'First', 'A', 100.00, 0, 'SP')
    second = Account('12345', 'Second', 'A', 200.00, 0, 'SP')

    processor = TransactionProcessor([first, second])
    result = processor.process_transactions([])

    # Sorted order: 12345 before 54321
    assert [a.account_number for a in result] == ['12345', '54321']
    # No balances or counts changed
    assert first.balance == 100.00
    assert first.total_transactions == 0
    assert second.balance == 200.00
    assert second.total_transactions == 0


def test_process_transactions_single_deposit_loop_runs_once():
    """TC7 - L1=1: loop executes exactly one iteration. D4 true branch taken.
    A single deposit is applied. Balance rises and transaction count becomes 1."""
    account = Account('12345', 'User', 'A', 100.00, 0, 'SP')
    transactions = [Transaction('04', 'User', '12345', 50.00, '')]

    processor = TransactionProcessor([account])
    result = processor.process_transactions(transactions)

    # 100.00 + 50.00 - 0.05 fee = 149.95
    assert len(result) == 1
    assert round(result[0].balance, 2) == 149.95
    assert result[0].total_transactions == 1


def test_process_transactions_deposit_then_withdrawal_loop_runs_twice():
    """TC8 - L1=2+: loop executes two iterations in sequence.
    D4 true branch taken first (deposit), then D1 true branch (withdrawal).
    Confirms the loop body runs multiple times and applies transactions in order."""
    account = Account('12345', 'User', 'A', 100.00, 0, 'SP')
    transactions = [
        Transaction('04', 'User', '12345', 50.00, ''),  # deposit
        Transaction('01', 'User', '12345', 20.00, ''),  # withdrawal
    ]

    processor = TransactionProcessor([account])
    result = processor.process_transactions(transactions)

    # After deposit: 100 + 50 - 0.05 = 149.95
    # After withdrawal: 149.95 - 20 - 0.05 = 129.90
    assert round(result[0].balance, 2) == 129.90
    assert result[0].total_transactions == 2


def test_process_transactions_withdrawal_takes_d1_true_branch():
    """TC9 - D1 true: code "01" routes to _apply_withdrawal.
    Sufficient funds so the withdrawal succeeds. Balance decreases by the
    amount plus the service fee and the transaction count increments."""
    account = Account('12345', 'User', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('01', 'User', '12345', 50.00, '')]

    processor = TransactionProcessor([account])
    result = processor.process_transactions(transactions)

    # 200.00 - 50.00 - 0.05 fee = 149.95
    assert round(result[0].balance, 2) == 149.95
    assert result[0].total_transactions == 1


def test_process_transactions_transfer_takes_d2_true_branch():
    """TC10 - D1 false, D2 true: code "02" routes to _apply_transfer.
    Source account is debited and destination account is credited. Both
    transaction counts increment and both accounts have fees applied."""
    source = Account('12345', 'User A', 'A', 500.00, 0, 'SP')
    destination = Account('67890', 'User B', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('02', 'User A', '12345', 100.00, '90')]

    processor = TransactionProcessor([source, destination])
    result = processor.process_transactions(transactions)

    src_out = next(a for a in result if a.account_number == '12345')
    dst_out = next(a for a in result if a.account_number == '67890')
    # Source: 500 - 100 - 0.05 fee = 399.95
    assert round(src_out.balance, 2) == 399.95
    assert src_out.total_transactions == 1
    # Destination: 200 + 100 - 0.05 fee = 299.95
    assert round(dst_out.balance, 2) == 299.95
    assert dst_out.total_transactions == 1


def test_process_transactions_paybill_takes_d3_true_branch():
    """TC11 - D1 false, D2 false, D3 true: code "03" routes to _apply_paybill.
    Valid company code EC with sufficient funds. Balance decreases by the
    payment amount plus service fee and transaction count increments."""
    account = Account('12345', 'User', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('03', 'User', '12345', 50.00, 'EC')]

    processor = TransactionProcessor([account])
    result = processor.process_transactions(transactions)

    # 200.00 - 50.00 - 0.05 fee = 149.95
    assert round(result[0].balance, 2) == 149.95
    assert result[0].total_transactions == 1


def test_process_transactions_create_takes_d5_true_branch():
    """TC12 - D1-D4 false, D5 true: code "05" routes to _apply_create.
    A new account is created. The overall account count increases by one,
    and the created account should be active with plan NP and zero completed
    transactions."""
    existing = Account('12345', 'Existing User', 'A', 500.00, 0, 'NP')
    transactions = [Transaction('05', 'New User', '00000', 0.00, '')]

    processor = TransactionProcessor([existing])
    result = processor.process_transactions(transactions)

    # One extra account should now exist
    assert len(result) == 2

    # Find the newly created account without hard-coding a specific number.
    new_accounts = [
        account for account in result
        if account.account_holder == 'New User' and account.account_number != '12345'
    ]
    assert len(new_accounts) == 1

    new_acc = new_accounts[0]
    assert len(new_acc.account_number) == 5
    assert new_acc.account_number.isdigit()
    assert new_acc.status == 'A'
    assert new_acc.plan == 'NP'
    assert new_acc.balance == 0.00
    assert new_acc.total_transactions == 0


def test_process_transactions_delete_takes_d6_true_branch():
    """TC13 - D1-D5 false, D6 true: code "06" routes to _apply_delete.
    The targeted account is removed from the collection. Account count
    decreases by one and the deleted account number is no longer present."""
    account = Account('12345', 'User', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('06', 'User', '12345', 0.00, '')]

    processor = TransactionProcessor([account])
    result = processor.process_transactions(transactions)

    assert len(result) == 0
    assert '12345' not in processor.accounts_by_number


def test_process_transactions_disable_takes_d7_true_branch():
    """TC14 - D1-D6 false, D7 true: code "07" routes to _apply_disable.
    Account status changes from A to D. Balance and transaction count
    are not affected by a disable operation."""
    account = Account('12345', 'User', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('07', 'User', '12345', 0.00, '')]

    processor = TransactionProcessor([account])
    processor.process_transactions(transactions)

    assert account.status == 'D'
    assert account.balance == 200.00
    assert account.total_transactions == 0


def test_process_transactions_change_plan_takes_d8_true_branch():
    """TC15 - D1-D7 false, D8 true: code "08" routes to _apply_change_plan.
    Account plan toggles from SP to NP. Balance and transaction count
    are not affected by a plan change."""
    account = Account('12345', 'User', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('08', 'User', '12345', 0.00, '')]

    processor = TransactionProcessor([account])
    processor.process_transactions(transactions)

    assert account.plan == 'NP'
    assert account.balance == 200.00
    assert account.total_transactions == 0


def test_process_transactions_unknown_code_takes_else_branch():
    """TC16 - D1-D8 all false, else branch taken: unrecognised code is logged.
    No state changes occur. Balance, transaction count, status, and plan
    must all remain exactly as they were before the transaction was processed."""
    account = Account('12345', 'User', 'A', 200.00, 0, 'SP')
    transactions = [Transaction('99', 'User', '12345', 0.00, '')]

    processor = TransactionProcessor([account])
    result = processor.process_transactions(transactions)

    assert result[0].balance == 200.00
    assert result[0].total_transactions == 0
    assert result[0].status == 'A'
    assert result[0].plan == 'SP'
