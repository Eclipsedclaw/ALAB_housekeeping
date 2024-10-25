# Author: Jiancheng Zeng(JC)
# Date: May 5th, 2024

from PyQt5.QtCore import QDateTime, Qt, QTimer, QMutex
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtGui import QColor
import ALABHK_query
import threading
import time
import RPi.GPIO as GPIO
import serial
from serial.tools import list_ports

# search serial port
ser = serial.Serial()
devices = [info.device for info in list_ports.comports()]
print('available port: ')
print(devices)


class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)
        
        try:
            # GPIO setting
            GPIO.setmode(GPIO.BCM)
            V1 = 'closed'
            V2 = 'closed'
            V1Channel = 2
            V2Channel = 2
            GPIO.setup(V1Channel,GPIO.OUT)
            GPIO.setup(V2Channel,GPIO.OUT)
        except:
            print("Current device not compatiable with RPi.GPIO module!")

        # Heater setting
        GPIO_pin = 23



        # Set the geometry of the main window
        self.setGeometry(100, 100, 650, 400)  # (x, y, width, height)

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        # link to grafana viewer
        grafanaText = QLabel("<a href='http://aramakilab.neu.edu:3000/d/f12ea01c-2b65-43c9-bd97-90bd0ddd0dfb/aramaki-lab-housekeeping?orgId=1&refresh=5s'>click here for Grafana Monitor</a>")
        grafanaText.setTextFormat(Qt.RichText)
        grafanaText.setOpenExternalLinks(True)

        # Check stlye
        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        # lock changes to prevent missclicking
        disableWidgetsCheckBox = QCheckBox("&Lock changes")

        # define global table for data query
        self.compressorWidget = QTableWidget(4, 1)
        self.rtdWidget = QTableWidget(10, 1)
        self.pressureWidget = QTableWidget(2, 1)

        # For multithreading
        self.mutex = QMutex()  # Define a QMutex object

        # direct to each small layout group definetion 
        self.createControlGroupBox()
        self.createDataTabWidget()

        styleComboBox.activated[str].connect(self.changeStyle)
        disableWidgetsCheckBox.toggled.connect(self.ControlGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.DataTabWidget.setDisabled)

        # The topLayout is added to this grid layout starting at row 0, column 0, and spanning 1 row and 2 columns 
        topLayout = QHBoxLayout()
        topLayout.addWidget(grafanaText)
        topLayout.addStretch(1)
        topLayout.addWidget(disableWidgetsCheckBox, alignment=Qt.AlignRight)
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.ControlGroupBox, 1, 1)
        mainLayout.addWidget(self.DataTabWidget, 1, 0)

        # Set row stretch factors to make the entire layout longer vertically
        mainLayout.setRowStretch(0, 3)

        mainLayout.setColumnStretch(0, 2)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        # GUI title
        self.setWindowTitle("ALAB Housekeeping")
        # GUI theme options: Not sure what are all the options
        # TODO: figure out what are the rest of the style themes
        self.changeStyle('qt5ct-style')

    # GUI theme options, 
    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    # process bar, not used in current HK
    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)

    # Control turn on compressor pop up page
    def turnONCompressor(self):
        dialog = CompressorControlONDialog(self)
        dialog.exec()

    # Control turn off compressor pop up page
    def turnOFFCompressor(self):
        dialog = CompressorControlOFFDialog(self)
        dialog.exec()
    
    # Control turn on heaters pop up page
    def turnONHeater(self):
        dialog = HeaterControlONDialog(self)
        dialog.exec()

    # Control turn off heaters pop up page
    def turnOFFHeater(self):
        dialog = HeaterControlOFFDialog(self)
        dialog.exec()

    # Control stop run pop up page
    def stopandquit(self):
        dialog = StopandquitDialog(self)
        dialog.exec()

    # Layout for control
    def createControlGroupBox(self):
        self.ControlGroupBox = QGroupBox("Control")

        # Start button
        HKONButton = QPushButton("START HOUSEKEEPING SYSTEM")
        HKONButton.setDefault(False)
        HKONButton.setMaximumWidth(250)  # Set maximum width
        HKONButton.clicked.connect(self.pumpDataIntoTables)  # Connect to function for HK start running
        HKONButton.setStyleSheet("background-color: lightgreen")  # Set button color to light green

        # Stop and quit button
        HKOFFButton = QPushButton("STOP HOUSEKEEPING SYSTEM")
        HKOFFButton.setDefault(False)
        HKOFFButton.setMaximumWidth(250)  # Set maximum width
        HKOFFButton.clicked.connect(self.stopandquit)  # Connect to function for stop HK and quit

        # Refresh button, not implemented yet
        # TODO: update the refresh button and show time before last data update for each sheet
        refrashButton = QPushButton("Refresh current system status")
        refrashButton.setDefault(True)
        refrashButton.setMaximumWidth(250)  # Set maximum width

        # Control Heater text
        HeaterText = QLabel("Control Heater")
        HeaterText.setTextFormat(Qt.RichText)
        HeaterText.setOpenExternalLinks(True)

        # Layout for heaters TURN ON and TURN OFF buttons
        heaterButtonLayout = QHBoxLayout()  
        heaterONButton = QPushButton("TURN ON")
        heaterONButton.setDefault(True)
        heaterONButton.setMaximumWidth(100)  # Set maximum width
        heaterONButton.clicked.connect(self.turnONHeater)  # Connect to function for turning ON heaters
        heaterOFFButton = QPushButton("TURN OFF")
        heaterOFFButton.setDefault(True)
        heaterOFFButton.setMaximumWidth(100)  # Set maximum width
        heaterOFFButton.clicked.connect(self.turnOFFHeater)  # Connect to function for turning OFF heaters

        heaterButtonLayout.addWidget(heaterONButton)  # heater TURN ON button
        heaterButtonLayout.addWidget(heaterOFFButton)  # heater TURN OFF button

        # control compressor text
        CompressorText = QLabel("Control Compressor")
        CompressorText.setTextFormat(Qt.RichText)
        CompressorText.setOpenExternalLinks(True)

        # Layout for compressor TURN ON and TURN OFF buttons
        compressorButtonLayout = QHBoxLayout()
        compressorONButton = QPushButton("TURN ON")
        compressorONButton.setDefault(True)
        compressorONButton.setMaximumWidth(100)  # Set maximum width
        compressorONButton.clicked.connect(self.turnONCompressor)  # Connect to function for turning ON compressor
        compressorOFFButton = QPushButton("TURN OFF")
        compressorOFFButton.setDefault(True)
        compressorOFFButton.setMaximumWidth(100)  # Set maximum width
        compressorOFFButton.clicked.connect(self.turnOFFCompressor)  # Connect to function for turning OFF compressor

        compressorButtonLayout.addWidget(compressorONButton)  # compressor TURN ON button
        compressorButtonLayout.addWidget(compressorOFFButton)  # compressor TURN OFF button

        # Layout all the buttons and texts
        layout = QVBoxLayout()
        layout.addWidget(HKONButton, alignment=Qt.AlignLeft)  # Align left horizontally
        layout.addWidget(HKOFFButton, alignment=Qt.AlignLeft)  # Align left horizontally
        layout.addWidget(refrashButton, alignment=Qt.AlignLeft)  # Align left horizontally
        layout.addWidget(HeaterText, alignment=Qt.AlignLeft)  # Align left horizontally
        layout.addLayout(heaterButtonLayout)  # Add TURN ON and TURN OFF buttons side by side
        layout.addWidget(CompressorText, alignment=Qt.AlignLeft)
        layout.addLayout(compressorButtonLayout)  # Add TURN ON and TURN OFF buttons side by side
        layout.addStretch(1)
        self.ControlGroupBox.setLayout(layout)



    # Layout for data
    def createDataTabWidget(self):
        self.DataTabWidget = QTabWidget()
        self.DataTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)
        
        # Layout for compressor's sheet
        compressorTab = QWidget()
        self.compressorWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Customize row headers
        row_headers_rtd = ["Helium discharge", "Water outlet", "Water inlet", "Return Preesure/PSIG"]
        for i, text in enumerate(row_headers_rtd):
            item = QTableWidgetItem(text)
            self.compressorWidget.setVerticalHeaderItem(i, item)
        self.compressorWidget.setHorizontalHeaderItem(0, QTableWidgetItem("temperature/C"))
        self.compressorWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # Create a QHBoxLayout for the right side
        rightLayout_compressor = QHBoxLayout()
        rightLayout_compressor.addWidget(self.compressorWidget)
        # Create a main QHBoxLayout to hold the right layout
        rightLmainLayout_compressor = QHBoxLayout()
        rightLmainLayout_compressor.addLayout(rightLayout_compressor)
        compressorTab.setLayout(rightLmainLayout_compressor)
        
        # Layout for rtd's sheet
        rtdTab = QWidget()
        # Create the chart widget for the right side
        self.rtdWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Customize row headers
        row_headers_rtd = ["Chamber Bottom(L0)", "Chamber Lower(L1)", "TPC Top(L2)", "TPC Middle(L3)", "TPC Lower(L4)", "Cold Head(L5)"]
        for i, text in enumerate(row_headers_rtd):
            item = QTableWidgetItem(text)
            self.rtdWidget.setVerticalHeaderItem(i, item)
        self.rtdWidget.setHorizontalHeaderItem(0, QTableWidgetItem("temperature/K"))
        self.rtdWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # Create a QHBoxLayout for the right side
        rightLayout_rtd = QHBoxLayout()
        rightLayout_rtd.addWidget(self.rtdWidget)
        # Create a main QHBoxLayout to hold the right layout
        mainLayout_rtd = QHBoxLayout()
        mainLayout_rtd.addLayout(rightLayout_rtd)
        rtdTab.setLayout(mainLayout_rtd)


        # Layout for pressure gauges' sheet
        pressureTab = QWidget()
        # Create the chart widget for the right side
        self.pressureWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Customize row headers
        row_headers_pressure = ["Chamber Pressure", "Jacket Pressure"]
        for i, text in enumerate(row_headers_pressure):
            item = QTableWidgetItem(text)
            self.pressureWidget.setVerticalHeaderItem(i, item)
        self.pressureWidget.setHorizontalHeaderItem(0, QTableWidgetItem("Torr"))
        self.pressureWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        # Create a QHBoxLayout for the right side
        rightLayout = QHBoxLayout()
        rightLayout.addWidget(self.pressureWidget)
        # Create a main QHBoxLayout to hold the right layout
        mainLayout = QHBoxLayout()
        mainLayout.addLayout(rightLayout)
        pressureTab.setLayout(mainLayout)

        # Sequence for these 3, first one shows in the front page by default
        self.DataTabWidget.addTab(rtdTab, "&Leveling")
        self.DataTabWidget.addTab(pressureTab, "&Pressure")
        self.DataTabWidget.addTab(compressorTab, "&Compressor")

    # Data pumping with multi-thread enabled
    # TODO: Figure out the rtd delay, could be issue from Arduino
    def pumpDataIntoTables(self):
        # Define functions for updating each table
        def updateTableData(tableWidget, data):
            tableWidget.clearContents()
            if data is None:
                print("Warning: Data is None. Skipping update for tableWidget.")
                return
            try:
                for row, item_data in enumerate(data):
                    item = QTableWidgetItem(str(item_data))
                    tableWidget.setItem(row, 0, item)
            except TypeError:
                print("Warning: Data is not iterable. Skipping update for tableWidget.")

        # Function for retrieving and updating data for each table
        def updateDataAndTable(tableWidget, data_func):
            data = data_func()
            self.mutex.lock()
            updateTableData(tableWidget, data)
            self.mutex.unlock()

        # Retrieve data and update tables concurrently
        threads = []
        threads.append(threading.Thread(target=updateDataAndTable, args=(self.rtdWidget, ALABHK_query.get_rtd)))
        threads.append(threading.Thread(target=updateDataAndTable, args=(self.compressorWidget, ALABHK_query.get_compressor)))
        threads.append(threading.Thread(target=updateDataAndTable, args=(self.pressureWidget, ALABHK_query.get_pressure)))

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Repeat this process every 1 seconds
        QTimer.singleShot(1000, self.pumpDataIntoTables)

