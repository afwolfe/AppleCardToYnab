# AppleCardToYnab

Uses [CardVision](https://github.com/BergQuester/CardVision) and [ynab-api](https://github.com/dmlerner/ynab-api) to parse Apple Card transaction screenshots and send them to YNAB as transactions.


## Requirements

* macOS (CardVision uses Apple's Vision API)
* Pipenv
* Python 3.9


## Usage

1. Create the Pipenv
    * `pipenv sync`
2. Initialize and update the submodule:
    * `git submodule update --init`
3. Copy template.env to .env and enter the variables.
    ```
    YNAB_API_KEY=
    YNAB_BUDGET_ID=
    YNAB_APPLE_CARD_ACCOUNT_ID=
    ```
4. Run the script, optionally including arguments specifying the `--inputPath` folder and `--outputPath` file for CardVision.
   * `pipenv run python main.py`

