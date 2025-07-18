#!/usr/local/bin/python3.9

# ------------ import functions ---------------------------------
import csv
import os
from datetime import datetime
from tabulate import tabulate
import pdfplumber
from jproperties import Properties
import shutil

# ------------ define global variables ---------------------------
fields = []  # create list with original headers
rows = []  # create list with all rows
csvfile = ""
filename = ""
bank = ""
visa_file = ""

# reading the properties from the properties file
configs = Properties()  # instantiate the Properties object
with open('SC_user_data.properties', 'rb') as config_file:  # load the properties file into the Properties object
    configs.load(config_file)

path = configs.get("FILE_PATH").data  # path where the csv and pdf files are saved
archivepath = str(path + "/archive")  # creates name and directory for archiving files
bunq_acc = [  # creating list with unique identifiers to distinguish between bunq accounts
    configs.get("BUNQ_ACCOUNT1").data,
    configs.get("BUNQ_ACCOUNT2").data,
    configs.get("BUNQ_ACCOUNT3").data,
    configs.get("BUNQ_ACCOUNT4").data
    ]


# ------------ menu function ---------------------------
def menu():
    global path
    global fields
    global rows
    global csvfile
    global filename
    global bunq_acc
    files = []  # create list with all the csv file names
    filenumber = 1

    print("")
    print("Available .csv & .pdf files in %s: " % path)
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
        raise SystemExit
    else:
        filename = str(path + "/" + files[file_input])  # creating the variable which will be used in reading the file

    if 'document' in filename: # before May 2025 ICS ANWB used the word 'Overzicht' but this changed in a recent update.
        visa()
    elif 'Rekeningtransacties' in filename:
        ob()
    elif 'Brubank' in filename:
        brubank()
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
            elif bunq_acc[0] or bunq_acc[1] or bunq_acc[2] or bunq_acc[3] in filename:  #
                fields = next(csvreader)  # extracting field names through first row
                for row in csvreader:  # extracting each data row one by one
                    rows.append(row)
                bunq()
            elif 'INGB' in filename:
                fields = next(csvreader)  # extracting field names through first row
                for row in csvreader:  # extracting each data row one by one
                    rows.append(row)
                ing()
            else:
                print("This file is not supported.")
                menu()


# ------------- convert data into the required output for Brubank - Argentina --------
def brubank():
    global rows
    global bank
    global filename
    bank = "Brubank"  # set variable to Brubank
    customlines = {29, 62, 70, 122, 135, 380, 430, 443, 510, 565}  # demark vertical lines
    table_settings = {  # used by pdfplumber to correctly extract the table from the pdf
        "explicit_vertical_lines": customlines,
        "horizontal_strategy": "text",
        "snap_y_tolerance": 5,
        "intersection_x_tolerance": 15,
    }

    i = 0  # counter for number of pages

    with pdfplumber.open(filename) as pdf:  # open PDF
        for page in pdf.pages:
            allpages = pdf.pages[i].extract_table(table_settings)  # extract table from all pages
            # test area to write pdfplumber debug info to a png file.
            p0 = pdf.pages[0]
            im = p0.to_image()
            im.reset().debug_tablefinder(table_settings)
            im.save("/Users/Sietse/Downloads/test.png", format="PNG", quantize=True, colors=256, bits=8)

            for row in allpages[24:]:
                if not row[0] == '':
                    del row[1:3]
                    del row[1]
                rows.append(row)
                continue
        i += 1  # increase counter for number of pages
        print(rows)
    filecreation()


# ------------- convert data into the required output for Openbank --------
def ob():
    global rows
    global bank
    global filename
    bank = "Openbank"  # set variable to Openbank
    # customlines = {27, 77, 152, 384, 413, 458}  # table_settings to demark vertical lines of cells (old PDF format OB)
    customlines = {52, 102, 177, 405, 426, 477}  # new version to demark vertical lines after change (?) of OB format
    table_settings = {  # used by pdfplumber to correctly extract the table from the pdf
        "explicit_vertical_lines": customlines,
        "horizontal_strategy": "lines"
    }

    i = 0  # counter for number of pages

    with pdfplumber.open(filename) as pdf:  # open PDF
        for page in pdf.pages:
            allpages = pdf.pages[i].extract_table(table_settings)  # extract table from all pages
            for row in allpages[:-1]:  # -1 due to additional line to PDF (last line with text)
                if not row[0] == '':
                    amount = row[4].replace(".", "")  # remove .
                    amount = amount.replace(",", ".")  # convert amount with comma to decimal point
                    amount = amount.strip()  # remove all spaces
                    amount = float(amount)  # convert string to float
                    if amount < 0:  # check if it should be in the column withdrawal or deposit
                        row.insert(0, amount * -1)  # insert amount in withdrawal column
                        row.insert(1, "")
                    else:
                        row.insert(0, "")
                        row.insert(1, amount)  # insert amount in deposit column
                    row.insert(6, row[2])
                    del row[2:4]  # delete dates at beginning of row
                    del row[3]
                    del row[4]
                    row.insert(3, "")
                    descr = str(row[2]).replace("\n", "")
                    descr = descr.replace("REFERENTIE", " -")  # replace the recurring "REFERENTIE" with a simple "-"
                    row[2] = descr
                    rows.append(row)
                continue
            i += 1  # increase counter for number of pages
    filecreation()


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


