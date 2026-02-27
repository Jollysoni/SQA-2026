"""
session.py

Session is a small helper class that remembers what "state" the front end is in.

It answers questions like:
- Are we logged in right now?
- Are we in standard mode or admin mode?
- Who is the current user (standard mode)?
- How much money has been withdrawn / transferred / paid in bills in this session?

In Phase 2 we keep the checks simple. More detailed rules can be added later.
"""


class Session:
    """Stores session state for the running front end program."""

    def __init__(self):
        """
        Create a new session object.

        Starts in a logged out state with zero totals.
        """
        self.logged_in = False
        self.mode = ""          # "standard" or "admin"
        self.current_user = ""  # account holder name in standard mode

        # Totals can be used for per session limits in later phases.
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0

    def start(self, mode, user):
        """
        Start a new session.

        Args:
            mode: "standard" or "admin"
            user: account holder name for standard mode, empty string for admin
        """
        self.logged_in = True
        self.mode = mode
        self.current_user = user

        # Reset totals for a fresh session.
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0

    def end(self):
        """
        End the current session.

        Clears mode and user and returns to logged out state.
        """
        self.logged_in = False
        self.mode = ""
        self.current_user = ""

        # We also reset totals so a future login starts clean.
        self.withdrawal_total = 0.0
        self.transfer_total = 0.0
        self.paybill_total = 0.0

    def is_admin(self):
        """
        Check if the session is in admin mode.

        Returns:
            True if mode is "admin", otherwise False.
        """
        return self.mode == "admin"

    def can_perform(self, transaction_type):
        """
        Decide if a transaction is allowed based on the current session state.

        rule set (simple):
        - If not logged in, only "login" is allowed.
        - Admin only transactions are blocked in standard mode.

        Args:
            transaction_type: a string like "withdrawal", "deposit", "create", etc.

        Returns:
            True if allowed, False if not allowed.
        """
        if not self.logged_in:
            return transaction_type == "login"

        privileged = ["create", "delete", "disable", "changeplan"]
        if transaction_type in privileged and not self.is_admin():
            return False

        return True

    def update_session_totals(self, transaction_type, amount):
        """
        Update running totals for the current session.

        This does not enforce limits yet. It just tracks totals so limit checks
        can be added later.

        Args:
            transaction_type: "withdrawal", "transfer", or "paybill"
            amount: numeric amount to add to the total
        """
        if transaction_type == "withdrawal":
            self.withdrawal_total += amount
        elif transaction_type == "transfer":
            self.transfer_total += amount
        elif transaction_type == "paybill":
            self.paybill_total += amount
