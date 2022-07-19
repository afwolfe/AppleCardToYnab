# AppleCardToYnab

Uses a Python reimplementation of [CardVision](https://github.com/BergQuester/CardVision) (`cardvisionpy/`) and [ynab-api](https://github.com/dmlerner/ynab-api) to parse Apple Card transaction screenshots and send them to YNAB as transactions.

## Requirements

* Pipenv
* Python 3.9
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

## Acknowledgements

* The cardvisionpy module would not be possible without the work originally done by [BergQuester's CardVision](https://github.com/BergQuester/CardVision) project to handle a lot of the "weirdness" of parsing Apple Card screenshots. While OpenCV/Tesseract handle them slightly differently than Apple's VisionKit, it provided a good starting point.

