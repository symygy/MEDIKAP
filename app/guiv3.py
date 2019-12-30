from PyQt5.QtWidgets import QApplication, QDialog, QTabWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFormLayout, QLineEdit, QDateEdit, QTextEdit, QRadioButton, \
    QGridLayout, QButtonGroup, QTableWidget, QHeaderView, QAbstractItemView, QSizePolicy, QCheckBox, QComboBox
from PyQt5.QtGui import QIcon
import sys
import datetime


class Window(QDialog):
    def __init__(self):
        super().__init__()

    def InitWindow(self):
        # create tab widget
        self.tab = QTabWidget()

        # create MainWindow groupbox
        self.gbMainWindow = QGroupBox()

        # TAB groupBoxes
        self.gbT1Main = QGroupBox()
        self.gbT2Main = QGroupBox()
        self.gbT3Main = QGroupBox()

        # Adding tabs
        self.tab.addTab(self.gbT1Main, "Dodaj klienta")
        self.tab.addTab(self.gbT2Main, "Lista klientów")
        self.tab.addTab(self.gbT3Main, "Faktura")

        # Setting MainWindow title
        self.setWindowTitle("MEDIKAP - gabinet medycyny pracy")

        # Main Window Layout
        self.layMainWindow = QHBoxLayout()

        # Set MainWindow Layout
        self.layMainWindow.addWidget(self.tab)
        self.gbMainWindow.setLayout(self.layMainWindow)

        # set MainWindow layout visible
        self.setLayout(self.layMainWindow)

        #show window
        self.show()

