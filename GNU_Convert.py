#!/usr/local/bin/python3.9

# ------------ import functions ---------------------------------
import csv
import os
from datetime import datetime
from tabulate import tabulate
import pdfplumber
from jproperties import Properties


# ------------ define global variables ---------------------------
fields = []                             # create list with original headers
rows = []                               # create list with all rows
configs = Properties()                  # instantiate the Properties object
with open('GNU_user_data.properties', 'rb') as config_file:  # load the properties file into the Properties object
    configs.load(config_file)

path = configs.get("FILE_PATH").data  # path where the csv files are saved
csvfile = ""
filename = ""
bank = ""
visa_file = ""


# ------------ menu function ---------------------------
def menu():
    global path
    global fields
    global rows
    global csvfile
    global filename
    files = []  # create list with all the csv file names
    filenumber = 1

    print("")
    print("Available .csv & .pdf files : ")
    for x in os.listdir(path):  # show available csv and pdf files in path, and ability to select the correct one
        if x.endswith(".csv") or x.endswith(".pdf"):
            files.append(x)
    files.sort()

    for f in files:
        print(str(filenumber) + " - " + files[filenumber - 1])
        filenumber += 1
    exit_number = filenumber
    print(str(exit_number) + " - Exit")
    print('\n')

    file_input = int(input("Choose the file to convert : ")) - 1

    if (file_input + 1) == exit_number:  # create option to exit the software gracefully
        print("")
        print("Goodbye!")
        raise SystemExit
    else:
        filename = str(path + "/" + files[file_input])  # creating the variable which will be used in reading csv part

    if 'overzicht' in filename:
        visa()
    else:  # reading csv selected file
        with open(filename, 'r', errors='ignore') as csvfile:  # errors='ignore' due to some characters in Rabobank
            csvreader = csv.reader(csvfile)  # creating a csv reader object
            if 'RABO' in filename:
                fields = next(csvreader)  # extracting field names through first row
                for row in csvreader:  # extracting each data row one by one
                    rows.append(row)
                rabo()
            elif 'ASN' in filename:
                for row in csvreader:  # extracting each data row one by one
                    rows.append(row)
                asn()
            elif 'NL15INGB' in filename:
                fields = next(csvreader)  # extracting field names through first row
                for row in csvreader:  # extracting each data row one by one
                    rows.append(row)
                ing()
            else:
                print("This file is not supported.")
                end()


# ------------- convert data into the required output for RABOBANK --------
def rabo():
    global rows
    global bank
    bank = "Rabobank"  # set variable to Rabobank
    for row in rows:
        var1 = row[6].split(",")  # split "bedrag" into two strings
        amount = float(str(var1[0] + "." + var1[1]))  # make it a float
        if amount < 0:  # check if it should be in the column withdrawal or deposit
            row.insert(0, -1 * amount)  # multiplying by -1 to have the amount with 'minus' sign
            row.insert(1, "")
        else:
            row.insert(0, "")
            row.insert(1, amount)
        description = str(row[11] + " - " + row[21])  # creating description string
        row.insert(2, description)  # inserting description
        volgnummer = int(row[6])  # convert volgnummers from string to int
        row.insert(3, volgnummer)  # inserting volgnummer
        del row[4:8]  # delete columns not needed
        del row[5:26]  # delete columns not needed
    filecreation()


# ------------- convert data into the required output for ING Bank --------
def ing():
    global rows
    global bank
    bank = "ING Bank"  # set variable to ING Bank
    for row in rows:
        var1 = row[6].split(",")  # split "bedrag" into two strings
        amount = float(str(var1[0] + "." + var1[1]))  # make it a float
        if row[5] == "Af":  # check if it should be in the column withdrawal or deposit
            row.insert(0, amount)
            row.insert(1, "")
        else:
            row.insert(0, "")
            row.insert(1, amount)
        description = str(row[3] + " - " + row[10])  # creating description string
        row.insert(2, description)  # inserting description
        row.insert(3, "")  # inserting volgnummer
        # here insert last treatment of date column
        day = str(row[4][6:8] + "-" + row[4][4:6] + "-" + row[4][:4])
        print(day)
        row.insert(4, day)
        del row[5:14]  # delete columns not needed
    filecreation()


