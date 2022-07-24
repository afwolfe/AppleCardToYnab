import dateparser

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
    assert(actual.date == dateparser.parse('Yesterday').date())

def test_transaction_amount_first():
    raw_transaction = [
        '$100.00', 'Grocery Store', 'Card Number Used', '1%', '5 hours ago'
    ]
    
    trot = TransactionParser(raw_transaction)
    actual = trot.next_transaction()

    assert(actual.payee == "Grocery Store")
    assert(actual.amount == -10000)
    assert(actual.memo == "Card Number Used")
    assert(actual.dailyCash == "1%")
    assert(actual.is_daily_cash())
    assert(not actual.is_declined())
    assert(not actual.is_pending())
    assert(actual.date == dateparser.parse('5 hours ago').date())


def test_transaction_daily_cash_before_memo():
    raw_transaction = [
        'Movie Theater', '$25.00', '2%', 'Pending - Card Number Used', '5 minutes ago'
    ]
    
    trot = TransactionParser(raw_transaction)
    actual = trot.next_transaction()

    assert(actual.payee == "Movie Theater")
    assert(actual.amount == -2500)
    assert(actual.memo == "Pending - Card Number Used")
    assert(actual.dailyCash == "2%")
    assert(actual.is_daily_cash())
    assert(not actual.is_declined())
    assert(actual.is_pending())
    assert(actual.date == dateparser.parse('5 minutes ago').date())

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
    assert(actual.date ==  dateparser.parse('Yesterday').date())