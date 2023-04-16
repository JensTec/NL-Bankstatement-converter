# NL-Bankstatement-converter

NL Bankstatement converter is a small application to convert `csv` and `pdf` files from four Dutch banks and one credit card provider into a `csv` format that can be easily imported into [GNUCash](https://github.com/Gnucash/gnucash).

The five banks/cards that are currently supported:
* Rabobank - download transactions in `csv` file
* ASN Bank - download transactions in `csv` file
* ING Bank - download transactions in `csv` file
* ANWB VISA ICS Credit Card - download transactions in monthly account statement `pdf`
* Openbank / Santander - download transactions in `pdf` file

## Configuration

Set your settings in the properties file, like path and name as it is shown on your ANWB Visa ICS Credit Card.

## Usage

1. Download the transactions from your bank (ING, ASN, Openbank and RaboBank) or monthly account statement (ANWB VISA Card) to the folder you defined in the properties file.
2. Launch the application and select the file you would like to convert. A summary will be given on the screen, and at the same time the `csv` output file will be written to the same folder.
3. Import your transactions into GNUCash by importing transactions in the CSV format.

### Extra tip

Make this file executable under MacOS:

* Change the extension of the file to .command
* In Terminal make the Python script file executable by running ``chmod +x GNU_Convert.command``
* Now you can double-click your Python script within MacOS and it will open a terminal window and run the script