# ------------- convert data into the required output for ASN Bank --------
def asn():
    global rows
    global bank
    bank = "ASN Bank"  # set variable to ASN Bank
    for row in rows:
        var1 = row[10].split(".")  # split "bedrag" into two strings
        amount = float(str(var1[0] + "." + var1[1]))  # make it a float
        if amount < 0:  # check if it should be in the column withdrawal or deposit
            row.insert(0, -1 * amount)  # multiplying by -1 to have the amount with 'minus' sign
            row.insert(1, "")
        else:
            row.insert(0, "")
            row.insert(1, amount)
        description = str(row[5] + " - " + row[19])  # creating description string
        row.insert(2, description)  # inserting description
        row.insert(3, "")  # inserting empty volgnummer
        del row[5:23]  # delete columns not needed
    filecreation()


# ------------- convert data into the required output for ASN Bank --------
def visa():
    global bank
    global rows
    global filename
    global visa_file
    bank = "ANWB Visa Card"
    card1 = configs.get("VISA_CARD1").data
    card2 = configs.get("VISA_CARD2").data
    cardinit1 = str(configs.get("VISA_CARD1_INIT").data + " - ")
    cardinit2 = str(configs.get("VISA_CARD2_INIT").data + " - ")
    intermediate = []
    metadate = []
    i = 0   # counter for number of pages
    j = 0   # counter for first rows to add to pagemetadate
    k = 0

    months = {'jan': 1, 'feb': 2, 'mrt': 3, 'apr': 4, 'mei': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'okt': 10,
              'nov': 11, 'dec': 12}

    with pdfplumber.open(filename) as pdf:  # open PDF
        pagemetadate = pdf.pages[0].extract_text()  # extract first page to extract meta data
        for row in pagemetadate.splitlines():
            metadate.append(row)  # add first 7 lines to metadate list
            j += 1
            if j == 7:
                break

        dateline = metadate[6].split(" ")  # split line with date
        checkdate = " ".join(dateline[0:3])  # this generates the dynamic date string to add to the checklist
        year = dateline[2]  # generate year variable to later concatenate the date
        visa_file = str(" " + " ".join(dateline[1:3]))  # this generates the dynamic date string to add to the filename

        checklist = ('Wisselkoers', 'Uw ', 'Het totale', 'machtigingsnummer', 'Bestedingslimiet', '€', 'Dit',
                     'Datum', 'transactie', 'Vorig', checkdate, 'International', 'Postbus', '1100 DS', 'worden', 'E',
                     'Telefoon', 'Kvk')

        for page in pdf.pages:
            pageprint = pdf.pages[i].extract_text()  # extract text from all pages
            for row in pageprint.splitlines():  # split each line into a row
                if not row.startswith(checklist):  # drop all lines that start with words from the 'checklist'
                    intermediate.append(row)  # add all rows to new list called 'intermediate'
            i += 1  # increase counter for number of pages

        try:
            intermediate.index(card1)  # determine of card1 is present
        except ValueError:
            card1status = 0     # variable that card is not present
            try:
                intermediate.index(card2)  # determine of card2 is present
            except ValueError:
                card2status = 0  # both cards are not present
            else:
                card2status = 1
                pos1 = intermediate.index(card2)
        else:
            card1status = 1
            pos1 = intermediate.index(card1)
            try:
                intermediate.index(card2)  # determine of card2 is present
            except ValueError:
                card2status = 0     # card2 is not present
            else:
                card2status = 1     # card 2 is present
                pos2 = intermediate.index(card2)       # index of card2 position

        if (card1status + card2status) == 2:        # both cards are present
            if pos1 < pos2:
                initial1 = cardinit1
                initial2 = cardinit2
                del intermediate[pos2]  # delete card on pos 2 from overview
                del intermediate[pos1]  # delete card on pos 1 from overview
            else:
                initial1 = cardinit2
                initial2 = cardinit1
                del intermediate[pos1]  # delete card on pos 1 from overview
                del intermediate[pos2]  # delete card on pos 2 from overview
        elif card1status == 1 and card2status == 0:  # only card1 is present
            initial1 = cardinit1
            del intermediate[pos1]
        elif card1status == 0 and card2status == 1:  # only card2 is present
            initial1 = cardinit2
            del intermediate[pos1]

    for row in intermediate:  # this function cleans each row, and writes final data
        rowsplit = row.split(" ")  # split row into separate columns
        length = len(rowsplit)  # define length for each row

        if 'januari' in visa_file:  # this if corrects the yeaer in december when the statement arrives in January
            if rowsplit[1] == 'dec':
                newdate = str(rowsplit[0] + "-" + str(months.get(rowsplit[1])).zfill(2) + "-" + str(int(year) - 1))
            else:
                newdate = str(rowsplit[0] + "-" + str(months.get(rowsplit[1])).zfill(2) + "-" + year)
        else:
            newdate = str(rowsplit[0] + "-" + str(months.get(rowsplit[1])).zfill(2) + "-" + year)  # lookup month and
                                                                                                # convert to date
        rowsplit.insert(0, newdate)     # insert correct date into file

        amount = rowsplit[length-1].replace(".", "")   # remove .
        amount = amount.replace(",", ".")       # convert amount with comma to decimal point
        if rowsplit[-1] == "Af":  # check if it should be in the column withdrawal or deposit
            rowsplit.insert(0, amount)  # insert amount in withdrawal column
            rowsplit.insert(1, "")
        else:
            rowsplit.insert(0, "")
            rowsplit.insert(1, amount)  # insert amount in deposit column
        rowsplit.insert(2, "")

        if (card1status + card2status) == 0:            # empty statement
            description = " ".join(rowsplit[8:length + 2])
        elif (card1status + card2status) == 1:        # one of both cards is present
            description = initial1 + " ".join(rowsplit[8:length + 2])
        else:           # both cards are present
            if pos1 < (pos2 - 1):
                if k < (pos2 - pos1):
                    k += 1
                    description = initial1 + " ".join(rowsplit[8:length + 2])
                else:
                    description = initial2 + " ".join(rowsplit[8:length + 2])
            else:
                if k < (pos1 - pos2):
                    k += 1
                    description = initial1 + " ".join(rowsplit[8:length + 2])
                else:
                    description = initial2 + " ".join(rowsplit[8:length + 2])
        rowsplit.insert(2, description)
        del rowsplit[5:]                    # delete all remaining fields
        rows.append(rowsplit)
    filecreation()


