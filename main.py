import argparse
import logging
import os
import sys
from typing import List

from dotenv import load_dotenv
from tabulate import tabulate

import ynab_api
from ynab_api.api import accounts_api, transactions_api
from ynab_api.model import save_transaction

from cardvisionpy import cardvisionpy
from cardvisionpy.models.transaction import Transaction

load_dotenv()

argparser = argparse.ArgumentParser(
    description="Convert Apple Card screenshots \
  to YNAB transactions."
)
argparser.add_argument(
    "-d", action="store_true", help="Enables debug printing."
)
cardvision = argparser.add_argument_group("cardvision")
cardvision.add_argument(
    "--imagePath",
    default="screenshots/",
    help="The path to the folder containing the screenshots for CardVision. \
    Defaults to 'screenshots'",
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

debug: bool = args.d

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)                             

if debug:
    logger.setLevel("DEBUG")
    handler.setLevel("DEBUG") 
else:
    logger.setLevel("INFO")
    handler.setLevel("INFO") 
log_format = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

image_path: os.PathLike = os.path.abspath(args.imagePath)

if not os.path.exists(image_path):
    raise FileNotFoundError(f"imagePath: {image_path} does not exist")

budget_id: str = args.budgetId
api_key: str = args.apiKey
account_id: str = args.accountId

# YNAB API configuration
configuration = ynab_api.Configuration(host="https://api.youneedabudget.com/v1")
configuration.api_key["bearer"] = api_key
configuration.api_key_prefix["bearer"] = "Bearer"

summary_keys = ["date", "payee_name", "amount", "memo"]

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
                    logger.info(f"Found Apple Account in YNAB: {account['name']}")
                    account_id = account["id"]
                    logger.debug(f"YNAB Apple Account ID: {account['id']}")

                    return account_id
    else:
        return account_id


def cents_to_milliunit(amount: int) -> int:
    """Converts the cents amount to a "milliunit" integer"""
    # TODO: Make cardvision py return the normal dollar float?
    return int(float(amount) * 10)


def cardvision_to_ynab_transactions(cv_transactions: list[Transaction]) -> List[save_transaction.SaveTransaction]:
    transactions = []
    summaries = []
    for cv_transaction in cv_transactions:
        if not cv_transaction.is_declined():  # don't import declined transactions
            ynab_transaction = save_transaction.SaveTransaction(
                account_id=get_apple_card_account_id(),
                date=cv_transaction.date,
                amount=cents_to_milliunit(cv_transaction.amount),
                payee_name=cv_transaction.payee[:50],
                memo=cv_transaction.memo[:200],
                cleared="uncleared" if cv_transaction.is_pending() else "cleared",
            )
            summary = [ynab_transaction[f] for f in summary_keys]
            summaries.append(summary)
            transactions.append(ynab_transaction)
    print(tabulate(summaries, headers=summary_keys))
    return transactions

def send_transactions_to_ynab(transactions: List[save_transaction.SaveTransaction]):
    """Sends the POST request to create the transactions in YNAB"""
    with ynab_api.ApiClient(configuration) as api_client:
        api_instance = transactions_api.TransactionsApi(api_client)
        api_response = api_instance.create_transaction(
            budget_id, {"transactions": transactions}
        )
        logger.debug(api_response)


if __name__ == "__main__":
    cv_transactions = cardvisionpy.get_processed_transactions(image_path)
    transactions = cardvision_to_ynab_transactions(cv_transactions)
    confirm = ""
    while confirm.lower() not in ["y", "n"]:
        confirm = input("Send transactions to YNAB? (y/n) ")
    if confirm.lower() == "y":
        send_transactions_to_ynab(transactions)
    else:
        logger.info("Not sending transactions.")