class TabNewClient:
    def __init__(self):
        pass

    def CreateTab1Layout(self):
        self.gbAddClient = QGroupBox("Dane klienta")
        self.gbRodzajBadania = QGroupBox("Podstawa prawna")


        self.gbDane = QGroupBox()
        self.gbComment = QGroupBox("Komentarz")
        self.gbButtons = QGroupBox()

        # TAB1 - layouts
        self.T1LayMain = QVBoxLayout()
        layDane = QHBoxLayout()

        # TAB1
        # Drugi parametr określa procent okna jaki będzie zajmował widget - GroupBox
        layDane.addWidget(self.gbAddClient, 66)
        layDane.addWidget(self.gbRodzajBadania, 33)
        self.gbDane.setLayout(layDane)


        # TAB1 - set layout to Main
        self.T1LayMain.addWidget(self.gbDane, 50)
        self.T1LayMain.addWidget(self.gbComment,50)
        self.T1LayMain.addWidget(self.gbButtons)

    def CreateForms(self):
        # layout

        layForms = QFormLayout()
        #Sprawdzic czemu nie dziala
        #layForms.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # line edits
        self.leName = QLineEdit()
        self.leSurname = QLineEdit()
        self.lePhone = QLineEdit()
        self.leMail = QLineEdit()
        self.leRejestr = QLineEdit()
        self.deDate = QDateEdit()
        self.deEndDate = QDateEdit()

        # CheckBox
        self.cbUnder60Years = QCheckBox("Badany ukończył 60 rok życia")

        # minimum dates
        self.deDate.setDate(datetime.date.today())
        self.SetEndDate(self.cbUnder60Years)

        # Form fields
        layForms.addRow("Imię: ", self.leName)
        layForms.addRow("Nazwisko: ", self.leSurname)
        layForms.addRow("Telefon: ", self.lePhone)
        layForms.addRow("E-mail: ", self.leMail)
        layForms.addRow("Nr w rejestrze: ", self.leRejestr)
        layForms.addRow("Data badania: ", self.deDate)
        layForms.addRow("Data upływu badania: ", self.deEndDate)
        layForms.addRow("", self.cbUnder60Years)
        self.gbAddClient.setLayout(layForms)

    def CreateRadioButtons(self):
        # layout
        layRadioButtons = QVBoxLayout()

        # RadioButtons
        rbKierZaw = QRadioButton("kierowca zawodowy")
        rbKierUprz = QRadioButton("kierowca uprzywilejowany")
        rbInstrEgz = QRadioButton("instruktor / egzaminator")
        rbZatrzPraJazd = QRadioButton("zatrzymane prawo jazdy")
        rbInne = QRadioButton("inna: ")
        rbInne.setChecked(True)

        # RadioButtons Group - potrzebne do sprawdzenia, który RB jest zaznaczony
        self.T1rbGroup = QButtonGroup()
        self.T1rbGroup.addButton(rbKierZaw, 0)
        self.T1rbGroup.addButton(rbKierUprz, 1)
        self.T1rbGroup.addButton(rbInstrEgz, 2)
        self.T1rbGroup.addButton(rbZatrzPraJazd, 3)
        self.T1rbGroup.addButton(rbInne, 4)

        # LineEdit
        self.leInne = QLineEdit()

        # Adding Widgets to layout
        layRadioButtons.addWidget(rbKierZaw)
        layRadioButtons.addWidget(rbKierUprz)
        layRadioButtons.addWidget(rbInstrEgz)
        layRadioButtons.addWidget(rbZatrzPraJazd)
        layRadioButtons.addWidget(rbInne)
        layRadioButtons.addWidget(self.leInne)

        # Adding layout to GroupBox
        self.gbRodzajBadania.setLayout(layRadioButtons)

    def CreateButtons(self):
        # layout
        layButtons = QHBoxLayout()

        self.btnDodaj = QPushButton("dodaj")
        self.btnWyczysc = QPushButton("wyczyść formularz")

        layButtons.addWidget(self.btnDodaj)
        layButtons.addWidget(self.btnWyczysc)

        self.gbButtons.setLayout(layButtons)

    def CreateComment(self):
        # layout
        layComment = QHBoxLayout()
        self.teCommentField = QTextEdit()
        layComment.addWidget(self.teCommentField)
        self.gbComment.setLayout(layComment)


    def SetEndDate(self, cbState):
        """Przelicza datę upływu badania w zależności od podanej daty badania.
        Jeżeli został zaznaczony CheckBox 'Badany ukończył 60 rok życia' do daty badanie dodane zostanie ~2.5 roku,
        jeżeli nie dodane zostanie 5 lat.
        """
        date = self.deDate.text()
        convertedDate = datetime.datetime.strptime(date, '%d.%m.%Y')
        if cbState.isChecked() == True:
            newDate = self.deEndDate.setDate(convertedDate + datetime.timedelta(days = 912))
        else:
            newDate = self.deEndDate.setDate(convertedDate + datetime.timedelta(days = 1827))