# --------------- create unique name, write the file and show results --------------------
def filecreation():
    global csvfile
    global filename
    global bank
    a = datetime.now()  # unique timestamp
    filename_write = str(path + "/" + bank + visa_file + " - GNUCash import " +
                         str(a.year) + str(a.month).zfill(2) + str(a.day).zfill(2) + "_" + str(a.hour).zfill(2) +
                         str(a.minute).zfill(2) + ".csv")

    fields_output = ["Withdrawal", "Deposit", "Description", "Number", "Date"]

    with open(filename_write, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)  # creating a csv writer object
        csvwriter.writerow(fields_output)  # writing the fields
        csvwriter.writerows(rows)  # writing the data rows

    print('\n')
    print(filename)
    print('\n')
    print(tabulate(rows, headers=fields_output))  # printing the table on screen with the data

    os.remove(filename)
    print("")
    print("File %s has been removed successfully." % filename)
    end()


# ------------ exit function  ---------------------------
def end():
    global rows
    global visa_file
    print("")
    end_input = str(input("Would you like to exit (y/n)? "))
    if end_input == "n":  # create option to exit the software gracefully
        rows = []           # reset rows list to initial state
        visa_file = ""      # reset visa file addition to initial state
        menu()
    else:
        print("")
        print("Goodbye!")
        raise SystemExit


# ------------ start menu ---------------------------
print("")
print("Welcome to the GNU-Cash bank files converter - made by JensTec (version 1.2)")
menu()
