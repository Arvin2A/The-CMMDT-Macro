from PySide6.QtCore import QThread, Signal
import subprocess, os

class MacroRunner(QThread):
    output_received = Signal(str)

    def __init__(self, sikulix_path, parent=None):
        super().__init__(parent)
        self.sikulix_path = sikulix_path
        self.process = None

    def run(self):
        """Run the SikuliX macro and capture its output."""
        try:
            if os.name == "posix" and "darwin" in os.uname().sysname.lower():
                subprocess.run(["xattr", "-rd", "com.apple.quarantine", self.sikulix_path])
            self.process = subprocess.Popen(
                ["java", "-jar", self.sikulix_path, "-r", "Macro/macro.sikuli", "-c", "-v"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            for line in self.process.stdout:
                self.output_received.emit(line.strip())

            for line in self.process.stderr:
                self.output_received.emit(line.strip()) 

        except Exception as e:
            self.output_received.emit(f"Error: {e}")

    def stop(self):
        """Terminate the macro subprocess."""
        if self.process:
            self.process.kill()
            self.wait()
