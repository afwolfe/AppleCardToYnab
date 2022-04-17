import argparse
import csv
import os
import subprocess

from dateutil import parser
from pprint import pprint

import ynab_api
from dotenv import load_dotenv
from ynab_api.api import accounts_api, transactions_api
from ynab_api.model import save_transaction

load_dotenv() 

argparser = argparse.ArgumentParser(description='Convert Apple Card screenshots to YNAB transactions.')
argparser.add_argument("--imagePath", help="The path to the folder containing the screenshots for CardVision", required=False, default="screenshots/")
argparser.add_argument("--outputPath", help="The file to write the transaction data from CardVision", required=False, default="transactions.csv")
args = argparser.parse_args()

# TODO: Add args for env variables below
BUDGET_ID = os.environ.get("YNAB_BUDGET_ID")
API_KEY = os.environ.get("YNAB_API_KEY")
CARD_VISION_PATH = os.path.abspath("CardVision")

account_id = os.environ.get("YNAB_APPLE_CARD_ACCOUNT_ID")

# YNAB API configuration
configuration = ynab_api.Configuration(
    host="https://api.youneedabudget.com/v1")
configuration.api_key['bearer'] = API_KEY
configuration.api_key_prefix['bearer'] = 'Bearer'

# Builds and calls the cardvisioncli with the given parameters
def call_CardVisionCli(input_folder, output_file):
    if not os.path.exists(input_folder):
        raise FileNotFoundError("inputPath does not exist")
    if os.path.exists(output_file):
        raise FileExistsError("outputPath already exists")
    # Make the paths absolute since we'll be calling from the CardVision directory.
    if not os.path.isabs(input_folder):
        input_folder = os.path.abspath(input_folder)
    if not os.path.isabs(output_file):
        output_file = os.path.abspath(output_file)

    # Build CardVision if necessary
    build_command = ["swift", "build", "-c", "release"]
    try:
        subprocess.run(build_command, cwd=CARD_VISION_PATH, check=True)
    except subprocess.CalledProcessError:
        raise Exception("Error occurred while building the cardvision CLI")

    # Call CardVision
    cardvision_command = ["swift", "run", "CardVisionCLI",
        "-imagePath", input_folder,
        "-outputPath", output_file
    ]
    try:
        subprocess.run(cardvision_command, cwd=CARD_VISION_PATH, check=True)
        if not os.path.exists(output_file):
            raise FileNotFoundError("Output file was not detected")
    except subprocess.CalledProcessError:
        raise Exception("Error occurred while calling the cardvision CLI")

# If account_id is not already stored (from the environment or a previous API call, get it and return it.)
def get_apple_card_account_id():
    global account_id
    if account_id is None:
        with ynab_api.ApiClient(configuration) as api_client:
            api_instance = accounts_api.AccountsApi(api_client)
            api_response = api_instance.get_accounts(BUDGET_ID)

            for account in api_response["data"]["accounts"]:
                if "apple" in account["name"].lower():
                    print(account["name"])
                    account_id = account["id"]
                    return account_id
    else:
        return account_id

# Converts the dollar amount to a "milliunit" integer
def amount_to_milliunit(amount):
    return int(float(amount) * 100)

# Uses the given csv file to create a list of YNAB SaveTransactions
def parse_cardvision_csv(csv_file):
    transactions = []
    with open(csv_file, 'r') as file:
        transaction_rows = csv.DictReader(file)
        for row in transaction_rows:
            if row["Declined"] != "true": # don't import declined transactions
                transactions.append(save_transaction.SaveTransaction(
                    account_id=get_apple_card_account_id(),
                    date=parser.parse(row["Date"]).date(),
                    amount=amount_to_milliunit(row["Amount"]),
                    payee_name=row["Payee"],
                    memo=row["Memo"],
                    cleared="uncleared" if row["Pending"] == "true" else "cleared"
                ))
    return transactions


# Sends the POST request to create the transactions in YNAB
def send_transactions_to_ynab(transactions):
    with ynab_api.ApiClient(configuration) as api_client:
        api_instance = transactions_api.TransactionsApi(api_client)
        api_response = api_instance.create_transaction(BUDGET_ID, {"transactions": transactions})
        pprint(api_response)


if __name__ == "__main__":
    call_CardVisionCli(args.imagePath, args.outputPath)
    transactions = parse_cardvision_csv(args.outputPath)
    send_transactions_to_ynab(transactions)
