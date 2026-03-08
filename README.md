[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/JensTec/NL-Bankstatement-converter/)
[![nl](https://img.shields.io/badge/lang-nl-yellow.svg)](https://github.com/JensTec/NL-Bankstatement-converter/blob/main/README.nl.md)
***

# NL-Bankstatement-converter

NL Bankstatement converter is a small application to convert `csv`, `xlsx` and `pdf` files from five Dutch banks, one Spanish bank and one credit card provider into a `csv` format that can be easily imported into [GnuCash](https://github.com/Gnucash/gnucash).

### The seven banks/cards that are currently supported: 

Transaction data provided in `csv` format:
* Rabobank
* ASN Bank
* ING Bank
* Bunq Bank

Transactions data provided in `pdf` format:
* ANWB VISA ICS Credit Card
* Openbank / Santander
 
Transactions data provided in `xlsx` format:
* BBVA Bank Spain

## Configuration

Set your settings in the properties file, like path, name and accountnumber as it is shown on your ANWB Visa ICS Credit Card. If you have Bunq accounts, put unique IBAN identifiers here as well.

If you want the input files to be automatically deleted after the conversion process has finalized, set `AUTO_DELETE` to `YES`. If set to `NO`, input files are archived in the folder `/Archive`. 


## Usage

1. Download the transactions from your bank (ING, ASN, Openbank, Bunq, BBVA and RaboBank) or monthly account statement (ANWB VISA Card) to the folder you defined in the properties file.
2. Launch the application and select the file you would like to convert. A summary will be given on the screen, and at the same time the `csv` output file will be written to the same folder.
3. Import your transactions into GnuCash by importing transactions in the CSV format.

### Extra tip

Make this file executable under MacOS:

* Change the extension of the file to .command
* In Terminal make the Python script file executable by running ``chmod +x Statement_Converter.command``
* Now you can double-click your Python script within MacOS and it will open a terminal window

Inspiration to solve the Openbank [pdfplumber](https://pypi.org/project/pdfplumber/#extracting-tables) challenge: 
[jsvine](https://github.com/jsvine/pdfplumber/blob/stable/examples/notebooks/extract-table-nics.ipynb).

If you would like me to add your bank statement format as well, just give me a shout.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X1O747G)