# For turn on compressor pop out control
class CompressorControlONDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Compressor Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<html>""<p>Are you sure you want to TURN ON cold head? <br>""<span style='color:red;'>Make sure water cooler is operating!</span></p>""</html>"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.ONClicked)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)
    
    def ONClicked(self):
        ALABHK_query.compressor_ON()
        self.accept()  # Accept the dialog


# For turn off compressor pop out control
class CompressorControlOFFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Compressor Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Are you sure you want to TURN OFF compressor?"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.OFFClicked)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

    def OFFClicked(self):
        ALABHK_query.compressor_OFF()
        self.accept()  # Accept the dialog

# For turn on heaters pop out control
class HeaterControlONDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Heaters Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<html>""<p>Are you sure you want to TURN ON heaters? ""</html>"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.HeaterOnClicked)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)
    
    def HeaterOnClicked(self):
        GPIO_pin = 23
        ALABHK_query.HeaterON(GPIO_pin)
        self.accept()

# For turn off heaters pop out control
class HeaterControlOFFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Heaters Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Are you sure you want to TURN OFF heaters?"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.HeaterOFFClicked)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

    def HeaterOFFClicked(self):
        GPIO_pin = 23
        ALABHK_query.HeaterOFF(GPIO_pin)
        self.accept()

# For exit
class StopandquitDialog(QDialog):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Exit Housekeeping")
        self.app = app  # Store the QApplication instance
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Are you sure you want to Exit?"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.on_yes_clicked)  # Close the application when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

    def on_yes_clicked(self):
        self.app.quit()  # Close the application
