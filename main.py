import sys
from PyQt5 import QtWidgets
from gui_client import Example


if __name__ == '__main__':


    app = QtWidgets.QApplication(sys.argv)
    w = Example()

    w.show()
    sys.exit(app.exec_())
