from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import form, sys

json_object = {}

class functions():
    # test, label, name, tests, labs
    def __init__(self, *objects):
        self.object = objects
        global json_object
        self.json_object = json_object

    def key_press_tests(self, event):
        if event.key() == Qt.Key_Delete:
            for index in self.object[3].selectedIndexes():
                self.object[3].model().removeRow(index.row())
        if event.key() == Qt.Key_Escape:
            self.object[3].clearSelection()
            self.clear()

    def key_press(self, event):
        if event.key() == Qt.Key_Delete:
            for index in self.object[0].selectedIndexes():
                self.object[0].model().removeRow(index.row())
        if event.key() == Qt.Key_Escape:
            self.object[0].clearSelection()

    def clicked_labs(self, event):
        self.object[3].model().clear()
        self.clear()
        for test in self.json_object[event.data()]:
            self.object[3].model().appendRow(self.create_item(test))

    def clicked_tests(self, event):
        self.object[0].model().clear()
        self.object[1].clear()
        self.object[2].clear()
        for labs in self.object[4].selectedIndexes():
            self.object[2].setText(event.data())
            for command in self.json_object[labs.data()][event.data()]:
                self.object[0].model().appendRow(self.create_item(command))

    @staticmethod
    def create_item(text):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        return item

    def label_return(self):
        text = self.object[1].text()
        if len(text) == 0:
            return
        item = self.create_item(text)
        if len(self.object[0].selectedIndexes()) > 0:
            self.object[0].model().insertRow(self.object[0].selectedIndexes()[0].row() + 1, item)
            self.object[0].clearSelection()
        else:
            self.object[0].model().appendRow(item)
        self.object[1].clear()

    def save_pressed(self):
        if len(self.object[4].selectedIndexes()) == 0:
            return
        text = self.object[2].text()
        count = self.object[0].model().rowCount()
        if len(text) == 0 or count == 0:
            return

        if not(text in self.json_object[self.object[4].selectedIndexes()[0].data()]):
            self.object[3].model().appendRow(functions.create_item(text))
        test = []
        for row in range(count):
            row = self.object[0].model().index(row, 0)
            test.append(self.object[0].model().itemData(row)[0])
        self.json_object[self.object[4].selectedIndexes()[0].data()][text] = test
        self.clear()

    def clear(self):
        self.object[2].clear()
        self.object[0].model().clear()
        self.object[1].clear()

class formManager():
    def __init__(self, widget):
        self.mainWindow = form.Ui_MainWindow()
        self.mainWindow.setupUi(MainWindow=widget)
        global json_object
        self.json_object = json_object

    # callback
    def clicked(self, event):
        self.mainWindow.t_tests.model().clear()
        for test in self.json_object[event.data()]:
            item = QStandardItem(test)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            item.setCheckable(True)
            self.mainWindow.t_tests.model().appendRow(item)

    # callback
    def clear_labs(self):
        self.mainWindow.t_labs.model().clear()
        self.json_object = {}

    # callback
    def add_lab(self):
        text = self.mainWindow.t_label.text()
        if len(text) == 0 or text in self.json_object:
            return
        self.json_object[text] = {}
        self.mainWindow.t_labs.model().appendRow(functions.create_item(text))
        self.mainWindow.t_label.clear()

    def all_init(self):
        # create all models
        self.mainWindow.m_tests.setModel(QStandardItemModel())
        self.mainWindow.t_tests.setModel(QStandardItemModel())
        self.mainWindow.a_tests.setModel(QStandardItemModel())
        self.mainWindow.m_test.setModel(QStandardItemModel())
        self.mainWindow.a_test.setModel(QStandardItemModel())
        labModels = QStandardItemModel()
        self.mainWindow.t_labs.setModel(labModels)
        self.mainWindow.m_labs.setModel(labModels)
        self.mainWindow.a_labs.setModel(labModels)

        m_functions = functions(self.mainWindow.m_test, self.mainWindow.m_label,
                                self.mainWindow.m_name, self.mainWindow.m_tests, self.mainWindow.m_labs)
        a_functions = functions(self.mainWindow.a_test, self.mainWindow.a_label,
                                self.mainWindow.a_name, self.mainWindow.a_tests, self.mainWindow.a_labs)

        # add functions for key-delete and esc
        self.mainWindow.m_test.keyPressEvent = m_functions.key_press
        self.mainWindow.a_test.keyPressEvent = a_functions.key_press
        self.mainWindow.m_tests.keyPressEvent = m_functions.key_press_tests
        self.mainWindow.a_tests.keyPressEvent = a_functions.key_press_tests
        self.mainWindow.t_labs.keyPressEvent = functions(self.mainWindow.t_labs).key_press

        # clicked callback
        self.mainWindow.t_labs.selectionModel().currentChanged.connect(self.clicked)
        self.mainWindow.a_labs.selectionModel().currentChanged.connect(a_functions.clicked_labs)
        self.mainWindow.m_labs.selectionModel().currentChanged.connect(m_functions.clicked_labs)
        self.mainWindow.a_tests.selectionModel().currentChanged.connect(a_functions.clicked_tests)
        self.mainWindow.m_tests.selectionModel().currentChanged.connect(m_functions.clicked_tests)
        self.mainWindow.a_tests.clicked[QtCore.QModelIndex].connect(a_functions.clicked_tests)
        self.mainWindow.m_tests.clicked[QtCore.QModelIndex].connect(m_functions.clicked_tests)
        self.mainWindow.t_labs.clicked[QtCore.QModelIndex].connect(self.clicked)
        self.mainWindow.a_labs.clicked[QtCore.QModelIndex].connect(a_functions.clicked_labs)
        self.mainWindow.m_labs.clicked[QtCore.QModelIndex].connect(m_functions.clicked_labs)

        # add validators
        validator = QtCore.QRegExp('[><][\w\s\[\]\,\(\)\.]{1,}$')
        self.mainWindow.m_label.setValidator(QRegExpValidator(validator))
        validator = QtCore.QRegExp('[\w\s\[\]\,\(\)\.]{1,}$')
        self.mainWindow.a_label.setValidator(QRegExpValidator(validator))

        # when press return, then adds new element in list
        self.mainWindow.m_label.returnPressed.connect(m_functions.label_return)
        self.mainWindow.a_label.returnPressed.connect(a_functions.label_return)
        self.mainWindow.t_label.returnPressed.connect(self.add_lab)

        # add callback for save buttons
        self.mainWindow.m_save.pressed.connect(m_functions.save_pressed)
        self.mainWindow.a_save.pressed.connect(a_functions.save_pressed)
        self.mainWindow.t_add.pressed.connect(self.add_lab)

        # add callback for clear buttons
        self.mainWindow.m_clear.pressed.connect(m_functions.clear)
        self.mainWindow.a_clear.pressed.connect(a_functions.clear)
        self.mainWindow.t_clear.pressed.connect(self.clear_labs)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = QMainWindow()
    manager = formManager(widget)
    manager.all_init()
    widget.show()
    app.exec()
