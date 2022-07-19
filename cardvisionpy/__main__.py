"""
CardVisionPy

A reimplementation of bergquester/CardVision in Python
using OpenCV and Tesseract.

"""
from csv import DictWriter
import os
import cv2
import pytesseract

from models.transaction import Transaction
from logic.transactionocrreadertext import TransactionReaderOcrText

custom_config = r'--oem 3 --psm 12'
IMAGE_PATH = "images/"
#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

if __name__ == "__main__":
    # TODO: Handle folder vs single file correctly
    # if os.path.isfile(IMAGE_PATH):
    #     files = [ os.path.abspath(IMAGE_PATH) ]
    # else:
    files = os.listdir(IMAGE_PATH)

    transactions: list[Transaction] = []
    for file in files:

        img = cv2.imread(os.path.join(IMAGE_PATH, file))
        img = get_grayscale(img)

        text = pytesseract.image_to_string(img, config=custom_config)
        strs = [t.strip() for t in text.split("\n") if t]
        trot = TransactionReaderOcrText(strs)
        transactions += trot.getTransactions()
    
    # Sort by date
    transactions = sorted(transactions, key=lambda x: getattr(x, 'date'))

    with open("cardvision.csv", 'w') as csvfile:
        # Exclude internal variables and functions from headers
        headers = {k: Transaction.__dict__[k] for k in Transaction.__dict__.keys() if "__" not in k and not callable(Transaction.__dict__[k])}
        
        dw = DictWriter(csvfile, fieldnames=headers)
        dw.writeheader()
        for t in transactions:
            dw.writerow(t.__dict__)