class TabSearch:
    def __init__(self):
        pass

    def CreateTab2Layout(self):
        self.gbTable = QGroupBox("Lista klientów")
        self.gbSearch = QGroupBox("Szukaj")
        self.gbEdit = QGroupBox("Modyfikowanie wpisów")

        self.T2LayMain = QHBoxLayout()
        self.layTable = QVBoxLayout()
        self.laySearch = QGridLayout()
        self.layEdit = QHBoxLayout()

        self.gbSearch.setLayout(self.laySearch)
        self.gbTable.setLayout(self.layTable)
        self.gbEdit.setLayout(self.layEdit)

        self.layTable.addWidget(self.tabwidTable)
        self.layTable.addWidget(self.btnShowAll)
        self.layTable.addWidget(self.gbEdit)

        self.T2LayMain.addWidget(self.gbTable, 80)
        self.T2LayMain.addWidget(self.gbSearch, 20)

    def CreateTable(self):
        self.tabwidTable = QTableWidget()
        self.tabwidTable.setEditTriggers(QAbstractItemView.NoEditTriggers)


        # Nazwy kolumn tabeli
        columnNames = ["ID", "nazwisko:", "imię:", "nr telefonu:", "e-mail:", "nr w rejestrze:", "data badania:",
                       "data upływu badania:", "komentarz:", "podstawa prawna:"]

        # Ustawia ilość kolumn i ich nazwy
        self.tabwidTable.setColumnCount(10)
        self.tabwidTable.setHorizontalHeaderLabels(columnNames)

        # Ustawia dopasowanie szerokości kolumny do zawartości
        header = self.tabwidTable.horizontalHeader()
        for i in range(0,10):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        # Przycisk
        self.btnShowAll = QPushButton("wyświetl wszystkich klientów")

        #Ukrycie kolumny zawierającej ID klienta
        self.tabwidTable.setColumnHidden(0, True)

    def CreateSearch(self):
        self.leSearch = QLineEdit()
        self.leSearch.setToolTip("Wpisz słowo którego szukasz")
        self.btnSearch = QPushButton("szukaj")

        rbEverywhere = QRadioButton("wszędzie")
        rbEverywhere.setChecked(True)
        rbName = QRadioButton("imię")
        rbSurName = QRadioButton("nazwisko")
        rbPhone = QRadioButton("telefon")
        rbEmail = QRadioButton("e-mail")
        rbRejestr = QRadioButton("numer w rejestrze")
        rbDate = QRadioButton("data badania")
        rbEndDate = QRadioButton("data upływu badania")
        rbPodsPrawna = QRadioButton("podstawa prawna")

        self.T2rbGroup = QButtonGroup()
        self.T2rbGroup.addButton(rbEverywhere, 5)
        self.T2rbGroup.addButton(rbName, 6)
        self.T2rbGroup.addButton(rbSurName, 7)
        self.T2rbGroup.addButton(rbPhone, 8)
        self.T2rbGroup.addButton(rbEmail, 9)
        self.T2rbGroup.addButton(rbRejestr, 10)
        self.T2rbGroup.addButton(rbDate, 11)
        self.T2rbGroup.addButton(rbEndDate, 12)
        self.T2rbGroup.addButton(rbPodsPrawna, 13)

        self.laySearch.addWidget(rbEverywhere)
        self.laySearch.addWidget(rbName)
        self.laySearch.addWidget(rbSurName)
        self.laySearch.addWidget(rbRejestr)
        self.laySearch.addWidget(rbPhone)
        self.laySearch.addWidget(rbEmail)
        self.laySearch.addWidget(rbRejestr)
        self.laySearch.addWidget(rbDate)
        self.laySearch.addWidget(rbEndDate)
        self.laySearch.addWidget(rbPodsPrawna)
        self.laySearch.addWidget(self.leSearch)
        self.laySearch.addWidget(self.btnSearch)

    def CreateEditButtons(self):

        self.btnDelete = QPushButton("usuń")

        self.btnEdit = QPushButton("zatwierdź zmiany")

        self.btnOnOffEdit = QPushButton("odblokuj edytowanie")

        #self.btnCreateInvoice = QPushButton("Faktura")

        self.layEdit.addWidget(self.btnEdit)
        self.layEdit.addWidget(self.btnOnOffEdit)
        self.layEdit.addWidget(self.btnDelete)
        #self.layEdit.addWidget(self.btnCreateInvoice)

