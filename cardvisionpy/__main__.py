"""
CardVisionPy

A reimplementation of bergquester/CardVision in Python
using OpenCV and Tesseract.

"""
import argparse
import os

from csv import DictWriter

import cv2
import pytesseract

from cardvisionpy.models.transaction import Transaction
from cardvisionpy.logic.transactionparser import TransactionParser

TESSERACT_CONFIG = r'--oem 3 --psm 12'

argparser = argparse.ArgumentParser()
argparser.add_argument("--input-path", default="images/")
argparser.add_argument("--output-file", default="transactions.csv")
argparser.add_argument("--verbose", action="store_true")

args = argparser.parse_args()
input_path = os.path.abspath(args.input_path)
output_file = os.path.abspath(args.output_file)
verbose = args.verbose

def get_grayscale(image: cv2.Mat):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def get_processed_transactions(input_path: os.PathLike):
    transactions: list[Transaction] = []
    files = os.listdir(input_path)
    for file in files:

        img = cv2.imread(os.path.join(input_path, file))
        img = get_grayscale(img)

        text = pytesseract.image_to_string(img, config=TESSERACT_CONFIG)
        strs = [t.strip() for t in text.split("\n") if t]
        trot = TransactionParser(strs)
        transactions += trot.get_transactions()
    
    # Sort by date
    return sorted(transactions, key=lambda x: getattr(x, 'date'))

def write_to_csv(transactions: list[Transaction], output_file: os.PathLike):
    # Exclude internal variables and functions from headers
    headers = {k: Transaction.__dict__[k] for k in Transaction.__dict__.keys() if "__" not in k and not callable(Transaction.__dict__[k])}
        
    with open(output_file, 'w') as csvfile:
        dw = DictWriter(csvfile, fieldnames=headers)
        dw.writeheader()
        dw.writerows([t.__dict__ for t in transactions])

if __name__ == "__main__":
    transactions = get_processed_transactions(input_path)
    write_to_csv(transactions, output_file)