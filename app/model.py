# coding: utf8
import sqlite3
from sqlite3 import OperationalError, IntegrityError, ProgrammingError
import datetime
#FV
import os
from fpdf import FPDF
import time


class Database:

    def CreateConnection(self, db = None):
        """Tworzy połączenie z bazą. Jeżeli został przekazany argument db to zostanie utworzony plik sqlite z podaną nazwą.
        Jeżeli argument db pozostanie pusty, wówczas baza zostanie utworzona w pamięci ulotnej i nie zostanie zapisana na dysku.
        Funkcja zwraca połączenie z bazą.
        """
        if db is None:
            mydb=':memory:'
            print("New connection to in-memory DB")
        else:
            mydb = "{}.db".format(db)
            print("Utworzono nowy plik bazy danych o nazwie: "+ mydb)
        connection = sqlite3.connect(mydb)
        return connection

    def CreateCursor(self, conn = None):
        """Tworzy cursor służący do poruszania się po bazie. Jeżeli jako argument nie zostanie przekazane połączenie to wyświetlony zostanie komunikat.
        Funkcja zwraca cursor.
        """
        if conn is None:
            print("There is no connection")
        else:
            cur = conn.cursor()
        return cur

    def CreateTables(self, cur):
        """Tworzy tabele w pliku bazy danych. Tworzone tabele to: id, imie, nazwisko, telefon, email, rejestr, date, endDate, comments, testType.
        Zwraca wartość True w przypdku powodzenia i treść błędu w przypadku niepowodzenia.
        """
        try:
            #cur.execute("DROP TABLE IF EXISTS gabinet;")
            cur.execute("""
                            CREATE TABLE IF NOT EXISTS gabinet (
                                id INTEGER PRIMARY KEY ASC,
                                nazwisko varchar(250),
                                imie varchar(250),                               
                                telefon varchar(250),
                                email varchar(250),
                                rejestr varchar(250),
                                date varchar(250),
                                endDate varchar(250),                        
                                comments TEXT,
                                testType varchar(250)                                                                              
                            )
                    """)
            return True

        except Exception as error:
            return error

    def DbAddClient(self, surname, name, phone, mail, rejestr, date, endDate, comment, testType, cur, conn):
        """Tworzy nowy wpis danych. Dodaje klienta na podstawie otrzymanych argumentów. Jako argumenty przyjmuje również cursor i połączenie z bazą.
        Zwraca wartość True w przypadku powodzenia i treść błędu w przypadku niepowodzenia.
        """
        try:
            cur.execute('INSERT INTO gabinet VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (surname, name, phone, mail, rejestr, date, endDate, comment, testType))
            conn.commit()
            return True
        except Exception as error:
            return error

    def DbAllClients(self, cur, conn, word, search = None):
        """Przeszukuje bazę według otrzymanych kryteriów. Jako atrybuty przyjmuje:
        -> cur - cursor
        -> conn - połączenie z bazą danych
        -> word - szukane słowo
        -> search -> może przyjąć wartości:
                    -> None - szuka wszystkiich wpisów i szereguje je alfabetycznie według nazwiska
                    -> True - szuka we wszystkich tabelach podanego słowa
                    -> nazwa_tabeli - szuka w przekazanej tabeli podanego słowa
        Zwraca wynik wykonanego zapytania w przypadku powodzenia lub zwraca treść błędu w przypadku niepowodzenia
        """
        if search is None:
            query = """
            SELECT * FROM gabinet ORDER BY nazwisko ASC;
            """
        elif search is True:
            query = """SELECT * FROM gabinet WHERE 
            imie LIKE "%{0}%" OR 
            nazwisko LIKE "%{0}%" OR 
            telefon LIKE "%{0}%" OR
            email LIKE "%{0}%" OR
            rejestr LIKE "%{0}%" OR
            date LIKE "%{0}%" OR
            endDate LIKE "%{0}%" OR
            comments LIKE "%{0}%" OR 
            testType LIKE "%{0}%"  """.format(word)

        else:
            query = """SELECT * FROM gabinet WHERE {0} LIKE "%{1}%" """.format(search, word)

        try:
            rows = cur.execute(query)
            allClients = cur.fetchall()
            return allClients
        except Exception as error:
            print(error)
            return error

    # def DbDeleteClient(self, clientID, cur, conn):
    #     #     query = """DELETE FROM gabinet where id={0}""".format(clientID)
    #     #     try:
    #     #         cur.execute(query)
    #     #         conn.commit()
    #     #         return True
    #     #     except Exception as error:
    #     #         return error
    #     #
    #     # def DbUpdateClient(self, clientData, cur, conn):
    #     #     print(clientData)
    #     #     query = """UPDATE gabinet SET nazwisko="{0}", imie="{1}", telefon="{2}", email="{3}",
    #     #      rejestr="{4}", date="{5}", endDate="{6}", comments="{7}", testType="{8}" WHERE id={9}
    #     #      """.format(clientData[1], clientData[2], clientData[3], clientData[4], clientData[5], clientData[6], clientData[7], clientData[8], clientData[9], int(clientData[0]))
    #     #     try:
    #     #         cur.execute(query)
    #     #         conn.commit()
    #     #         print("dziala")
    #     #         return True
    #     #     except Exception as error:
    #     #         return error

    def EditOrDelete(self, clientData, delOrEdit, cur, conn):
        """Usuwa lub modyfkuje dane klienta wybranego w tabeli. Jako atrybuty przyjmuje:
        -> clientData - lista danych klienta pobrana z tabeli
        -> delOrEdit - wartość tekstowa określająca czy wybrany wpis ma zostać zmodyfikowany(edit) czy usunięty(del).
        -> cur - cursor
        -> conn - połączenie z bazą
        """

        if delOrEdit == "del":
            query = """DELETE FROM gabinet where id={0}""".format(int(clientData[0]))
        else:
            query = """UPDATE gabinet SET nazwisko="{0}", imie="{1}", telefon="{2}", email="{3}", 
                     rejestr="{4}", date="{5}", endDate="{6}", comments="{7}", testType="{8}" WHERE id={9}
                     """.format(clientData[1], clientData[2], clientData[3], clientData[4], clientData[5], clientData[6],
                                clientData[7], clientData[8], clientData[9], int(clientData[0]))
        try:
            cur.execute(query)
            conn.commit()
            print("dziala")
            return True
        except Exception as error:
            return error

class InvoiceFV(FPDF):
    def __init__(self, companyName, companyAdress1, companyAdress2, companyNIP, researchDate, paymentMethod, invoicePositionsList, OwnInvoiceNumber, summarizedPayment, invoiceCreationDate):
        super().__init__()
        self.companyName = companyName
        self.companyAdress1 = companyAdress1
        self.companyAdress2 = companyAdress2
        self.companyNIP = companyNIP
        self.researchDate = researchDate
        self.paymentMethod = paymentMethod
        self.invoicePositionsList = invoicePositionsList
        self.OwnInvoiceNumber = OwnInvoiceNumber
        self.summarizedPayment = summarizedPayment
        self.invoiceCreationDate = invoiceCreationDate

        self.logo = './logo/logo2.png'
        self.add_font('Arial', '', r"c:\WINDOWS\Fonts\arial.ttf", uni=True)
        self.add_font('ArialBold', '', r"c:\WINDOWS\Fonts\arialbd.ttf", uni=True)
        self.add_font('ArialItalic', '', r"c:\WINDOWS\Fonts\ariali.ttf", uni=True)
        self.add_page()

    def header(self):
        # Logo
        self.image(self.logo, 15, 15, 55)
        # Czcionka
        self.set_font('Arial', '', 10)
        # Dane o FV
        self.set_xy(10,30)
        self.cell(0, 5, 'Miejsce wystawienia: Żabno', 0, 2, 'R')
        self.cell(0, 5, 'Data wystawienia: {0}'.format(self.invoiceCreationDate), 0, 2, 'R')
        self.cell(0, 5, 'Data wykonania usługi: {0}'.format(self.researchDate), 0, 2, 'R')
        # Line break
        self.ln(15)

    def footer(self):
        # Pozycja ustawiona na 2.5 cm od dołu strony
        self.set_y(-25)
        # Czcionka: Arial italic 8
        self.set_font('Arial', '', 6)
        # Treść stopki
        self.cell(0, 5, 'MEDIKAP Maria Kapa ', 0, 2, 'C')
        self.cell(0, 5, 'Plac Grunwaldzki 15B, 33-240 Żabno ', 0, 2, 'C')
        self.cell(0, 5, 'e-mail: gabinet.medikap@gmail.com tel: 539 993 332', 0, 2, 'C')
        self.cell(0, 5, 'NIP: 9930212793 REGON: 852441210', 0, 0, 'C')

    def InvoiceTitle(self, invoiceNum):
        self.set_font('ArialBold','', 20)
        self.cell(0, 5, 'Faktura nr: {0}'.format(invoiceNum), 0, 2, '')
        self.ln(15)

    def InvoiceClientData(self, invoicePostionList):
        self.set_font('ArialBold', '', 13)
        self.cell(80, 5, 'Sprzedawca', 'B', 0, '')
        self.cell(35, 15, '', '', 0, '')
        self.cell(80, 5, 'Nabywca', 'B', 2, '')

        self.ln(5)
        self.set_font('Arial', '', 11)

        self.cell(80, 5, 'MEDIKAP Maria Kapa', 0, 0, '')
        self.cell(35, 15, '', '', 0, '')
        if len(self.companyName) > 30:
            self.set_font('Arial', '', 9)
        elif len(self.companyName) > 40:
            self.set_font('Arial', '', 8)
        self.cell(80, 5, '{0}'.format(self.companyName), 0, 2, '')
        self.ln(1)
        self.set_font('Arial', '', 11)
        self.cell(80, 5, 'Plac Grunwaldzki 15B, 33-240 Żabno', 0, 0, '')
        self.cell(35, 15, '', '', 0, '')
        self.cell(80, 5, '{0}'.format(self.companyAdress1), 0, 2, '')
        self.ln(1)
        self.cell(80, 5, 'NIP: 9930212793', 0, 0, '')
        self.cell(35, 15, '', '', 0, '')
        self.cell(80, 5, '{0}'.format(self.companyAdress2), 0, 2, '')
        self.ln(1)
        self.cell(80, 5, 'REGON: 852441210', 0, 0, '')
        self.cell(35, 15, '', '', 0, '')
        self.cell(80, 5, 'NIP: {0}'.format(self.companyNIP), 0, 2, '')
        self.ln(1)
        self.cell(80, 5, 'Bank: ING Bank Śląski', 0, 0, '')
        self.cell(35, 15, '', '', 0, '')
        self.cell(80, 5, 'Forma płatności: {0}'.format(self.paymentMethod), 0, 2, '')
        self.ln(1)
        self.cell(80, 5, 'Nr konta: 84 1050 1562 1000 0097 1773 0833', 0, 2, '')
        self.ln(15)

        # Tabelka tytuły
        tableTitle = ['L.p.', 'Nazwa usługi','PKWiU', 'Ilość', 'J.m.', 'Cena', 'Wartość']
        self.set_font('ArialBold', '', 8)
        self.FillTable(tableTitle)

        # Tabelka pozycje
        self.set_font('Arial', '', 8)
        for singlePosition in invoicePostionList:
            self.FillTable(singlePosition)


        # Podsumowanie
        self.set_x(160)
        self.cell(20, 10, 'Razem (PLN)', 1, 0, 'C')
        self.cell(20, 10, '{0}'.format(self.summarizedPayment + ',00'), 1, 0, 'C')

        self.ln(10)
        self.cell(80, 5, 'Podstawa zwolnienia z VAT:', 0, 2, '')
        self.cell(80, 5, 'Zwolenienie ze względu na zakres wykonywanych czynności (art. 43 ust. 1) pkt 19 Ustawy o VAT', 0, 2, '')
        self.ln(5)
        self.cell(50, 5, 'razem: {0} PLN'.format(self.summarizedPayment+ ',00'), 0, 2, '')

        if self.paymentMethod == 'przelew':
            alreadyPayed = '0'
            paymentLeft = str(self.summarizedPayment)
            paymentDeadline = (datetime.date.today() + datetime.timedelta(days = 7)).strftime('%d.%m.%Y')
        else:
            alreadyPayed = str(self.summarizedPayment)
            paymentLeft = '0'
            paymentDeadline = self.researchDate

        self.cell(50, 5, 'zapłacono: {0} PLN'.format(alreadyPayed), 0, 2, '')
        self.cell(50, 5, 'pozostało do zapłaty: {0} PLN'.format(paymentLeft), 0, 2, '')

        self.ln(5)
        self.set_font('ArialBold', '', 8)
        self.cell(50, 5, 'Termin płatności: {0}'.format(paymentDeadline), 0, 2, '')

        self.ln(10)
        self.set_x(20)
        self.set_font('Arial', '', 8)
        self.cell(50, 5, '.......................................................', 0, 0, '')
        self.cell(65, 15, '', '', 0, '')
        self.cell(50, 5, '............................................................', 0, 0, '')

        self.set_font('Arial','', 6)
        self.ln(3)
        self.set_x(20)
        self.cell(50, 5, 'podpis osoby upoważnionej do odbioru faktury', 0, 0, '')
        self.cell(65, 15, '', '', 0, '')
        self.cell(50, 5, 'podpis osoby upoważnionej do wystawienia faktury', 0, 0, '')


    def FillTable(self, elementList):
        rowWidth = [20, 70, 20, 20, 20, 20, 20]
        i=0
        for element in elementList:
            self.cell(rowWidth[i], 10, element, 1, 0, 'C')
            i+=1

        self.ln()

    def InvoiceCounter(self):
        if self.OwnInvoiceNumber == False:
            month = datetime.date.today().today().strftime('%m')
            year = datetime.date.today().year

            fileName = "invoiceNumber.txt"

            fileOpened = open(fileName, 'r+')
            content = fileOpened.read().split('/')

            if content[1] == str(month):
                number = int(content[0])
                number+=1
            else:
                number = 1

            invoiceNumber = str(number) + "/" + str(month) + "/" + str(year)
            fileOpened.seek(0)
            fileOpened.truncate()
            fileOpened.write(invoiceNumber)
            fileOpened.close()
            return invoiceNumber
        else:
            return self.OwnInvoiceNumber

    def PrintInvoice(self):
        self.CreateFolder()
        invoiceNumber = self.InvoiceCounter()
        self.InvoiceTitle(invoiceNumber)
        self.InvoiceClientData(self.invoicePositionsList)

        newName = invoiceNumber.split('/')
        folder = "./faktury/"
        fileName = str(folder + newName[0] + '-' + newName[1] + '-' + newName[2] + '.pdf')

        try:
            self.output(fileName, 'F')
            return True
        except Exception as error:
            return error

    def CreateFolder(self):
        if os.path.isdir("./faktury") == False:
            os.mkdir("./faktury")