class TabInvoice:
    def __init__(self):
        pass

    def CreateTab3Layout(self):
        self.gbInvoiceData = QGroupBox("Dane do faktury")
        self.gbInvoiceButtons = QGroupBox()
        self.gbInvoiceService = QGroupBox("Wykonane usługi")

        self.T3LayMain = QVBoxLayout()
        self.T3LayMain.addWidget(self.gbInvoiceData, 45)
        self.T3LayMain.addWidget(self.gbInvoiceService, 45)
        self.T3LayMain.addWidget(self.gbInvoiceButtons, 10)

    def CreateInvoiceForms(self):
        # Layout
        layInvoiceForms = QFormLayout()

        # Text Fields
        self.leCompanyName = QLineEdit()
        self.leCompanyAdress1 = QLineEdit()
        self.leCompanyAdress2 = QLineEdit()
        self.leCompanyNIP = QLineEdit()
        self.deDate = QDateEdit()
        self.deInvoiceCreateDate = QDateEdit()
        self.leOwnInvoiceNumber = QLineEdit()

        # CheckBox
        self.cbOwnInvoiceNumber = QCheckBox("Własny numer faktury:")


        # ComboBox
        self.comboPayment = QComboBox()
        self.comboPayment.addItem("gotówka")
        self.comboPayment.addItem("przelew")

        # minimum dates
        self.deDate.setDate(datetime.date.today())
        self.deInvoiceCreateDate.setDate(datetime.date.today())

        # Form fields
        layInvoiceForms.addRow("Nazwa firmy: ", self.leCompanyName)
        layInvoiceForms.addRow("Ulica, numer budynku: ", self.leCompanyAdress1)
        layInvoiceForms.addRow("Kod pocztowy, miasto: ", self.leCompanyAdress2)
        layInvoiceForms.addRow("NIP: ", self.leCompanyNIP)
        layInvoiceForms.addRow("Data badania: ", self.deDate)
        layInvoiceForms.addRow("Data wystawienia faktury: ", self.deInvoiceCreateDate)
        layInvoiceForms.addRow("Forma płatności:", self.comboPayment)
        layInvoiceForms.addRow("Własny numer faktury:", self.leOwnInvoiceNumber)
        #layInvoiceForms.addRow("", self.cbOwnInvoiceNumber)
        #layInvoiceForms.addRow("Termin płatności: ", self.dePayDate)

        self.gbInvoiceData.setLayout(layInvoiceForms)



    def CreateServicesCheckBox(self):
        # Layout
        layInvoiceServices = QGridLayout()

        # CheckBoxes
        self.cbDriver150 = QCheckBox("Badanie psychologiczne: kierowca 150 zł")
        self.cbAddJudgment = QCheckBox("Dodatkowe orzeczenie 80 zł")
        self.cbConsultation = QCheckBox("Konsultacja psychologiczna ")
        self.cbOther = QCheckBox("Inna usługa: ")

        self.checkBoxesList = [self.cbDriver150, self.cbAddJudgment, self.cbConsultation, self.cbOther]

        # LineEdits
        self.leConsultation = QLineEdit()
        self.leConsultationPrice = QLineEdit()
        self.leOther = QLineEdit()
        self.leOtherPrice = QLineEdit()

        # Tooltips
        self.leOther.setToolTip("Wpisz nazwę")
        self.leOtherPrice.setToolTip("Wpisz kwotę")
        self.leConsultationPrice.setToolTip("Wpisz kwotę")
        self.leOwnInvoiceNumber.setToolTip("Przykład: 9/09/2019. Zostaw puste jeśli numer ma być utworzony automatycznie")

        layInvoiceServices.addWidget(self.cbDriver150, 0, 0)
        layInvoiceServices.addWidget(self.cbAddJudgment, 2, 0)
        layInvoiceServices.addWidget(self.cbConsultation, 3, 0)
        layInvoiceServices.addWidget(self.leConsultationPrice, 3, 1)
        layInvoiceServices.addWidget(self.cbOther, 4, 0)
        layInvoiceServices.addWidget(self.leOther, 4, 1)
        layInvoiceServices.addWidget(self.leOtherPrice, 4, 2)

        self.gbInvoiceService.setLayout(layInvoiceServices)

    def CreateInvoiceButtons(self):
        layInvoiceButtons = QHBoxLayout()
        self.btnCreateInvoice = QPushButton("utwórz fakturę")
        self.btnClearInvoiceForm = QPushButton("wyczyść formularz")

        layInvoiceButtons.addWidget(self.btnCreateInvoice)
        layInvoiceButtons.addWidget(self.btnClearInvoiceForm)

        self.gbInvoiceButtons.setLayout(layInvoiceButtons)





