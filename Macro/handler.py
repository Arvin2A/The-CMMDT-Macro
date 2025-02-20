from PySide6.QtCore import QThread, Signal
import subprocess, os, urllib.request, requests

class MacroRunner(QThread):
    output_received = Signal(str)

    def __init__(self, macro_dir="Macro", sikulix_url=None, parent=None):
        super().__init__(parent)
        self.macro_dir = macro_dir
        self.sikulix_url = sikulix_url or "https://launchpad.net/sikuli/sikulix/2.0.5/+download/sikulixide-2.0.5.jar"
        self.sikulix_path = os.path.join(self.macro_dir, "sikulix.jar")
        self.process = None
    def download_sikulix(self):
        """Download SikuliX JAR if it doesn't exist."""
        if not os.path.exists(self.macro_dir):
            os.makedirs(self.macro_dir)  # Create Macro directory if missing

        if not os.path.exists(self.sikulix_path):
            self.output_received.emit("Downloading SikuliX...")
            try:
                response = requests.get(self.sikulix_url, stream=True)
                response.raise_for_status()

                with open(self.sikulix_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                self.output_received.emit("Download complete!")
            except requests.exceptions.RequestException as e:
                self.output_received.emit(f"Download failed: {e}")
                return False
        return True
    def run(self):
        """Run the SikuliX macro and capture its output."""
        if not self.download_sikulix():
            return
        try:
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
            self.process.terminate()
            self.wait()
