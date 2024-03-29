[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/JensTec/NL-Bankstatement-converter/)
[![nl](https://img.shields.io/badge/lang-nl-yellow.svg)](https://github.com/JensTec/NL-Bankstatement-converter/blob/main/README.nl.md)
***

# NL-Bankstatement-converter

NL-Bankstatement-converter is een kleine applicatie om `csv` en `pdf` bestanden van vijf Nederlandse banken en één creditcardaanbieder om te zetten naar een `csv` bestandsformaat dat eenvoudig geïmporteerd kan worden in [GnuCash](https://github.com/Gnucash/gnucash).

De zes banken/kaarten die momenteel worden ondersteund:
* Rabobank - download de transacties in een `csv` bestand
* ASN Bank - download de transacties in een `csv` bestand
* ING Bank - download de transacties in een `csv` bestand
* ANWB VISA ICS Creditcard - download een maandafschrift in `pdf`
* Openbank / Santander - download transacties in een `pdf` bestand
* Bunq Bank - download transacties in een `csv` bestand

## Configuratie

Stel uw instellingen in het `properties` bestand, zoals de directory en uw naam zoals deze wordt weergegeven op uw ANWB Visa ICS-creditcard. Als u Bunq-accounts heeft, plaats dan hier ook uw unieke IBAN-id's.

Als u wilt dat de invoerbestanden automatisch worden verwijderd nadat het conversieproces is voltooid, dan stelt u `AUTO_DELETE` in op `YES`. Als deze setting op `NO` staat, dan wordt het invoerbestand automatisch gearchiveerd in de directory `/Archive'.

## Gebruik

Download de transacties van uw bank (ING, ASN, Openbank, Bunq en RaboBank) of maandafschrift (ANWB VISA Card) naar de map die u in het `properties` bestand heeft gedefiniëerd.
Start de applicatie en selecteer het bestand dat u wilt converteren. Er wordt een samenvatting op het scherm gegeven en tegelijkertijd wordt het csv-uitvoerbestand naar dezelfde map geschreven.

Importeer uw transacties in GnuCash door transacties in de `csv` indeling te importeren.

## Extra tip

Maak uw Python applicatie uitvoerbaar onder MacOS:

- Wijzig de extensie van het bestand in `.command`
- Maak in Terminal het Python-scriptbestand uitvoerbaar door `chmod +x Statement_Converter.command` uit te voeren
- Nu kunt u dubbelklikken op uw Python applicatie in MacOS en het opent in een terminalvenster

Inspiratie om de Openbank [pdfplumber](https://pypi.org/project/pdfplumber/#extracting-tables) challenge op te lossen: [jsvine](https://github.com/jsvine/pdfplumber/blob/stable/examples/notebooks/extract-table-nics.ipynb).

Als u wilt dat ik ook uw bankafschriftformaat toevoeg, stuur me simpelweg een berichtje.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/X8X1O747G)
