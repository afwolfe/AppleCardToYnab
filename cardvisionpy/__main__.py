"""
CardVisionPy

A reimplementation of bergquester/CardVision in Python
using OpenCV and Tesseract.

"""
import argparse
import os

from cardvisionpy import cardvisionpy

argparser = argparse.ArgumentParser()
argparser.add_argument("--input-path", default="images/")
argparser.add_argument("--output-file", default="transactions.csv")
argparser.add_argument("--verbose", action="store_true")

args = argparser.parse_args()
input_path = os.path.abspath(args.input_path)
output_file = os.path.abspath(args.output_file)
verbose = args.verbose

if __name__ == "__main__":
    transactions = cardvisionpy.get_processed_transactions(input_path)
    cardvisionpy.write_to_csv(transactions, output_file)
