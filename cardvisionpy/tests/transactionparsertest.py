from datetime import date, timedelta
from cardvisionpy.logic.transactionparser import TransactionParser

def test_next_transaction():
    raw_transaction = [
        'Amazon', '$50.00', 'Card Number Used', '1%', 'Yesterday'
    ]
    
    trot = TransactionParser(raw_transaction)
    actual = trot.next_transaction()

    assert(actual.payee == "Amazon")
    assert(actual.amount == -5000)
    assert(actual.memo == "Card Number Used")
    assert(actual.dailyCash == "1%")
    assert(actual.is_daily_cash())
    assert(not actual.is_declined())
    assert(not actual.is_pending())
    assert(actual.date == date.today() - timedelta(days=1))

def test_daily_cash_adjustment():
    raw_transaction = ['Daily Cash Adjustment', '$0.25', 'From Refund', 'Yesterday']

    trot = TransactionParser(raw_transaction)
    actual = trot.next_transaction()

    assert(actual.payee == "Daily Cash Adjustment")
    assert(actual.amount == -25)
    assert(actual.memo == "From Refund")
    assert(not actual.is_daily_cash())
    assert(not actual.is_declined())
    assert(not actual.is_pending())
    assert(actual.date == date.today() - timedelta(days=1))