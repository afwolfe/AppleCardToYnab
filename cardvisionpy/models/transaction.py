from datetime import date

class Transaction:
    """
    Holds a Transaction representing an Apple Card transaction.
    """
    
    # The date of the transaction
    date: date = None
    # The payee (or payer)
    payee: str = None

    # The amount, in cents
    amount: int = None

    # The daily cash %
    dailyCash: str = None

    # The memo for the transaction
    memo: str = None

    # If the transaction is pending
    pending: bool = None

    # If the transaction was marked as declined
    declined: bool = None

    def set_memo(self, memo: str):
        self.memo = memo
        self.declined = self.is_declined()
        self.pending = self.is_pending()

    def is_daily_cash(self):
        non_dc_payees = ["Payment", "Daily Cash Adjustment", "Balance Adjustment"]
        if self.payee in non_dc_payees:
            return False

        return not ("refund" in self.memo.lower() or self.is_declined())


    def is_declined(self) -> bool:
        """Determines if the given transaction string is 'Declined'"""
        return "declined" in self.memo.lower()

    def is_pending(self) -> bool:
        """Determines if the given transaction string is 'Pending'"""
        return "pending" in self.memo.lower()
        
    def __str__(self) -> str:
        return f"""Payee: {self.payee}
Amount: {self.amount}
Memo: {self.memo}
Pending: {self.pending}
Declined: {self.declined}
Date: {self.date}
Daily Cash: {self.dailyCash}
"""