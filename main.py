import argparse
import csv
import os
import subprocess
from typing import List

from dateutil import parser
from dotenv import load_dotenv
from pprint import pprint
from tabulate import tabulate

import ynab_api
from ynab_api.api import accounts_api, transactions_api
from ynab_api.model import save_transaction

from cardvisionpy import cardvisionpy

load_dotenv()

argparser = argparse.ArgumentParser(
    description="Convert Apple Card screenshots \
  to YNAB transactions."
)
argparser.add_argument(
    "-f", action="store_true", help="Force overwriting of outputPath."
)
cardvision = argparser.add_argument_group("cardvision")
cardvision.add_argument(
    "--imagePath",
    default="screenshots/",
    help="The path to the folder containing the screenshots for CardVision. \
    Defaults to 'screenshots'",
    required=False,
)
cardvision.add_argument(
    "--outputPath",
    default="transactions.csv",
    help="The file to write the transaction data from CardVision. \
    Defaults to 'transactions.csv'",
    required=False,
)
ynab = argparser.add_argument_group("ynab")
ynab.add_argument(
    "--budgetId",
    default=os.environ.get("YNAB_BUDGET_ID"),
    help="The YNAB budget ID to write to, defaults to YNAB_BUDGET_ID in env.",
    required=False,
)
ynab.add_argument(
    "--apiKey",
    default=os.environ.get("YNAB_API_KEY"),
    help="The YNAB API key to use to, defaults to YNAB_API_KEY in env.",
    required=False,
)
ynab.add_argument(
    "--accountId",
    default=os.environ.get("YNAB_APPLE_CARD_ACCOUNT_ID"),
    help="The YNAB account ID of the Apple Card, defaults to YNAB_APPLE_CARD_ACCOUNT_ID in env. \
    Will attempt to read find account with 'Apple' in budget if not specified.",
    required=False,
)

args = argparser.parse_args()

force: bool = args.f

image_path: os.PathLike = os.path.abspath(args.imagePath)
output_path: os.PathLike = os.path.abspath(args.outputPath)

if not os.path.exists(image_path):
    raise FileNotFoundError(f"imagePath: {image_path} does not exist")
if os.path.exists(output_path) and not force:
    raise FileExistsError(f"outputPath: {output_path} already exists.")

budget_id: str = args.budgetId
api_key: str = args.apiKey
account_id: str = args.accountId

# YNAB API configuration
configuration = ynab_api.Configuration(host="https://api.youneedabudget.com/v1")
configuration.api_key["bearer"] = api_key
configuration.api_key_prefix["bearer"] = "Bearer"

summary_keys = ["date", "payee_name", "amount", "memo"]


def call_cardvision(input_folder: os.PathLike, output_file: os.PathLike) -> None:
    """Uses the cardvisionpy with the specified input and output paths."""
    try:
        # TODO: Parse Transactions directly instead of serializing to CSV first.
        transactions = cardvisionpy.get_processed_transactions(input_folder)
        cardvisionpy.write_to_csv(transactions, output_file)
        if not os.path.exists(output_file):
            raise FileNotFoundError("Output file was not detected")
    except Exception:
        raise Exception("Error occurred while processing screenshots")


def get_apple_card_account_id() -> str:
    """If account_id is not already stored,
    either from the environment or a previous API call, get it and return it."""
    global account_id
    if account_id is None:
        with ynab_api.ApiClient(configuration) as api_client:
            api_instance = accounts_api.AccountsApi(api_client)
            api_response = api_instance.get_accounts(budget_id)

            for account in api_response["data"]["accounts"]:
                if "apple" in account["name"].lower():
                    print(account["name"])
                    account_id = account["id"]
                    return account_id
    else:
        return account_id


def cents_to_milliunit(amount: int) -> int:
    """Converts the cents amount to a "milliunit" integer"""
    # TODO: Make cardvision py return the normal dollar float?
    return int(float(amount) * 10)


def parse_cardvision_csv(
    csv_file: os.PathLike,
) -> List[save_transaction.SaveTransaction]:
    """Uses the given csv file to create a list of YNAB SaveTransactions"""
    transactions = []
    summaries = []
    with open(csv_file, "r") as file:
        transaction_rows = csv.DictReader(file)
        for row in transaction_rows:
            if row["declined"] != "true":  # don't import declined transactions
                transaction = save_transaction.SaveTransaction(
                    account_id=get_apple_card_account_id(),
                    date=parser.parse(row["date"]).date(),
                    amount=cents_to_milliunit(row["amount"]),
                    payee_name=row["payee"][:50],
                    memo=row["memo"][:200],
                    cleared="uncleared" if row["pending"] == "True" else "cleared",
                )
                summary = [transaction[f] for f in summary_keys]
                summaries.append(summary)
                transactions.append(transaction)
    print(tabulate(summaries, headers=summary_keys))
    return transactions


def send_transactions_to_ynab(transactions: List[save_transaction.SaveTransaction]):
    """Sends the POST request to create the transactions in YNAB"""
    with ynab_api.ApiClient(configuration) as api_client:
        api_instance = transactions_api.TransactionsApi(api_client)
        api_response = api_instance.create_transaction(
            budget_id, {"transactions": transactions}
        )
        pprint(api_response)


if __name__ == "__main__":
    call_cardvision(image_path, output_path)
    transactions = parse_cardvision_csv(output_path)
    confirm = ""
    while confirm.lower() not in ["y", "n"]:
        confirm = input("Send transactions to YNAB? (y/n) ")
    if confirm.lower() == "y":
        send_transactions_to_ynab(transactions)
    else:
        print("Not sending transactions.")
