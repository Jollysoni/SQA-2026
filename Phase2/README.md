# CSCI 3060U – Phase 3: Front End Requirements Testing

**Group Members:**
- Mansi Kandoi – 100821953
- Sneh Patel – 100950609
- Jolly Soni – 100876863

---

## What This Phase Is About

In Phase 1 we wrote acceptance tests. In Phase 2 we built the ATM front end program. In Phase 3, we actually ran those tests against the program, found the bugs, fixed them, and made sure everything passes automatically.

The whole point is that a human shouldn't have to manually check anything — you run two scripts, and the computer tells you whether everything is working or not.

---

## How the Project Is Organized

```
Phase3/
├── bank-atm                  ← the program you actually run
├── scripts/
│   ├── run_all.sh            ← runs all 20 tests automatically
│   └── check_all.sh          ← compares outputs to expected results
├── src/
│   ├── frontend_app.py       ← main program logic
│   ├── account.py            ← account data class
│   ├── account_store.py      ← loads and searches accounts
│   ├── session.py            ← tracks login state
│   ├── transaction.py        ← stores one transaction in memory
│   └── transaction_writer.py ← writes the final ATF output file
└── tests/
    ├── currentaccounts.txt   ← the bank accounts file used during tests
    ├── inputs/               ← 20 test input files (one per test case)
    ├── expected/
    │   ├── atf/              ← what the ATF output file should look like
    │   └── console/          ← what the terminal output should look like
    └── outputs/
        ├── atf/              ← actual ATF outputs produced by the program
        └── console/          ← actual terminal outputs produced by the program
```

---

## How to Run the Program Manually

If you want to try it interactively (just to see it working), go into the `Phase3` folder and run:

```bash
./bank-atm tests/currentaccounts.txt myoutput.atf
```

Then type commands one at a time and press Enter:

```
login
standard
Sneh Patel
withdrawal
00101
100
logout
```

The program will respond after each command. When you log out, it writes the transaction file (`myoutput.atf`).

---

## How to Run All the Tests

Make sure you are inside the `Phase3` folder, then run:

```bash
bash scripts/run_all.sh
```

This runs all 20 test cases automatically. It feeds each input file into the program and saves both the ATF output and the terminal output into the `tests/outputs/` folder.

---

## How to Check If All Tests Passed

After running the tests, run:

```bash
bash scripts/check_all.sh
```

This compares every actual output against the expected output using `diff`. For each test it will print either `PASS` or `FAIL`. If everything is good, the last line will be:

```
All output checks passed.
```

If something fails, it will show you exactly which lines are different.

---

## What the Tests Cover

| # | Test | What It's Checking |
|---|------|--------------------|
| 01 | Login and logout | Basic session flow works |
| 02 | Transaction before login | You can't do anything without logging in |
| 03 | Second login in same session | You can't login twice |
| 04 | Withdrawal at $500 limit | Standard users can withdraw exactly $500 |
| 05 | Withdrawal above $500 | Standard users cannot exceed $500 |
| 06 | Withdrawal causing negative balance | Can't withdraw more than you have |
| 07 | Standard deposit recorded | Deposits get written to the ATF file |
| 08 | Deposit not available same session | Deposited money can't be spent right away |
| 09 | Transfer up to $1000 | Standard users can transfer up to $1000 |
| 10 | Transfer above $1000 | Standard users cannot exceed $1000 |
| 11 | Paybill within limit | Valid paybill with enough funds works |
| 12 | Paybill invalid company | Only EC, CQ, FI are accepted |
| 13 | Paybill above $2000 | Standard users cannot pay more than $2000 |
| 14 | Transaction on disabled account | Disabled accounts are blocked |
| 15 | Admin withdrawal from other user | Admin can act on any account |
| 16 | Standard user cannot create | Only admins can create accounts |
| 17 | Admin can create account | Create transaction is recorded correctly |
| 18 | Admin can disable account | Disable transaction is recorded correctly |
| 19 | Admin can delete account | Delete transaction is recorded correctly |
| 20 | Admin can change account plan | Changeplan transaction is recorded correctly |

---

## Bugs We Found and Fixed

During testing, 11 of the 20 tests initially failed. The full details are in the `Phase3.docx` failure table, but here's a quick summary of what was wrong:

- The $500 withdrawal limit, $1000 transfer limit, and $2000 paybill limit were not being enforced at all
- Withdrawals were not checking if the account had enough money
- Deposits were incorrectly making funds available immediately in the same session (they shouldn't be)
- Invalid bill company codes like "XX" were being accepted instead of rejected
- Transactions on disabled accounts were going through
- The ATF output records were 41 characters instead of the required 40
- Test 11's input was using an account with only $1,200 balance for a $2,000 paybill — the test itself was wrong, not the code
- The check script had a naming bug that caused console output filenames to get `.out` appended twice

All issues were fixed, and all 20 tests now pass.

---

## Requirements

- Python 3 (no extra packages needed)
- Unix/Linux/macOS terminal (or Git Bash on Windows)
