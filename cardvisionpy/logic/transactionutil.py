"""
TransactionUtil.py
"""

import re

def isDailyCashTransaction(payee: str, memo: str) -> bool:
    """Determines if the payee and memo combination constitute a Daily Cash transaction."""
    nonDailyCashPayees = ["Payment", "Daily Cash Adjustment", "Balance Adjustment"]
    if payee in nonDailyCashPayees:
        return False

    return not ("refund" in memo.lower() or isDeclinedTransaction(memo))

def isAmount(amountCandidate: str) -> bool:
    """Determines if the given amount string is a valid monetary amount"""
    return re.search("^\+*\$[\d,]*\.\d\d$", amountCandidate) != None

def isDeclinedTransaction(candidate: str) -> bool:
    """Determines if the given transaction string is 'Declined'"""
    return "declined" in candidate.lower()

def isPendingTransaction(candidate: str) -> bool:
    """Determines if the given transaction string is 'Pending'"""
    return "pending" in candidate.lower()


def isTimestamp(candidate: str) -> bool:
    """Determines if the given string contains a valid timestamp"""
    return (re.search("[0-9]{1,2} (?:minute|hour)s{0,1} ago", candidate) != None or # relative timestamp
        re.search("\\d{1,2}\\/\\d{1,2}\\/\\d{2}", candidate) != None or # mm/dd/yy date stamp
        re.search("(?i)W*(?:Mon|Tues|Wednes|Thurs|Fri|Satur|Sun|Yester)day\\b[sS]*", candidate) != None) # day of week including Yesterday

def amountInCents(amount: str) -> int:
    """Converts a dollar amount to cents"""
    cents = amount.replace("+","").replace("$","").replace(".","").replace(",","")
    if cents.isnumeric():
        cents = int(cents)
        return cents if "+" in amount else -cents
    return None