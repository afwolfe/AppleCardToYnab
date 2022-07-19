import dateparser
from datetime import date
import re

import cardvisionpy.logic.transactionutil as transactionutil
from cardvisionpy.models.transaction import Transaction

class TransactionParser:
    """Can iterate over and return a processed list of Transactions."""

    raw_transactions: list[str] = []

    def __init__(self, transactions: list[str]):
        self.raw_transactions = transactions

    def get_transactions(self) -> list[Transaction]:
        """Iterates over all of the elements in the provided transactions and returns the final list."""
        transactions: list[Transaction] = []
        while len(self.raw_transactions) > 0:
            transactions.append(self.next_transaction())
        return transactions
    
    def next_transaction(self) -> Transaction:
        """Processes and removes the next transaction from the list"""
        try:
            new_transaction = Transaction()
            next_field = self.raw_transactions.pop(0)

            # Sometimes payee names get broken into additional lines
            # Keep iterating until we find a valid transaction amount
            while new_transaction.amount is None: 
                if transactionutil.is_amount(next_field):
                    new_transaction.amount = transactionutil.amount_in_cents(next_field)
                else:
                    if new_transaction.payee is None: 
                        new_transaction.payee = next_field
                    else: 
                        new_transaction.payee += f" {next_field}"
                next_field = self.raw_transactions.pop(0)

            if new_transaction.payee is None: 
                new_transaction.payee = next_field
                next_field = self.raw_transactions.pop(0)

            time_description = None
            if new_transaction.payee == "Balance Adjustment":
                third_ba_line = self.raw_transactions.pop(0)
                if third_ba_line == "Dispute - Provisional Adjustment":
                    new_transaction.set_memo(third_ba_line)
                else:
                    time_description = third_ba_line
                    new_transaction.set_memo(new_transaction.payee)
            else:
                new_transaction.set_memo(next_field)

            next_field = self.raw_transactions.pop(0)

            daily_cash = next_field
            if new_transaction.is_daily_cash():
                while ("%" not in daily_cash):
                    daily_cash = self.raw_transactions.pop(0)
                new_transaction.dailyCash = daily_cash

            # // Sometimes "ago" winds up on the next line and separators from Family Sharing mess with the timestamp.
            # // Keep building the string until it contains a valid time stamp.
            if time_description is None:
                time_description = self.raw_transactions.pop(0)
            while not transactionutil.is_timestamp(time_description):
                time_description += " " + self.raw_transactions.pop(0)
            
            time_description = time_description.replace("-"," ").replace("•"," ")

            # Attempt to remove family member's name from description when using Family Sharing.
            # ex. "NAME - Yesterday"
            # If the description contains spaces and does not start with a number, it likely starts with the family member's name.
            if " " in time_description and re.match("^[0-9]", time_description) == None: 
                time_description = time_description.split(" ", 1)
                familyMember = time_description[0]
                new_transaction.set_memo(f"{familyMember} - {new_transaction.memo}")
                time_description = time_description[1].strip()
            
            parsed_date = dateparser.parse(time_description)
            if parsed_date is None:
                print("[WARN] Exception while parsing date, defaulting to today.")
                new_transaction.date = date.today()
            else:
                new_transaction.date = parsed_date.date()
            return new_transaction
        except IndexError:
            print("[ERR] Ran out of text elements while generating transaction")
            return None