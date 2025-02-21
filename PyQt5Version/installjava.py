import os
import platform
import subprocess
import urllib.request

class Install:
    def check(self):
        try:
            subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    def download_java(self):
        system = platform.system()
        if system == "Windows":
            url = "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe"
            filename = "jdk_installer.exe"
        elif system == "Darwin":  # macOS
            url = "https://download.oracle.com/java/21/latest/jdk-21_macos-x64_bin.dmg"
            filename = "jdk_installer.dmg"
        else:  # Linux
            url = "https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.tar.gz"
            filename = "jdk_installer.tar.gz"
        
        print(f"Downloading Java from {url}...")
        urllib.request.urlretrieve(url, filename)
        print(f"Downloaded Java to {filename}")
        return filename

    def install_java(self,filename):
        system = platform.system()
        if system == "Windows":
            subprocess.run([filename, "/s"], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["hdiutil", "attach", filename], check=True)
            subprocess.run(["sudo", "installer", "-pkg", "/Volumes/JDK*/JDK*.pkg", "-target", "/"], check=True)
            subprocess.run(["hdiutil", "detach", "/Volumes/JDK*"], check=True)
        else:  # Linux
            subprocess.run(["tar", "-xvzf", filename, "-C", "/opt/"], check=True)
            os.environ["JAVA_HOME"] = "/opt/jdk-21"
            os.environ["PATH"] += ":/opt/jdk-21/bin"
        print("Java installation complete.")
    
