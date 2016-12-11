from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import form, sys

class delete_key():
    def __init__(self, object):
        self.object = object

    def key_press(self, event):
        if event.key() == Qt.Key_Delete:
            for index in self.object.selectedIndexes():
                self.object.model().removeRow(index.row())
        if event.key() == Qt.Key_Escape:
            self.object.clearSelection()

class formManager():
    def __init__(self, widget):
        self.mainWindow = form.Ui_MainWindow()
        self.mainWindow.setupUi(MainWindow=widget)

    def create_item(self, text):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        return item

    def m_label_return(self):
        item = self.create_item(self.mainWindow.m_label.text())
        if len(self.mainWindow.m_test.selectedIndexes()) > 0:
            self.mainWindow.m_test.model().insertRow(self.mainWindow.m_test.selectedIndexes()[0].row() + 1, item)
            self.mainWindow.m_test.clearSelection()
        else:
            self.mainWindow.m_test.model().appendRow(item)
        self.mainWindow.m_label.clear()

    def a_label_return(self):
        item = self.create_item(self.mainWindow.a_label.text())
        if len(self.mainWindow.a_test.selectedIndexes()) > 0:
            self.mainWindow.a_test.model().insertRow(self.mainWindow.m_test.selectedIndexes()[0].row() + 1, item)
            self.mainWindow.a_test.clearSelection()
        else:
            self.mainWindow.a_test.model().appendRow(item)
        self.mainWindow.a_label.clear()

    def m_save_pressed(self):
        self.mainWindow.m_tests.model().appendRow(self.create_item(self.mainWindow.m_name.text()))
        for row in range(self.mainWindow.m_test.model().rowCount()):
            row = self.mainWindow.m_test.model().index(row, 0)
            self.mainWindow.m_test.model().itemData(row)[0]
        self.m_clear()

    def m_clear(self):
        self.mainWindow.m_name.clear()
        self.mainWindow.m_test.model().clear()
        self.mainWindow.m_label.clear()

    def a_save_pressed(self):
        self.mainWindow.a_tests.model().appendRow(self.create_item(self.mainWindow.a_name.text()))
        for row in range(self.mainWindow.a_test.model().rowCount()):
            row = self.mainWindow.a_test.model().index(row, 0)
            self.mainWindow.a_test.model().itemData(row)[0]
        self.a_clear()

    def a_clear(self):
        self.mainWindow.a_name.clear()
        self.mainWindow.a_test.model().clear()
        self.mainWindow.a_label.clear()

    def all_init(self):
        self.mainWindow.m_tests.setModel(QStandardItemModel())
        self.mainWindow.a_tests.setModel(QStandardItemModel())
        self.mainWindow.m_test.setModel(QStandardItemModel())
        self.mainWindow.a_test.setModel(QStandardItemModel())

        self.mainWindow.m_test.keyPressEvent = delete_key(self.mainWindow.m_test).key_press
        self.mainWindow.a_test.keyPressEvent = delete_key(self.mainWindow.a_test).key_press
        self.mainWindow.m_tests.keyPressEvent = delete_key(self.mainWindow.m_tests).key_press
        self.mainWindow.a_tests.keyPressEvent = delete_key(self.mainWindow.a_tests).key_press

        validator = QtCore.QRegExp('[><][\w\s\[\]\,\(\)\.]{1,}$')
        self.mainWindow.m_label.setValidator(QRegExpValidator(validator))
        validator = QtCore.QRegExp('[\w\s\[\]\,\(\)\.]{1,}$')
        self.mainWindow.a_label.setValidator(QRegExpValidator(validator))
        self.mainWindow.m_label.returnPressed.connect(self.m_label_return)
        self.mainWindow.a_label.returnPressed.connect(self.a_label_return)

        self.mainWindow.m_save.pressed.connect(self.m_save_pressed)
        self.mainWindow.m_clear.pressed.connect(self.m_clear)
        self.mainWindow.a_save.pressed.connect(self.a_save_pressed)
        self.mainWindow.a_clear.pressed.connect(self.a_clear)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QMainWindow()
    manager = formManager(widget)
    widget.show()
    manager.all_init()
    app.exec()
