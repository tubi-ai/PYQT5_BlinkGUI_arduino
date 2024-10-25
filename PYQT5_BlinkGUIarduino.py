import sys
import serial
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, 
    QHBoxLayout, QLabel, QComboBox, QSlider, QCheckBox, 
    QMenuBar, QAction, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, QTimer

# Connecting serial port and error tracing
commPort = '/dev/cu.usbserial-1110'
try:
    ser = serial.Serial(commPort, baudrate=9600, timeout=1)
except serial.SerialException:
    QMessageBox.critical(None, "Connection Error", "Unable to connect to the device.")
    sys.exit()

class BlinkGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blink GUI with PyQt5")
        self.setGeometry(300, 300, 400, 300)
        self.initUI()

        # Creating a timer (for LED flashing)
        self.blinkTimer = QTimer()
        self.blinkTimer.timeout.connect(self.toggleLED)  # Timer her çalıştığında LED durumunu değiştirir
        self.isOn = False  # LED durumunu izlemek için

    def initUI(self):
        # LED Status Label
        self.ledStatus = QLabel("LED Status: OFF", self)
        self.ledStatus.setAlignment(Qt.AlignCenter)

        # Turn On / Off Buttons
        self.btn_On = QPushButton("Turn On", self)
        self.btn_On.clicked.connect(self.turnOnLED)

        self.btn_Off = QPushButton("Turn Off", self)
        self.btn_Off.clicked.connect(self.turnOffLED)

        # Blink Checkbox
        self.blinkCheckBox = QCheckBox("Blink", self)
        self.blinkCheckBox.stateChanged.connect(self.toggleBlink)

        # Slider for Blink Speed
        self.blinkSpeedSlider = QSlider(Qt.Horizontal, self)
        self.blinkSpeedSlider.setRange(50, 1200)
        self.blinkSpeedSlider.setValue(800)
        self.blinkSpeedSlider.setTickPosition(QSlider.TicksBelow)
        self.blinkSpeedSlider.setTickInterval(50)
        self.blinkSpeedSliderLabel = QLabel("Blink Speed: 800 ms", self)
        self.blinkSpeedSlider.valueChanged.connect(self.updateSliderLabel)

        # Combobox for Number of Blinks
        self.comboBlink = QComboBox(self)
        self.comboBlink.addItems([str(i) for i in range(1, 21)])
        self.comboBlink.setCurrentText("5")

        # Menü Bar
        menuBar = QMenuBar(self)
        fileMenu = menuBar.addMenu("File")
        saveAction = QAction("Save", self)
        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.closeApp)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # Status Bar
        self.statusBar = QStatusBar(self)
        self.statusBar.showMessage("Status: Connected")

        # Layout
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.btn_On)
        buttonLayout.addWidget(self.btn_Off)
        buttonLayout.addWidget(self.blinkCheckBox)

        sliderLayout = QVBoxLayout()
        sliderLayout.addWidget(self.blinkSpeedSliderLabel)
        sliderLayout.addWidget(self.blinkSpeedSlider)

        comboLayout = QHBoxLayout()
        comboLayout.addWidget(QLabel("Num Blinks:"))
        comboLayout.addWidget(self.comboBlink)

        mainLayout = QVBoxLayout()
        mainLayout.setMenuBar(menuBar)
        mainLayout.addWidget(self.ledStatus)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addLayout(sliderLayout)
        mainLayout.addLayout(comboLayout)
        mainLayout.addWidget(self.statusBar)

        self.setLayout(mainLayout)
        

    def turnOnLED(self):
        if not self.blinkCheckBox.isChecked():
            ser.write(b'o')
            self.updateStatus("ON")

    def turnOffLED(self):
        ser.write(b'x')
        self.updateStatus("OFF")    

    def startBlinking(self):
        """BIt starts the link process and starts the timer according to the slider value."""
        interval = self.blinkSpeedSlider.value()
        self.blinkTimer.start(interval)  # Timer works according to slider value

    def stopBlinking(self):
        """Stops the blink process and turns off the LED."""
        self.blinkTimer.stop()
        ser.write(b'x')
        self.updateStatus("OFF")

    def toggleLED(self):
        """Changes the state of the LED and updates it instantly."""
        if self.isOn:
            ser.write(b'x')
            self.updateStatus("OFF")
        else:
            ser.write(b'o')
            self.updateStatus("ON")
        self.isOn = not self.isOn  # Inverts the LED state

    def toggleBlink(self):
        """Controls Blink mode."""
        if self.blinkCheckBox.isChecked():
            self.startBlinking()
        else:
            self.stopBlinking()

    def updateSliderLabel(self):
        """Updates the value of the slider and changes the blink speed instantly."""
        value = self.blinkSpeedSlider.value()
        self.blinkSpeedSliderLabel.setText(f"Blink Speed: {value} ms")
        if self.blinkTimer.isActive():  # If the timer is active, update its speed
            self.blinkTimer.setInterval(value)

    def updateStatus(self, status):
        """Updates the LED status label."""
        self.ledStatus.setText(f"LED Status: {status}")
        self.ledStatus.setStyleSheet(f"color: {'green' if status == 'ON' else 'red'}")

    def closeApp(self):
        """Gets confirmation from the user and closes the application."""
        reply = QMessageBox.question(self, "Exit", "Are you sure you want to exit?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

def main():
    app = QApplication(sys.argv)
    window = BlinkGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
 