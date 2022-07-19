from cardvisionpy.logic import transactionutil


def test_is_amount():
    amounts = [ "$0.00", "$99.00", "$1.00", "$100,000,000.00"]

    for amount in amounts:
        assert transactionutil.is_amount(amount)

def test_is_datestamp_day():
    week = ["Yesterday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in week:
        assert transactionutil.is_timestamp(day)

def test_is_datestamp_abs():
    dates = ["01/01/99", "12/31/00"]
    for date in dates:
        assert transactionutil.is_timestamp(date)
    
def test_is_datestamp_relative():
    relative_stamps = ["1 minute ago", "50 minutes ago", "1 hour ago", "10 hours ago"]
    for timestamp in relative_stamps:
        assert transactionutil.is_timestamp(timestamp)

def test_family_transaction_datestamp():
    timestamps = ['Partner — 16 minutes ago', 'Partner - 1 hour ago', 'Partner - Tuesday', 'Partner - 12/31/21']
    for timestamp in timestamps:
        assert transactionutil.is_timestamp(timestamp)
