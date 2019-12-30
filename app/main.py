from PyQt5.QtWidgets import QApplication, QMessageBox, QTableWidgetItem, QAbstractItemView
import sys
from application.guiv3 import TabNewClient, TabSearch, TabInvoice, Window, QIcon
from PyQt5.QtGui import QPixmap
from application.model import Database, InvoiceFV
from PyQt5.QtCore import Qt
import datetime


class Main:
    def __init__(self):
        # zmienna pomocnicza - pełni funkcję flagi
        global editTriggerFlag
        editTriggerFlag = False

    def SetIcon(self, element, iconName):
        """Nadaje ikony przekazanym elementom według zdefiniowanego słownika."""
        iconDict = {
            "ok" : "./icon/ok.png",
            "delete" : "./icon/delete.png",
            "lock" : "./icon/lock.png",
            "unlock" : "./icon/unlock.png",
            "search" : "./icon/search.png",
            "add" : "./icon/add.png",
            "clear" : "./icon/clear.png",
            "createInv" : "./icon/createInv.png",
            "showClients" : "./icon/showClients",
        }

        element.setIcon(QIcon(iconDict.get(iconName)))

    def MessageBox(self, err="info", txt="", add_txt="", title="", details=""):
        """Tworzy MessageBox'a z przekazanych do funkcji argumentów. Funkcja przyjmuje:
        -> err - Definiuje ikonę. Można wpisać 'info' lub 'error'.
        -> txt - Treść pop-upa
        -> add_txt - Dodatkowa treść pop-upa
        -> title - Tytuł pop-upa
        -> details - Dodatkowe szczegóły, które mają zostać wyświetlone np: treść błędu.
        """

        try:
            self.msg = QMessageBox()

            if err == "info":
                self.msg.setIcon(QMessageBox.Information)
            if err == "error":
                self.msg.setIcon(QMessageBox.Warning)

            self.msg.setText(txt)
            self.msg.setInformativeText(add_txt)
            self.msg.setWindowTitle(title)
            self.msg.setDetailedText(details)
            self.msg.setStandardButtons(QMessageBox.Ok)

            self.msg.exec()
        except Exception as err:
            print(err)

    def ClearT1Fields(self):
        """
        ***METODA DO POPRAWY***
        Czyści pola formularzy zawartych w zakładce: Dodaj
        """

        self.tab1.leName.setText("")
        self.tab1.leSurname.setText("")
        self.tab1.lePhone.setText("")
        self.tab1.leMail.setText("")
        self.tab1.leRejestr.setText("")
        self.tab1.teCommentField.setText("")
        self.tab1.leInne.setText("")

    def ClearT3Fields(self):
        """
        ***METODA DO POPRAWY***
        Czyści pola formularzy zawartych w zakładce: Faktura
        """

        self.tab3.leOwnInvoiceNumber.setText("")
        self.tab3.leOtherPrice.setText("")
        self.tab3.leOther.setText("")
        self.tab3.leCompanyAdress1.setText("")
        self.tab3.leCompanyAdress2.setText("")
        self.tab3.leCompanyName.setText("")
        self.tab3.leCompanyNIP.setText("")
        self.tab3.leConsultation.setText("")
        self.tab3.leConsultationPrice.setText("")
        self.tab3.deDate.setDate(datetime.date.today())
        self.tab3.deInvoiceCreateDate.setDate(datetime.date.today())

        self.tab3.cbDriver150.setChecked(False)
        self.tab3.cbAddJudgment.setChecked(False)
        self.tab3.cbConsultation.setChecked(False)
        self.tab3.cbOther.setChecked(False)

    def IsRadioButtonChecked(self, radioButtonGroup, resultsDict):
        """Sprawdza, który RadioButton jest zaznaczony, a następnie przypisuje zmiennej testType
        odpowiednią wartość tekstową. Funkcja zwraca zmiena testType. Przyjmuje jako argumenty:
        -> radioButtonGroup - grupa RadioButtonów, która ma zostać sprawdzona
        -> resultsDict - słownik zawierający poszczególne podstawy prawne przypisane do odpowiednich numerów id RadioButtonów
        """
        #Sprawdza, który RadioButton jest zaznaczony i zwraca jego ID
        try:
            whichRBChecked = str(radioButtonGroup.checkedId())
        except Exception as e:
            return e
        return resultsDict.get(whichRBChecked)

    def AddUserToDB(self):
        """Zbiera dane wpisane w formularzu i przesyła do funkcji odpowiedzialnej za dodanie wpisu do bazy danych"""

        # Słownik zawierający poszczególne podstawy prawne badania w zalezności od id RadioButtona.
        testCauseDict = {
            '0': "kierowca zawodowy",
            '1': "kierowca uprzywilejowany",
            '2': "instruktor / egzaminator",
            '3': "zatrzymane prawo jazdy",
            '4': self.tab1.leInne.text()
        }

        # Zmienne pomocnicze
        name = self.tab1.leName.text()
        surname = self.tab1.leSurname.text()
        phone = self.tab1.lePhone.text()
        mail = self.tab1.leMail.text()
        rejestr = self.tab1.leRejestr.text()
        date = self.tab1.deDate.text()
        endDate = self.tab1.deEndDate.text()
        comment = self.tab1.teCommentField.toPlainText()
        testCause = self.IsRadioButtonChecked(self.tab1.T1rbGroup, testCauseDict)

        # Wywołanie metody dodającej klienta do bazy danych na podstawie przekazanych zmiennych
        newUserResult = self.db.DbAddClient(surname, name, phone, mail, rejestr, date, endDate, comment, testCause, self.cur, self.conn)

        # Wnioskowanie o powodzeniu dodania nowego klienta
        if  newUserResult == True:
            self.MessageBox("info", "Pomyślnie dodano klienta do bazy", "", "UWAGA")
            # Czyszczenie pol formularza
            self.ShowClients()
            self.ClearT1Fields()
        else:
            self.MessageBox("error", "Coś poszło nie tak. Szczegóły znajdziesz poniżej. Zapisz treść błędu do dalszej diagnostyki.", "", "BŁĄD", str(newUserResult))


    def ChangeTab(self, index):
        self.window.tab.setCurrentIndex(index)

    def EditOrDelClient(self, ButtonChoice):
        """W zależności od tego, czy został wciśnięty przycisk: edytuj lub usuń - zaznaczony wpis zostanie wyedytowany lub usunięty.
        Jeżeli żaden wiersz nie został zaznaczony to zostanie wyświetlony komunikat błędu.
        """
        # Lista do, której zostaną wpisane poszczególe wartości zaznaczonego wpisu
        clientData = []

        # Określa numer aktualnie zaznaczonego wiersza
        currentRow = self.tab2.tabwidTable.currentRow()

        # Liczy ile column ma tabela
        columnCount = self.tab2.tabwidTable.columnCount()

        # Sprawdza czy został zaznaczony jakikolwiek wiersz tabeli.
        if str(currentRow) != "-1":
            for column in range(0, columnCount):
                selectedClient = self.tab2.tabwidTable.item(currentRow, column)
                clientData.append(selectedClient.text())

            # Wywołuje metodę bazodanową odpowiedzialną za aktualizację lub usunięcie wpisu
            operationResult = self.db.EditOrDelete(clientData, ButtonChoice, self.cur, self.conn)

            # Jeżeli funkcja bazodanowa zwróci wartość True, wyświetlony zostanie pop-up z informacją, że aktualizacja danych lub ich usunięcie przebiegło pomyślnie.
            # W przeciwnym wypadku wyświtlony zostanie komunikat z treścią zwróconego błędu
            if operationResult == True:
                if ButtonChoice == "edit":
                    self.MessageBox("info", "Zmodyfikowano dane klienta", "", "UWAGA")
                else:
                    self.MessageBox("info", "Usunięto klienta z bazy", "", "UWAGA")
                self.ShowClients()
            else:
                self.MessageBox("error","Coś poszło nie tak. Szczegóły znajdziesz poniżej. Zapisz treść błędu do dalszej diagnostyki.","","BŁĄD", str(operationResult))
        else:
            self.MessageBox("error","Żadna pozycja nie jest zaznaczona !","","BŁĄD")

    def EnableDisableTableEdit(self):
        """Odblokowuje lub blokuje możliwość edycji danych w tabeli. Zmienia również ikonę i opis przycisku.
        Po edycji danych należy zatwierdzić zmiany, by zostały zapisane w bazie.
        """
        global editTriggerFlag

        try:
            if editTriggerFlag == False:
                self.tab2.tabwidTable.setEditTriggers(QAbstractItemView.DoubleClicked)
                self.tab2.btnOnOffEdit.setText("zablokuj edytowanie")
                editTriggerFlag = not editTriggerFlag
                self.SetIcon(self.tab2.btnOnOffEdit, "unlock")
            else:
                self.tab2.tabwidTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
                self.tab2.btnOnOffEdit.setText("odblokuj edytowanie")
                self.SetIcon(self.tab2.btnOnOffEdit, "lock")
                editTriggerFlag = not editTriggerFlag

        except Exception as e:
            print(e)

    def ShowClients(self, search=None, word=""):
        """"Pobiera dane wszystkich klientów z pliku bazy danych a następnie wczytuje je do widoku tabeli."""

        dane = self.db.DbAllClients(self.cur, self.conn, word, search)

        self.tab2.tabwidTable.setRowCount(0)
        for row_number, row_data in enumerate(dane):
            self.tab2.tabwidTable.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tab2.tabwidTable.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def SearchClients(self):
        """Odpowiada za określenie w której kolumnie bazy ma być szukane pobrane z pola tekstowego słowo.
         -> True - sprawia, że podane słowo jest szukane we wszystkich tabelach.
         """
        searchBy = {
            '5': True,
            '6': "imie",
            '7': "nazwisko",
            '8': "telefon",
            '9': "email",
            '10': "rejestr",
            '11': "date",
            '12': "endDate",
            '13': "testType",
        }

        usersChoice = self.IsRadioButtonChecked(self.tab2.T2rbGroup, searchBy)
        searchedWord = self.tab2.leSearch.text()

        self.ShowClients(usersChoice, searchedWord)

    def InitDatabase(self):
        """Inicjuje połączenie z bazą danych."""
        # polaczenie z baza
        self.db = Database()
        self.conn = self.db.CreateConnection("medikap")
        self.cur = self.db.CreateCursor(self.conn)
        if self.db.CreateTables(self.cur) == False:
            # Wyswietlanie pop-upa z błędem
            print("Nie udało się utworzyć tabel")

    def InitInvoice(self):
        """Tworzy obiekt klasy: InvoiceFV i przekazuje do niej zebrane z pól tekstowych dane."""

        # Zmienne pomocnicze - zebrane dane z pól tekstowych wypełnionych przez użytkownika
        companyName = self.tab3.leCompanyName.text()
        companyAdress1 = self.tab3.leCompanyAdress1.text()
        companyAdress2 = self.tab3.leCompanyAdress2.text()
        companyNIP = self.tab3.leCompanyNIP.text()
        researchDate = self.tab3.deDate.text()
        invoiceCreationDate = self.tab3.deInvoiceCreateDate.text()
        paymentMethod = str(self.tab3.comboPayment.currentText())
        operationResult = False

        try:
            # Jeżeli użytkownik wpisał własny numer faktury będzie on uwzględniony w wygenerowanym pliku .pdf
            # if self.OwnInvoiceNumber() == False:
            #     self.MessageBox("error",
            #                     "Błędny format numeru faktury. Poprawny format to np: 20/12/2019",
            #                     "", "BŁĄD")
            # else:
            OwnInvoiceNumber = self.OwnInvoiceNumber()

            # Otrzymuje listę ponumerowanych pozycji widocznych na fakturze w zależności od wyboru użytkownika
            invoicePositionsList = self.InvoicePosition()

            if invoicePositionsList != False:
                # Podliczenie kwoty do zapłaty za wszystkie wykonane usługi
                summarizedPayment = str(self.SummarizePayment(invoicePositionsList))

                # Instancja klasy InvoiceFV wraz ze zmiennymi pomocniczymi służącymi do wygenerowania dokumentu .pdf
                self.pdf = InvoiceFV(companyName, companyAdress1, companyAdress2, companyNIP, researchDate, paymentMethod, invoicePositionsList, OwnInvoiceNumber, summarizedPayment, invoiceCreationDate)

                # Wywołanie funkcji tworzącej plik .pdf na dysku twardym
                operationResult = self.pdf.PrintInvoice()

            else:
                operationResult = None

        except Exception as e:
            operationResult = e

            # Wyświetlenie stosownego komunikatu
        if operationResult == True:
            self.MessageBox("info", "Pomyślnie utworzono fakturę ", "", "UWAGA")

        elif operationResult == None:
            self.MessageBox("error", "Nie wybrano żadnej pozycji do wyświetlenia na fakturze! ", "", "BŁĄD")

        else:
            self.MessageBox("error","Coś poszło nie tak. Szczegóły znajdziesz poniżej. Zapisz treść błędu do dalszej diagnostyki.","","BŁĄD", str(operationResult))

    def InvoicePosition(self):
        """Zwraca listę ponumerowanych pozycji, które mają być wyświetlone finalnie na fakturze.
        """

        consultationPrice = self.tab3.leConsultationPrice.text()
        otherPrice = self.tab3.leOtherPrice.text()
        otherName = self.tab3.leOther.text()

        if consultationPrice == '':
            consultationPrice = '0'

        if otherPrice == '':
            otherPrice = '0'

        # Numery index CheckBoxów wybranych do wyświetlenia na fakturze
        selectedCheckBoxes = self.IsCheckBoxSelected(self.tab3.checkBoxesList)

        if selectedCheckBoxes == False:
            return False
        else:

            # Możliwe pozycje do wyświetlenia
            invoicePossiblePositions = [
                ["Badanie psychologiczne: kierowca", '', '1,00', '', '150', '150'],
                ["Dodatkowe orzeczenie", '', '1,00', '', '80', '80'],
                ["Konsultacja psychologiczna", '', '1,00', '', '{0}'.format(consultationPrice), '{0}'.format(consultationPrice)],
                ['{0}'.format(otherName), '', '1,00', '', '{0}'.format(otherPrice), '{0}'.format(otherPrice)],
            ]

            # Lista pomocnicza do której zostaną wpisane dane konkretnej pozycji z listy powyżej
            invoiceItems = []

            # Iterator zlicza liczbę pozycji na fakturze, a następnie wpisuje tę wartość do konkretnej pozycji faktury w pętli. Numeruje kolejne pozycje na fakturze
            iterator = 0
            for element in selectedCheckBoxes:
                iterator += 1
                invoicePossiblePositions[element].insert(0, str(iterator))
                invoiceItems.append(invoicePossiblePositions[element])

            # Zwrócona zostaje kompletna lista, której każdy element to odrębna pozycja na fakturze wraz z dodanym numerem pozycji
            print("Zwracam invoiceItems")
            return invoiceItems

    def IsCheckBoxSelected(self, checkBoxList):
        """Zwraca index zaznaczonego CheckBoxa. Jako argument przyjmuje listę CheckBoxów do sprawdzenia. Dla każdego elementu przesłanej listy sprawdza czy CheckBox jest zaznaczony.
        Zwraca listę indexów zaznaczonych CheckBoxów"""

        selectedCheckBoxesIndex = []

        for singleCheckBox in checkBoxList:
            if singleCheckBox.isChecked() == True:
                selectedCheckBoxesIndex.append(self.tab3.checkBoxesList.index(singleCheckBox))

        if not selectedCheckBoxesIndex:
            return False
        else:
            return selectedCheckBoxesIndex

    def SummarizePayment(self, paymentPositions):
        """Podlicza kwotę do zapłaty na podstawie pozycji widocznych na fakturze. Zwraca sumę kwot do zapłaty."""
        sum = 0
        for element in paymentPositions:
            sum += int(element[5])
        return sum

    def OwnInvoiceNumber(self):
        """Jeżeli użytkownik wpisał własny numer faktury, automatyczna numeracja zostanie pominięta, a wybrany numer wpisany do pliku .pdf.
        Jeżeli użytkownik zostawi pole puste, wówczas numer faktury zostanie wybrany wutomatycznie na podstawie pliku tekstowego: invoiceNumber.txt"""
        if len(self.tab3.leOwnInvoiceNumber.text()) <  9:
            return False
        else:
            return self.tab3.leOwnInvoiceNumber.text()

    def run(self):

        ######################################
        ### Wygląd i ustawienia początkowe ###
        ######################################

        app = QApplication(sys.argv)
        # Tworzy obiekt klasy Window
        self.window = Window()
        # Wyświetla przyciku do zmiany rozmiaru i zamykania okna
        self.window.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.window.InitWindow()
        # 200, 200 punkt w którym rysuje okno / 1200 x 700 rozmiar okna
        self.window.setGeometry(200, 200, 1200, 700)

        #Tworzy layout zakładki numer: 1
        self.tab1 = TabNewClient()
        self.tab1.CreateTab1Layout()
        self.window.gbT1Main.setLayout(self.tab1.T1LayMain)
        self.tab1.CreateForms()
        self.tab1.CreateRadioButtons()
        self.tab1.CreateButtons()
        self.tab1.CreateComment()

        # Tworzy layout zakładki numer: 2
        self.tab2 = TabSearch()
        self.tab2.CreateTable()
        self.tab2.CreateTab2Layout()
        self.window.gbT2Main.setLayout(self.tab2.T2LayMain)
        self.tab2.CreateSearch()
        self.tab2.CreateEditButtons()

        # InvoiceTab
        self.tab3 = TabInvoice()
        self.tab3.CreateTab3Layout()
        self.tab3.CreateInvoiceForms()
        self.tab3.CreateServicesCheckBox()
        self.tab3.CreateInvoiceButtons()
        self.window.gbT3Main.setLayout(self.tab3.T3LayMain)

        # Ustawia ikonę okna głównego i zakładek
        tab1Icon = './icon/new.png'
        tab2Icon = "./icon/clientlist.png"
        tab3Icon = "./icon/invoice.png"
        mainIcon = "./icon/main.png"

        self.window.setWindowIcon(QIcon(mainIcon))

        self.window.tab.setTabIcon(0, QIcon(tab1Icon))
        self.window.tab.setTabIcon(1, QIcon(tab2Icon))
        self.window.tab.setTabIcon(2, QIcon(tab3Icon))

        # Ustawia ikonę poszczególnych przycisków. Wykorzystywana jest funkcja pomocnicza.
        self.SetIcon(self.tab1.btnDodaj, "add")
        self.SetIcon(self.tab1.btnWyczysc, "clear")
        self.SetIcon(self.tab3.btnClearInvoiceForm, "clear")

        self.SetIcon(self.tab2.btnOnOffEdit, "lock")
        self.SetIcon(self.tab2.btnEdit, "ok")
        self.SetIcon(self.tab2.btnDelete, "delete")
        self.SetIcon(self.tab2.btnSearch, "search")
        self.SetIcon(self.tab3.btnCreateInvoice, "createInv")
        self.SetIcon(self.tab2.btnShowAll, "showClients")

        #Inicjalizuje polaczenie z baza danych
        self.InitDatabase()

        #########################
        ### Signals and Slots ###
        #########################

        # Dodawanie klienta
        self.tab1.btnDodaj.clicked.connect(self.AddUserToDB)
        # Czyszczenie pól formularza w zakładce: Dodaj
        self.tab1.btnWyczysc.clicked.connect(self.ClearT1Fields)
        # Wyświetlanie wszystkich klientów
        self.tab2.btnShowAll.clicked.connect(lambda: self.ShowClients(None))
        # Szukanie klientów według zadanych kryteriów
        self.tab2.btnSearch.clicked.connect(self.SearchClients)
        # Usuwanie z bazy zaznaczonego klienta
        self.tab2.btnDelete.clicked.connect(lambda: self.EditOrDelClient("del"))
        # Modyfikowanie danych osobowych zaznaczonego klienta
        self.tab2.btnEdit.clicked.connect(lambda: self.EditOrDelClient("edit"))
        # Włącza lub wyłącza możliwość edycji tabeli
        self.tab2.btnOnOffEdit.clicked.connect(self.EnableDisableTableEdit)
        # Przekazuje CheckBox, którego stan będzie przesyłany do metody SetEndDate po każdej jego zmianie
        self.tab1.cbUnder60Years.stateChanged.connect(lambda: self.tab1.SetEndDate(self.tab1.cbUnder60Years))
        # Utwórz fakture
        self.tab3.btnCreateInvoice.clicked.connect(self.InitInvoice)
        # Czyszczenie pól formularza w zakładce: Faktura
        self.tab3.btnClearInvoiceForm.clicked.connect(self.ClearT3Fields)


        app.exec_()

if __name__ == "__main__":
    Main().run()