# ------------- convert data into the required output for Bunq Bank --------
def bunq():
    global rows
    global bank
    global bunq_acc

    if bunq_acc[0] in rows[0][3]:
        bank = "Bunq Joint Account"  # you can insert any name here
    elif bunq_acc[1] in rows[0][3]:
        bank = "Bunq ES Deduction Account"
    elif bunq_acc[2] in rows[0][3]:
        bank = "Bunq Savings Account"
    elif bunq_acc[3] in rows[0][3]:
        bank = "Bunq Bizum Account"
    else:
        bank = "Bunq unknown"

    for row in rows:
        var1 = row[2].replace(".", "")
        var2 = var1.split(",")  # split amount into two strings
        amount = float(str(var2[0] + "." + var2[1]))  # make it a float
        if amount < 0:  # check if it should be in the column withdrawal or deposit
            row.insert(0, -1 * amount)  # multiplying by -1 to have the amount with 'minus' sign
            row.insert(1, "")
        else:
            row.insert(0, "")
            row.insert(1, amount)

        if row[6] == "":  # only show this string if it is not empty
            one = ""
        else:
            one = str(row[6] + " - ")
        if row[7] in row[8]:  # prevent information showing twice
            two = str(row[8])
        else:
            two = str(row[7] + " - " + row[8])
        row.insert(2, (one + two))  # inserting description
        row.insert(3, "")  # inserting empty volgnummer
        row.insert(4, row[4])  # inserting date
        del row[5:14]  # delete columns not needed

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


# ------------- convert data into the required output for ANWB Visa Credit Card --------
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
    i = 0  # counter for number of pages
    j = 0  # counter for first rows to add to pagemetadate
    k = 0

    months = {'jan.': 1, 'feb.': 2, 'mrt.': 3, 'apr.': 4, 'mei': 5, 'jun.': 6, 'jul.': 7, 'aug.': 8, 'sep.': 9, 'okt.': 10,
              'nov.': 11, 'dec.': 12}

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
                     'Telefoon', 'Kvk', 'Nu beschikbaar', 'Voeg', card1, card2)

        for page in pdf.pages:
            pageprint = pdf.pages[i].extract_text()  # extract text from all pages
            for row in pageprint.splitlines():  # split each line into a row
                if not row.startswith(checklist):  # drop all lines that start with words from the 'checklist'
                    intermediate.append(row)  # add all rows to new list called 'intermediate'
            i += 1  # increase counter for number of pages

        try:
            intermediate.index(card1)  # determine if card1 is present
        except ValueError:
            card1status = 0  # variable that card is not present
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
                card2status = 0  # card2 is not present
            else:
                card2status = 1  # card 2 is present
                pos2 = intermediate.index(card2)  # index of card2 position

        if (card1status + card2status) == 2:  # both cards are present
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

        if 'januari' in visa_file and rowsplit[1] == 'dec.':  # this corrects the year in December when the statement
            # arrives in January
            newdate = str(rowsplit[0] + "-" + str(months.get(rowsplit[1])).zfill(2) + "-" + str(int(year) - 1))
        else:
            newdate = str(rowsplit[0] + "-" + str(months.get(rowsplit[1])).zfill(2) + "-" + year)  # lookup month and
            # convert to date
        rowsplit.insert(0, newdate)  # insert correct date into file

        amount = rowsplit[length - 1].replace(".", "")  # remove .
        amount = amount.replace(",", ".")  # convert amount with comma to decimal point
        if rowsplit[-1] == "Af":  # check if it should be in the column withdrawal or deposit
            rowsplit.insert(0, amount)  # insert amount in withdrawal column
            rowsplit.insert(1, "")
        else:
            rowsplit.insert(0, "")
            rowsplit.insert(1, amount)  # insert amount in deposit column
        rowsplit.insert(2, "")

        if (card1status + card2status) == 0:  # empty statement
            description = " ".join(rowsplit[8:length + 2])
        elif (card1status + card2status) == 1:  # one of both cards is present
            description = initial1 + " ".join(rowsplit[8:length + 2])
        else:  # both cards are present
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
        del rowsplit[5:]  # delete all remaining fields
        rows.append(rowsplit)
    filecreation()


# --------------- create unique name, write the file and show results --------------------
def filecreation():
    global csvfile
    global filename
    global bank
    global rows
    global visa_file

    auto_delete = configs.get("AUTO_DELETE").data  # auto delete input file , yes or no?
    a = datetime.now()  # unique timestamp
    filename_write = str(path + "/" + bank + visa_file + " - GnuCash import " +
                         str(a.year) + str(a.month).zfill(2) + str(a.day).zfill(2) + "_" + str(a.hour).zfill(2) +
                         str(a.minute).zfill(2) + ".csv")

    fields_output = ["Withdrawal", "Deposit", "Description", "Number", "Date"]

    with open(filename_write, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)  # creating a csv writer object
        csvwriter.writerow(fields_output)  # writing the fields
        csvwriter.writerows(rows)  # writing the data rows

    print("You have converted the file: '" + filename[len(path) + 1:] + "' from %s." % bank)
    print('\n')
    print(tabulate(rows, headers=fields_output))  # printing the table on screen with the data

    if auto_delete == "YES":
        os.remove(filename)
        print("")
        print("File %s has been removed successfully." % filename)
    else:  # if auto_delete is set to "NO", the input file will be archived in a separate folder
        if not os.path.exists(archivepath):  # check if the archivepath folder already exists
            os.mkdir(archivepath)
            print('\n')
            print("Folder '%s' has been created." % archivepath)
        shutil.move(filename, archivepath)  # move inputfile to 'archivepath'
        print("The input file has been moved to %s." % archivepath)
    print("----------------------------------------------------------------------")

    # reset values and return to menu()
    rows = []  # reset rows list
    visa_file = ""  # reset visa file addition
    menu()


# ------------ start menu ---------------------------
print("")
print("NL-Bankstatement-converter for GnuCash - written by JensTec")
menu()
