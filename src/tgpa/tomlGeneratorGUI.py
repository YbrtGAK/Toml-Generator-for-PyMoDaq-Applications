"""
Creator : Yann Berton
Date : 31/10/2024
Purpose : Automatically generate tolm files for keithley in pymodaq
"""

# Imports
# Libraries for the frontend (PyQt5, sys)
from PyQt5.QtWidgets import QCheckBox, QVBoxLayout, QWidget, QApplication, QPushButton, \
 QLabel, QGridLayout, QTabWidget, QFrame, QSpacerItem, QSizePolicy, QToolButton, QMainWindow, \
 QAction, QMenu, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QFileDialog
from PyQt5.QtGui import QPixmap
from pyqt_checkbox_list_widget.checkBoxListWidget import CheckBoxListWidget
from PyQt5.QtCore import Qt
import sys

# Libraries for the backend
from keithleyDataClass import Keithley2700
from utilities import getAFilesPath, getAFilesPathToSave  # Some usefull small functions for a best user's experience


# Classes definition
class KeithleyDialog(QDialog):
    """Dialog windows to configure Keithley parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keithley Settings")

        # Create a form layout
        self.layout = QFormLayout()

        # Create text fields for parameters (prefilled parameters for my application, change them if needed)
        self.title_field = QLineEdit(self)
        self.title_field.setText("\"Configuration entry for a Keithley 27XX Multimeter/Switch System\"")
        self.rsrc_name_example_field = QLineEdit(self)
        self.rsrc_name_example_field.setText("[\"ASRL1::INSTR\" \"TCPIP::192.168.01.01::1394::SOCKET\"]")
        self.rsrc_name_field = QLineEdit(self)
        self.rsrc_name_field.setText("ASRL7::INSTR")
        self.model_name_field = QLineEdit(self)
        self.model_name_field.setText("\"2701\"")
        self.panel_field = QLineEdit(self)
        self.panel_field.setText("\"rear\"")
        self.termination_character_field = QLineEdit(self)
        self.termination_character_field.setText("Keithley must be set to LF")

        # Add fields to the layout
        self.layout.addRow("Title:", self.title_field)
        self.layout.addRow("rsrc_name_example:", self.rsrc_name_example_field)
        self.layout.addRow("rsrc_name:", self.rsrc_name_field)
        self.layout.addRow("model_name:", self.model_name_field)
        self.layout.addRow("panel:", self.panel_field)
        self.layout.addRow("termination_character:", self.termination_character_field)

        # Add "OK" / "Cancel" buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        # Set layout
        self.setLayout(self.layout)

    def get_data(self):
        """Return parameters of configuration as dictionnaries"""

        return {
            'title': self.title_field.text(),
            'rsrc_name_example': self.rsrc_name_example_field.text(),
            'rsrc_name': self.rsrc_name_field.text(),
            'model_name': self.model_name_field.text(),
            'panel': self.panel_field.text(),
            'termination_character': self.termination_character_field.text()
        }


class SensorsDialog(QDialog):
    """Dialog window to input sensors' parameters"""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create tabs
        self.tabs = QTabWidget()
        
        # Create empty dictionaries for every sensor types
        # Frtd : PT100 sensors for thermocouples reference
        # Tc : Thermocouples
        # Volt : Any other sensor providing a voltage value as an indirect measure
        self.sensors = {"Frtd":{}, "Tc":{}, "Volt":{}}
        
        # Tabs settings
        self.tab_frtd = QWidget()
        self.tab_tc = QWidget()
        self.tab_volt = QWidget()
        
        # Setup tabs
        self.setup_tab(self.tab_frtd, "Frtd")
        self.setup_tab(self.tab_tc, "Tc")
        self.setup_tab(self.tab_volt, "Volt")
        
        # Add tabs to menu
        self.tabs.addTab(self.tab_frtd, "Frtd")
        self.tabs.addTab(self.tab_tc, "Tc")
        self.tabs.addTab(self.tab_volt, "Volt")
        
        # Add tabs to the main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        
    def setup_tab(self,tab,sensor_type:str):
        """Create and specify a form layout for sensors tabs"""

        self.layout = QFormLayout()  # Instanciate a form layout widget

        # Text fields for sensors' parameters
        match sensor_type:  # Design sensor parameters' tab according its type
            case "Frtd":  # for Frtd such as PT100 :
                self.sensors["Frtd"]["mode"] = QLineEdit(self)
                self.sensors["Frtd"]["mode"].setText("temp")
                self.sensors["Frtd"]["transducer"] = QLineEdit(self)
                self.sensors["Frtd"]["transducer"].setText("frtd")
                self.sensors["Frtd"]["type"] = QLineEdit(self)
                self.sensors["Frtd"]["type"].setText("pt100")
                self.sensors["Frtd"]["resolution"] = QLineEdit(self)
                self.sensors["Frtd"]["resolution"].setText("6")
                self.sensors["Frtd"]["nplc"] = QLineEdit(self)
                self.sensors["Frtd"]["nplc"].setText("5")
    
                # Add fields to the form
                self.layout.addRow("Mode:", self.sensors["Frtd"]["mode"])
                self.layout.addRow("Transducer:",self.sensors["Frtd"]["transducer"])
                self.layout.addRow("Type:", self.sensors["Frtd"]["type"])
                self.layout.addRow("Resolution:", self.sensors["Frtd"]["resolution"])
                self.layout.addRow("NPLC:", self.sensors["Frtd"]["nplc"])
                
            case "Tc":
                self.sensors["Tc"]["mode"] = QLineEdit(self)
                self.sensors["Tc"]["mode"].setText("temp")
                self.sensors["Tc"]["transducer"] = QLineEdit(self)
                self.sensors["Tc"]["transducer"].setText("tc")
                self.sensors["Tc"]["type"] = QLineEdit(self)
                self.sensors["Tc"]["type"].setText("K")
                self.sensors["Tc"]["ref_junc"] = QLineEdit(self)
                self.sensors["Tc"]["ref_junc"].setText("ext")
                self.sensors["Tc"]["resolution"] = QLineEdit(self)
                self.sensors["Tc"]["resolution"].setText("6")
                self.sensors["Tc"]["nplc"] = QLineEdit(self)
                self.sensors["Tc"]["nplc"].setText("5")
    
                # Add field to the form
                self.layout.addRow("Mode:", self.sensors["Tc"]["mode"])
                self.layout.addRow("Transducer:", self.sensors["Tc"]["transducer"])
                self.layout.addRow("Type:", self.sensors["Tc"]["type"])
                self.layout.addRow("Ref_junc:", self.sensors["Tc"]["ref_junc"])
                self.layout.addRow("Resolution:", self.sensors["Tc"]["resolution"])
                self.layout.addRow("NPLC:", self.sensors["Tc"]["nplc"])

            case "Volt":
                self.sensors["Volt"]["mode"] = QLineEdit(self)
                self.sensors["Volt"]["mode"].setText("Volt:dc")
    
                # Ajouter les champs au formulaire
                self.layout.addRow("Mode:", self.sensors["Volt"]["mode"])

        # Add OK and Cancel buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        tab.setLayout(self.layout)

    def get_data(self):
        """Get GUI's info in dictionaries"""
        
        for key_sensors in self.sensors :
            for key_sensor in self.sensors[key_sensors] : 
                self.sensors[key_sensors][key_sensor] = self.sensors[key_sensors][key_sensor].text()
        return self.sensors


