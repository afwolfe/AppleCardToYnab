# AppleCardToYnab

Uses [cardvisionpy](https://github.com/afwolfe/cardvisionpy) and [ynab-api](https://github.com/dmlerner/ynab-api) to parse Apple Card transaction screenshots and send them to YNAB as transactions.

## Requirements

* Pipenv
* Python 3.9+
* [Tesseract](https://github.com/tesseract-ocr/tesseract)

## Usage

1. Create the Pipenv
    * `pipenv install`
2. Copy template.env to .env and enter the variables.

    ```bash
    YNAB_API_KEY=
    YNAB_BUDGET_ID=
    YNAB_APPLE_CARD_ACCOUNT_ID=
    ```

3. Run the script, optionally including arguments specifying the `--inputPath` folder and `--outputPath` file for CardVision.
   * `pipenv run python main.py`
4. Review the resulting transactions and enter `y` or `n` to confirm or cancel uploading the transactions to YNAB.

