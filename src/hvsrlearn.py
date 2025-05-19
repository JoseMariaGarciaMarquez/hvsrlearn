import sys
from PyQt5.QtWidgets import QApplication
from hvsr_gui import HvsrMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HvsrMainWindow()
    window.show()
    sys.exit(app.exec_())