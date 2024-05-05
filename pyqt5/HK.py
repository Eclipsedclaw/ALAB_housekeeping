#!/usr/bin/env python3

from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
from PyQt5.QtGui import QColor

# For turn on compressor pop out control
class CompressorControlONDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Compressor Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<html>""<p>Are you sure you want to TURN ON cold head? <br>""<span style='color:red;'>Make sure water cooler is operating!</span></p>""</html>"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.accept)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

# For turn off compressor pop out control
class CompressorControlOFFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Compressor Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Are you sure you want to TURN OFF compressor?"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.accept)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

# For turn on heaters pop out control
class HeaterControlONDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Heaters Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<html>""<p>Are you sure you want to TURN ON heaters? ""</html>"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.accept)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

# For turn off heaters pop out control
class HeaterControlOFFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Heaters Control")
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Are you sure you want to TURN OFF heaters?"))
        
        yesButton = QPushButton("Yes")
        yesButton.clicked.connect(self.accept)  # Accept the dialog when "Yes" is clicked
        layout.addWidget(yesButton)
        
        noButton = QPushButton("No")
        noButton.clicked.connect(self.reject)  # Reject the dialog when "No" is clicked
        layout.addWidget(noButton)
        
        self.setLayout(layout)

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        # Set the geometry of the main window
        self.setGeometry(100, 100, 550, 400)  # (x, y, width, height)

        self.originalPalette = QApplication.palette()

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())

        grafanaText = QLabel("<a href='http://aramakilab.neu.edu:3000/d/f12ea01c-2b65-43c9-bd97-90bd0ddd0dfb/aramaki-lab-housekeeping?orgId=1&refresh=5s'>click here for Grafana Monitor</a>")
        grafanaText.setTextFormat(Qt.RichText)
        grafanaText.setOpenExternalLinks(True)

        self.useStylePaletteCheckBox = QCheckBox("&Use style's standard palette")
        self.useStylePaletteCheckBox.setChecked(True)

        disableWidgetsCheckBox = QCheckBox("&Lock changes")

        self.createTopRightGroupBox()
        self.createBottomLeftTabWidget()

        styleComboBox.activated[str].connect(self.changeStyle)
        disableWidgetsCheckBox.toggled.connect(self.topRightGroupBox.setDisabled)
        disableWidgetsCheckBox.toggled.connect(self.bottomLeftTabWidget.setDisabled)

        topLayout = QHBoxLayout()
        topLayout.addWidget(grafanaText)
        topLayout.addStretch(1)
        topLayout.addWidget(disableWidgetsCheckBox, alignment=Qt.AlignRight)

        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.topRightGroupBox, 1, 1)
        mainLayout.addWidget(self.bottomLeftTabWidget, 1, 0)

        # Set row stretch factors to make the entire layout longer vertically
        mainLayout.setRowStretch(0, 3)

        mainLayout.setColumnStretch(0, 2)
        mainLayout.setColumnStretch(1, 1)
        self.setLayout(mainLayout)

        self.setWindowTitle("ALAB Housekeeping")
        self.changeStyle('qt5ct-style')

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        self.changePalette()

    def changePalette(self):
        if (self.useStylePaletteCheckBox.isChecked()):
            QApplication.setPalette(QApplication.style().standardPalette())
        else:
            QApplication.setPalette(self.originalPalette)

    def advanceProgressBar(self):
        curVal = self.progressBar.value()
        maxVal = self.progressBar.maximum()
        self.progressBar.setValue(curVal + (maxVal - curVal) / 100)


    def turnONCompressor(self):
        dialog = CompressorControlONDialog(self)
        dialog.exec()

    def turnOFFCompressor(self):
        dialog = CompressorControlOFFDialog(self)
        dialog.exec()
    
    def turnONHeater(self):
        dialog = HeaterControlONDialog(self)
        dialog.exec()

    def turnOFFHeater(self):
        dialog = HeaterControlOFFDialog(self)
        dialog.exec()

    def createTopRightGroupBox(self):
        self.topRightGroupBox = QGroupBox("Control")

        refrashButton = QPushButton("Refresh current system status")
        refrashButton.setDefault(True)
        refrashButton.setMaximumWidth(250)  # Set maximum width

        HeaterText = QLabel("Control Heater")
        HeaterText.setTextFormat(Qt.RichText)
        HeaterText.setOpenExternalLinks(True)

        heaterButtonLayout = QHBoxLayout()  # Layout for TURN ON and TURN OFF buttons

        heaterONButton = QPushButton("TURN ON")
        heaterONButton.setDefault(True)
        heaterONButton.setMaximumWidth(100)  # Set maximum width
        heaterONButton.clicked.connect(self.turnONHeater)  # Connect to function for turning ON heaters

        heaterOFFButton = QPushButton("TURN OFF")
        heaterOFFButton.setDefault(True)
        heaterOFFButton.setMaximumWidth(100)  # Set maximum width
        heaterOFFButton.clicked.connect(self.turnOFFHeater)  # Connect to function for turning OFF heaters

        heaterButtonLayout.addWidget(heaterONButton)  # Add TURN ON button
        heaterButtonLayout.addWidget(heaterOFFButton)  # Add TURN OFF button

        CompressorText = QLabel("Control Compressor")
        CompressorText.setTextFormat(Qt.RichText)
        CompressorText.setOpenExternalLinks(True)

        compressorButtonLayout = QHBoxLayout()  # Layout for TURN ON and TURN OFF buttons

        compressorONButton = QPushButton("TURN ON")
        compressorONButton.setDefault(True)
        compressorONButton.setMaximumWidth(100)  # Set maximum width
        compressorONButton.clicked.connect(self.turnONCompressor)  # Connect to function for turning ON compressor

        compressorOFFButton = QPushButton("TURN OFF")
        compressorOFFButton.setDefault(True)
        compressorOFFButton.setMaximumWidth(100)  # Set maximum width
        compressorOFFButton.clicked.connect(self.turnOFFCompressor)  # Connect to function for turning OFF compressor

        compressorButtonLayout.addWidget(compressorONButton)  # Add TURN ON button
        compressorButtonLayout.addWidget(compressorOFFButton)  # Add TURN OFF button

        layout = QVBoxLayout()
        layout.addWidget(refrashButton, alignment=Qt.AlignLeft)  # Align center horizontally
        layout.addWidget(HeaterText, alignment=Qt.AlignLeft)  # Align left horizontally
        layout.addLayout(heaterButtonLayout)  # Add TURN ON and TURN OFF buttons side by side
        layout.addWidget(CompressorText, alignment=Qt.AlignLeft)
        layout.addLayout(compressorButtonLayout)  # Add TURN ON and TURN OFF buttons side by side
        layout.addStretch(1)
        self.topRightGroupBox.setLayout(layout)


    def createBottomLeftTabWidget(self):
        self.bottomLeftTabWidget = QTabWidget()
        self.bottomLeftTabWidget.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)

        tab1 = QWidget()
        tableWidget1 = QTableWidget(10, 2)

        # Adjust size policy and size hint
        tableWidget1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tableWidget1.setMinimumHeight(200)  # Adjust minimum height to show more rows initially

        tab1hbox = QHBoxLayout()
        tab1hbox.setContentsMargins(5, 5, 5, 5)
        tab1hbox.addWidget(tableWidget1)
        tab1.setLayout(tab1hbox)

        tab2 = QWidget()
        textEdit = QTextEdit()

        tableWidget2 = QTableWidget(3, 2)

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(tableWidget2)
        tab2.setLayout(tab2hbox)

        tab3 = QWidget()
        tableWidget3 = QTableWidget(2, 2)

        # Adjust size policy and size hint
        tableWidget3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tableWidget3.setMinimumHeight(200)  # Adjust minimum height to show more rows initially

        tab3hbox = QHBoxLayout()
        tab3hbox.setContentsMargins(5, 5, 5, 5)
        tab3hbox.addWidget(tableWidget3)
        tab3.setLayout(tab3hbox)

        self.bottomLeftTabWidget.addTab(tab3, "&Pressure")
        self.bottomLeftTabWidget.addTab(tab1, "&Leveling")
        self.bottomLeftTabWidget.addTab(tab2, "&Compressor")

    def pumpDataIntoTables(self):
        # For the first table (tab1)
        tableWidget1 = self.bottomLeftTabWidget.widget(0).layout().itemAt(0).widget()
        for row in range(tableWidget1.rowCount()):
            for col in range(tableWidget1.columnCount()):
                # Assuming you have data stored in a list named data_list
                item = QTableWidgetItem(str(data_list[row][col]))
                tableWidget1.setItem(row, col, item)

        # For the second table (tab2)
        tableWidget2 = self.bottomLeftTabWidget.widget(1).layout().itemAt(0).widget()
        for row in range(tableWidget2.rowCount()):
            for col in range(tableWidget2.columnCount()):
                # Assuming you have data stored in a list named data_list2
                item = QTableWidgetItem(str(data_list2[row][col]))
                tableWidget2.setItem(row, col, item)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())