"""
Object-oriented programming example demonstrating classes and inheritance.
"""

class BankAccount:
    """Represents a basic bank account with deposit and withdrawal operations."""

    def __init__(self, account_holder, initial_balance=0):
        self.account_holder = account_holder
        self.balance = initial_balance
        self.transaction_history = []

    def deposit(self, amount):
        """Deposit money into the account."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.transaction_history.append(f"Deposit: +${amount}")
        return self.balance

    def withdraw(self, amount):
        """Withdraw money from the account."""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.transaction_history.append(f"Withdrawal: -${amount}")
        return self.balance

    def get_balance(self):
        """Return current account balance."""
        return self.balance

    def get_transaction_history(self):
        """Return list of all transactions."""
        return self.transaction_history


class SavingsAccount(BankAccount):
    """Savings account with interest rate."""

    def __init__(self, account_holder, initial_balance=0, interest_rate=0.02):
        super().__init__(account_holder, initial_balance)
        self.interest_rate = interest_rate

    def apply_interest(self):
        """Apply interest to the current balance."""
        interest = self.balance * self.interest_rate
        self.balance += interest
        self.transaction_history.append(f"Interest: +${interest:.2f}")
        return self.balance
