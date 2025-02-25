from mainwindow import Ui_MainWindow
from console import Ui_Console
from PySide6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QMainWindow, QTextEdit
from PySide6.QtCore import QFile, Signal
from installjava import Install
from handler import MacroRunner
import sys
import os
import subprocess
import json
import time
# Get the directory where main.py is located
if getattr(sys, 'frozen', False):  # Running from PyInstaller
    BASE_DIR = sys._MEIPASS  # Temporary extraction folder
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "macro.sikuli", "data.json")
if os.path.exists(DATA_FILE):
    print("File found!")
else:
    print("File NOT found!")
print("E")
#####UI MAIN SCRIPT, SEE MACRO.SIKULIX/MACRO.PY FOR MACRO CONTROLS (MUST EDIT WITH SIKULIX IDE)#####
data = {
    "ShakeEnabled": True,
    "CastDuration": 1.0,
    "ShowVisualIndicators": True,
    "ShakeSpeed": 0.5,
    "Control": 0.0,
    "ClickShake": True,
    "IsLinux": False
}
class ConsoleOutput:
    def __init__(self, text_edit: QTextEdit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.append(text)  # Append text to the QTextEdit

    def flush(self):
        pass  # Needed for compatibility with sys.stdout
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.runbutton.clicked.connect(self.start_macro2)
        self.ui.stopbutton.clicked.connect(self.stop_macro)
        self.macro_runner = None
        self.sikulix_path = os.path.join(BASE_DIR, "sikulix.jar")
        self.load_data()
        self.jsonpath = "Macro/macro.sikuli\data.json"
        #console
        self.console = QWidget()
        self.consoleui = Ui_Console()
        self.consoleui.setupUi(self.console)
        self.consoleui.closeconsole.clicked.connect(self.consoletoggle)
        self.ui.consolebutton.clicked.connect(self.consoletoggle)
        self.ui.consolebutton.setEnabled(True)
        self.console_widget = self.consoleui.log
        self.console_widget.setReadOnly(True)  # Make sure it's read-only
        sys.stdout = ConsoleOutput(self.console_widget)  # Redirect print() output
        sys.stderr = ConsoleOutput(self.console_widget)  # Redirect errors
        self.setsimplejson_path = "simplejson"
        self.process = None
    def consoletoggle(self):
        if not self.console.isVisible():
            self.console.show()
        else:
            self.console.hide()   
    def update_console(self, text):
        """Update console log widget with new output."""
        self.console_widget.append(text) 
    def load_data(self):
        try:
            with open(DATA_FILE,"r") as w:
                data = json.load(w)
                self.ui.castduration.setValue(data.get("CastDuration"))
                self.ui.skipshake.setChecked(data.get("ShakeEnabled"))
                self.ui.latency.setValue(data.get("ShakeSpeed"))
                self.ui.visual_indicators.setChecked(data.get("ShowVisualIndicators"))
                self.ui.control.setValue(data.get("Control"))
                self.ui.clickshake.setChecked(data.get("ClickShake"))
                self.ui.islinux.setChecked(data.get("IsLinux"))
        except:
            try:
                with open("macro.sikuli/data.json","r") as w:
                    data = json.load(w)
                    self.ui.castduration.setValue(data.get("CastDuration"))
                    self.ui.skipshake.setChecked(data.get("ShakeEnabled"))
                    self.ui.latency.setValue(data.get("ShakeSpeed"))
                    self.ui.visual_indicators.setChecked(data.get("ShowVisualIndicators"))
                    self.ui.control.setValue(data.get("Control"))
                    self.ui.clickshake.setChecked(data.get("ClickShake"))
                    self.ui.islinux.setChecked(data.get("IsLinux"))
            except Exception as e:
                self.show_error_dialog(f"data.json doesnt exist! See: {e}")
    def show_error_dialog(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)  # Critical icon for error
        error_dialog.setWindowTitle("Error")       # Title for the dialog
        error_dialog.setText("An error occurred!")
        error_dialog.setInformativeText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)  # Only "OK" button
        error_dialog.exec()    
    def start_macro2(self):
        """Start the macro and update the console."""
        if self.macro_runner and self.macro_runner.isRunning():
            return
        print("Start Macro button clicked!")
        if self.sikulix_path != "":
            data = {
                "CastDuration": self.ui.castduration.value(),
                "ShakeEnabled": self.ui.skipshake.isChecked(),
                "ShakeSpeed": self.ui.latency.value(),
                "ShowVisualIndicators": self.ui.visual_indicators.isChecked(),
                "Control": self.ui.control.value(),
                "ClickShake": self.ui.clickshake.isChecked(),
                "IsLinux": self.ui.islinux.isChecked()
            }
            try:
                with open(DATA_FILE,"w") as f:
                    json.dump(data,f,indent=4)
                    f.flush()
            except:
                try:
                    with open("macro.sikuli\data.json","w") as f:
                        json.dump(data,f,indent=4)
                        f.flush()
                except Exception as e:
                    self.show_error_dialog(f"Failed to save data. Error: {e}")
            self.ui.runbutton.setEnabled(False)
            self.ui.stopbutton.setEnabled(True)
        self.macro_runner = MacroRunner()
        self.macro_runner.output_received.connect(self.update_console)
        self.macro_runner.start()
    def stop_macro(self):
        if self.macro_runner:
            self.macro_runner.stop()
            self.macro_runner.wait()
            print("Terminated")
            self.macro_runner = None
            self.ui.stopbutton.setEnabled(False)
            self.ui.runbutton.setEnabled(True)
if __name__ == "__main__":
    install = Install()
    if install.check():
        print("Java is already installed.")
    else:
        print("Java is not installed. Downloading and installing...")
        filename = install.download_java()
        install.install_java(filename)
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    if window.macro_runner:
        window.macro_runner.stop()
    sys.exit(app.exec())