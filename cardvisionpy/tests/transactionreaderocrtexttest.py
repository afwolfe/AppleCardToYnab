from datetime import date, timedelta
from cardvisionpy.logic.transactionocrreadertext import TransactionReaderOcrText

def test_next_transaction():
    rawTransaction = [
        'Amazon', '$50.00', 'Card Number Used', '1%', 'Yesterday'
    ]
    
    trot = TransactionReaderOcrText(rawTransaction)
    actual_transaction = trot.nextTransaction()
    print(actual_transaction)
    assert(actual_transaction.payee == "Amazon")
    assert(actual_transaction.amount == -5000)
    assert(actual_transaction.memo == "Card Number Used")
    assert(actual_transaction.dailyCash == "1%")
    assert(actual_transaction.date == date.today() - timedelta(days=1))