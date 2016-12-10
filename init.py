from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import *
from PyQt5 import QtCore
import form, sys


class formManager():
    def __init__(self, widget):
        self.mainWindow = form.Ui_MainWindow()
        self.mainWindow.setupUi(MainWindow=widget)

    def create_add_button(self, text):
        model = QStandardItemModel()
        item = QStandardItem()
        item.setText(text)
        item.setSelectable(False)
        item.setDropEnabled(False)
        model.appendRow(item)
        return model

    def all_init(self):
        self.mainWindow.m_labs.setModel(self.create_add_button('Add lab'))
        self.mainWindow.m_tests.setModel(self.create_add_button('Add test'))
        self.mainWindow.a_labs.setModel(self.create_add_button('Add lab'))
        self.mainWindow.a_tests.setModel(self.create_add_button('Add test'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QMainWindow()
    manager = formManager(widget)
    widget.show()
    manager.all_init()
    app.exec()