class MainWindow(QMainWindow):

    """Main app - GUI layout """

    def __init__(self, keithleyChannelList):
        super().__init__()
        self.keithleyChannelList = keithleyChannelList
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Tolm File Generator for Keithley")

        # Create the main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        # Add a "+" button to add tabs
        self.add_tab_button = QToolButton(self)
        self.add_tab_button.setText("+")
        self.add_tab_button.clicked.connect(self.add_new_tab)

        # Set the button's location in the tabs
        self.tabs.setCornerWidget(self.add_tab_button, Qt.TopRightCorner)

        # Add the first tab corresponding to the first card of the Keithley
        self.tab1 = QWidget()
        self.setup_tab(self.tab1, self.keithleyChannelList)
        self.tabs.addTab(self.tab1, "Card n°1")

        # Add a button to save the lists
        self.button = QPushButton("Save the lists")
        self.button.clicked.connect(self.save_the_list)
        
        # Add a button to generate the toml
        self.button_generate = QPushButton("Generate the toml file")
        self.button_generate.clicked.connect(self.generate_toml)

        # Main layout - add tabs and buttons
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.button)
        layout.addWidget(self.button_generate)
        self.main_widget.setLayout(layout)

        # Add a menu
        self.create_menu()

    def setup_tab(self, tab, keithleyChannelList):
        """Config a tab to set Keithley's channel to the rights sensors"""

        # Design checkboxes
        checkboxesFont = self.font()
        checkboxesFont.setBold(True)
        checkboxesFont.setItalic(True)
        checkboxesFont.setPointSize(9)

        # Design layout
        layout = QGridLayout()
        
        # Card information - prefilled information for my application, editable
        card_nb = str(self.tabs.count() + 1)
        if self.tabs.count() + 1 < 10 : 
            card_nb = ''.join(('0',card_nb))
        tab.card_name_label = QLabel("Card name (e.g : MODULE01)")
        tab.card_name = QLineEdit(self)
        tab.number_label = QLabel("Card number (e.g : 7706)")
        tab.number = QLineEdit(self)
        if self.tabs.count() + 1 == 1 : 
            tab.number.setText("7706")
        if self.tabs.count() + 1 == 2 : 
            tab.number.setText("7702")
        tab.card_name.setText("MODULE" + card_nb)
        if card_nb == '1':
            tab.number.setText("7706")
        elif card_nb == '2':
            tab.number.setText("7702")
        tab.info_label = QLabel("Info")
        tab.info = QLineEdit(self)
        if self.tabs.count() + 1 >= 5 :
            tab.lab_pic = QLabel(self)
            tab.logo = QPixmap("logo.png")
            tab.lab_pic.setPixmap(tab.logo)
            tab.lab_pic.resize(tab.logo.width(), tab.logo.height())


        # Add widget to the layout
        layout.addWidget(tab.number_label, 0,0)    
        layout.addWidget(tab.number, 0,1)
        if self.tabs.count() + 1 >= 5:
            layout.addWidget(tab.lab_pic, 0,2,2,1, alignment=Qt.AlignCenter)
        layout.addWidget(tab.card_name_label, 1,0)
        layout.addWidget(tab.card_name,1,1)
        layout.addWidget(tab.info_label, 2,0)
        layout.addWidget(tab.info,2,1)

        # FRTD checkbox design
        title_Frtd = QLabel("FRTD")
        title_Frtd.setAlignment(Qt.AlignCenter)
        title_Frtd.setFont(checkboxesFont)
        allCheckBoxFrtd = QCheckBox('Check all')
        checkBoxListWidget_Frtd = CheckBoxListWidget()
        checkBoxListWidget_Frtd.addItems(keithleyChannelList)
        allCheckBoxFrtd.stateChanged.connect(checkBoxListWidget_Frtd.toggleState)

        # Add widgets to the layout
        layout.addWidget(title_Frtd, 3, 0)
        layout.addWidget(allCheckBoxFrtd, 4, 0)
        layout.addWidget(checkBoxListWidget_Frtd, 5, 0)

        # TC checkbox design
        title_Tc = QLabel("Tc")
        title_Tc.setAlignment(Qt.AlignCenter)
        title_Tc.setFont(checkboxesFont)
        allCheckBoxTc = QCheckBox('Check all')
        checkBoxListWidget_Tc = CheckBoxListWidget()
        checkBoxListWidget_Tc.addItems(keithleyChannelList)
        allCheckBoxTc.stateChanged.connect(checkBoxListWidget_Tc.toggleState)

        # Add widgets to the layout
        layout.addWidget(title_Tc, 3, 1)
        layout.addWidget(allCheckBoxTc, 4, 1)
        layout.addWidget(checkBoxListWidget_Tc, 5, 1)

        # Voltage checkbox design
        title_Volt = QLabel("Volt")
        title_Volt.setAlignment(Qt.AlignCenter)
        title_Volt.setFont(checkboxesFont)
        allCheckBoxVolt = QCheckBox('Check all')
        checkBoxListWidget_Volt = CheckBoxListWidget()
        checkBoxListWidget_Volt.addItems(keithleyChannelList)
        allCheckBoxVolt.stateChanged.connect(checkBoxListWidget_Volt.toggleState)

        # Add widgets to the layout
        layout.addWidget(title_Volt, 3, 2)
        layout.addWidget(allCheckBoxVolt, 4, 2)
        layout.addWidget(checkBoxListWidget_Volt, 5, 2)

        # Set the tabs layout
        tab.setLayout(layout)

    def create_menu(self):
        """Create a menu bar with a tab 'Keithley'"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
             font-size: 14px;
             padding: 4px; 
         """) 
        keithley_menu = menubar.addMenu('&Keithley')

        # Action to open the configuration window
        keithley_settings_action = QAction('Keithley Settings', self)
        keithley_settings_action.triggered.connect(self.open_keithley_dialog)
        
        sensors_settings_action = QAction('Sensors Settings', self)
        sensors_settings_action.triggered.connect(self.open_sensors_dialog)
    
        # Style sheet for the tab "Keithley"
        keithley_menu.setStyleSheet("""
            QMenu {
                font-size: 12px;  /* Réduire la taille de la police de l'onglet */
            }
        """)
    
        keithley_menu.addAction(keithley_settings_action)
        keithley_menu.addAction(sensors_settings_action)

    def open_keithley_dialog(self):
        """Open window dialog to enter the parameters"""
        keithley_dialog = KeithleyDialog(self)
        if keithley_dialog.exec_() == QDialog.Accepted:
            # Récupérer les données de la boîte de dialogue
            self.keithley_settings = keithley_dialog.get_data()
            
    def open_sensors_dialog(self):
        """Open window dialog to enter the parameters"""
        sensors_dialog = SensorsDialog(self)
        if sensors_dialog.exec_() == QDialog.Accepted:
            # Récupérer les données de la boîte de dialogue
            self.sensors_settings = sensors_dialog.get_data()

    def add_new_tab(self):
        """Add a new tab"""
        # Count the number of tabs
        tab_count = self.tabs.count() + 1

        # Create a new tab widget
        new_tab = QWidget()

        # Add the label
        cardChannelList = [str(tab_count*100 + e) for e in range(1,41)]
        self.setup_tab(new_tab, cardChannelList)
        self.tabs.addTab(new_tab, f"Card n°{tab_count}")

    def close_tab(self, index):
        """Deleter the tab"""
        self.tabs.removeTab(index)

    def save_the_list(self):
        """Save checked items in each tab's lists"""
        
        # Initialization of the dictionary
        self.data_settings = {"Card n°" + str(i + 1) : {"Frtd":[],"Tc":[],"Volt":[]} for i in range(self.tabs.count())}

        # Loop over the tabs - hence the different cards
        self.nb_cards = (self.tabs.count())
        for tab_index in range(self.tabs.count()):
            tab = self.tabs.widget(tab_index)
            layout = tab.layout()
            self.data_settings["Card n°" + str(tab_index + 1)]["settings"] = {"name" : tab.card_name.text(),
                                                                              "number" : tab.number.text(),
                                                                              "info" : tab.info.text()}
            # Loop over each tab widget
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                # Action if the widget is a checkBoxList
                if isinstance(widget, CheckBoxListWidget):
                    # Loop over each checkable item in the box
                    for j in range(widget.count()):
                        item = widget.item(j)
                        # If the item is checked, append it to the right list in the dictionary
                        if item.checkState() == Qt.Checked:
                            if layout.itemAt(i-2).widget().text() == "FRTD":
                                self.data_settings["Card n°" + str(tab_index + 1)]["Frtd"].append(item.text())
                            elif layout.itemAt(i-2).widget().text() == "Tc":
                                self.data_settings["Card n°" + str(tab_index + 1)]["Tc"].append(item.text())
                            elif layout.itemAt(i-2).widget().text() == "Volt":
                                self.data_settings["Card n°" + str(tab_index + 1)]["Volt"].append(item.text())
                                
        # Check if user input allow a working toml config toml file
        # If some thermocouples are registered, check if a FRTD is registered too
        for card in self.data_settings:
            if len(self.data_settings[card]["Tc"])>0 and len(self.data_settings[card]["Frtd"])==0 :
                print(card + " : Des thermocouples sont renseignés sans Frtd")
                
        # Check if theres no sensors attributed to a same channel
            LFrtd = self.data_settings[card]["Frtd"]
            LTc = self.data_settings[card]["Tc"]
            LVolt = self.data_settings[card]["Volt"]
            
            for e in LFrtd :
                if e in LTc:
                    print(card + " : Le canal "
                          + e + " est assigné à un frtd et à au moins un thermocouple.")
                if e in LVolt:
                    print(card + " : Le canal "
                          + e + " est assigné à un frtd et à au moins un autre capteur.")
            for e in LTc:
                if e in LVolt:
                    print(card + " : Le canal "
                          + e + " est assigné à un thermocouple et à au moins à un autre capteur.")
                
        print('Lists successfully saved :)')
        
    def generate_toml(self):
        """Generate the toml file"""
        
        # Try / except combination to allow the user to use standard Keithlkey info
        try : 
            self.INSTRUMENT01 = Keithley2700(name = "INSTRUMENT01",
                                             title = self.keithley_settings['title'],
                                             rsrc_name_example = self.keithley_settings["rsrc_name_example"],
                                             rsrc_name = self.keithley_settings["rsrc_name"],
                                             model_name=self.keithley_settings["model_name"],
                                             panel=self.keithley_settings["panel"],
                                             termination_character=self.keithley_settings["termination_character"],
                                             sensors_settings=self.sensors_settings)
        except AttributeError:
            self.INSTRUMENT01 = Keithley2700(
                name="INSTRUMENT01",
                title="Instrument in wich is plugged the switching module used for data acquisition",
                rsrc_name_example=["ASRL1::INSTR", "TCPIP::192.168.01.01::1394::SOCKET"],
                rsrc_name="ASRL7::INSTR",
                model_name="2701",
                panel="rear",
                termination_character="Keithley must be set to LF",
                sensors_settings = {'Frtd': {'mode': 'temp',
                                             'transducer': 'frtd',
                                             'type': 'pt100',
                                             'resolution': '6',
                                             'nplc': '5'},
                                    'Tc': {'mode': 'temp',
                                           'transducer': 'tc',
                                           'type': 'K',
                                           'ref_junc': 'ext',
                                           'resolution': '6',
                                           'nplc': '5'},
                                    'Volt': {'mode': 'Volt:dc'}})

        # Add every card registered by the user in the object instrument
        for i in range(0,self.nb_cards):
            self.INSTRUMENT01.add_module(name=self.data_settings["Card n°" + str(i + 1)]["settings"]["name"],
                                         number=self.data_settings["Card n°" + str(i + 1)]["settings"]["number"],
                                         info=self.data_settings["Card n°" + str(i + 1)]["settings"]["info"])
            # For each card, get the sensors info
            for channel in self.data_settings["Card n°" + str(i + 1)]["Frtd"] : 
                self.INSTRUMENT01.modules[-1].config_channel(nb_channel=channel, sensor="frtd")
            
            for channel in self.data_settings["Card n°" + str(i + 1)]["Tc"] : 
                self.INSTRUMENT01.modules[-1].config_channel(nb_channel=channel, sensor="tc")
                
            for channel in self.data_settings["Card n°" + str(i + 1)]["Volt"] : 
                self.INSTRUMENT01.modules[-1].config_channel(nb_channel=channel, sensor="Volt")
                
        # Write the toml file
        self.INSTRUMENT01.write_tolm(getAFilesPathToSave())
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow(keithleyChannelList=[str(e) for e in range(101, 141)])
    main_window.show()
    app.exec_()
