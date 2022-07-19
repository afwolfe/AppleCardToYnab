import dateparser
from datetime import date
import re

import cardvisionpy.logic.transactionutil as transactionutil
from cardvisionpy.models.transaction import Transaction

class TransactionReaderOcrText:
    """Can iterate over and return a processed list of Transactions."""

    rawTransactions: list[str] = []

    def __init__(self, transactions: list[str]):
        self.rawTransactions = transactions

    def getTransactions(self) -> list[Transaction]:
        """Iterates over all of the elements in the provided transactions and returns the final list."""
        finalTransactions: list[Transaction] = []
        while len(self.rawTransactions) > 0:
            finalTransactions.append(self.nextTransaction())
        return finalTransactions
    
    def nextTransaction(self) -> Transaction:
        """Processes and removes the next transaction from the list"""
        try:
            newTransaction = Transaction()
            nextField = self.rawTransactions.pop(0)

            # Sometimes payee names get broken into additional lines
            # Keep iterating until we find a valid transaction amount
            while newTransaction.amount is None: 
                if transactionutil.isAmount(nextField):
                    newTransaction.amount = transactionutil.amountInCents(nextField)
                else:
                    if newTransaction.payee is None: 
                        newTransaction.payee = nextField
                    else: 
                        newTransaction.payee += f" {nextField}"
                nextField = self.rawTransactions.pop(0)

            if newTransaction.payee is None: 
                newTransaction.payee = nextField
                nextField = self.rawTransactions.pop(0)

            timeDescription = None
            if newTransaction.payee == "Balance Adjustment":
                thirdBALine = self.rawTransactions.pop(0)
                if thirdBALine == "Dispute - Provisional Adjustment":
                    newTransaction.setMemo(thirdBALine)
                else:
                    timeDescription = thirdBALine
                    newTransaction.setMemo(newTransaction.payee)
            else:
                newTransaction.setMemo(nextField)

            nextField = self.rawTransactions.pop(0)

            dailyCash = nextField
            if newTransaction.__is_daily_cash__():
                while ("%" not in dailyCash):
                    dailyCash = self.rawTransactions.pop(0)
                newTransaction.dailyCash = dailyCash

            # // Sometimes "ago" winds up on the next line and separators from Family Sharing mess with the timestamp.
            # // Keep building the string until it contains a valid time stamp.
            if timeDescription is None:
                timeDescription = self.rawTransactions.pop(0)
            while not transactionutil.isTimestamp(timeDescription):
                timeDescription += " " + self.rawTransactions.pop(0)
            
            timeDescription = timeDescription.replace("-"," ").replace("•"," ")

            # Attempt to remove family member's name from description when using Family Sharing.
            # ex. "NAME - Yesterday"
            # If the description contains spaces and does not start with a number, it likely starts with the family member's name.
            if " " in timeDescription and re.match("^[0-9]", timeDescription) == None: 
                timeDescription = timeDescription.split(" ", 1)
                familyMember = timeDescription[0]
                newTransaction.setMemo(f"{familyMember} - {newTransaction.memo}")
                timeDescription = timeDescription[1].strip()
            
            parsedDate = dateparser.parse(timeDescription)
            if parsedDate is None:
                print("[WARN] Exception while parsing date, defaulting to today.")
                newTransaction.date = date.today()
            else:
                newTransaction.date = parsedDate.date()
            return newTransaction
        except IndexError:
            print("[ERR] Ran out of text elements while generating transaction")
            return None