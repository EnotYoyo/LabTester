from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import form, sys
from collections import OrderedDict
import json
from PyQt5.QtWidgets import QFileDialog
from swi_prolog import *

json_object = OrderedDict()
chosen_filename = None
prolog = None

class CusomMessageBox(QMessageBox):
    def __init__(self, text):
        super(QMessageBox, self).__init__()
        self.setWindowTitle("Warning!")
        self.setStyleSheet("background-color: rgb(224, 255, 255);\n"
                           "color: rgb(105, 105, 105);"
                           "text-align: center;")
        self.setText(text)

def save_json():
    global json_object
    with open('data.txt', 'w') as outfile:
        json.dump(json_object, outfile)

def open_json():
    global json_object
    try:
        with open('data.txt', 'r') as inputfile:
            json_object = json.load(inputfile, object_pairs_hook=OrderedDict)

    except:
        json_object = OrderedDict()

class functions():
    # test, label, name, tests, labs
    def __init__(self, autotest, *objects):
        self.object = objects
        # this is crutch!
        # because in qt first call clicked_labs is pseudo call
        self.first_change = 1
        self.keys = []
        self.autotest = autotest

    def key_press_tests(self, event):
        if event.key() == Qt.Key_Delete:
            for index in self.object[3].selectedIndexes():
                for lab in self.object[4].selectedIndexes():
                    labs = json_object[lab.data()]
                    labs.pop(index.data(), None)
                    json_object[lab.data()] = labs
                    save_json()
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
        global json_object
        if self.first_change == 1:
            self.first_change = 0
            return
        self.object[3].model().clear()
        for index in self.object[4].selectedIndexes():
            if index.data() != event.data():
                self.clear()
        for test in json_object[event.data()]:
            self.object[3].model().appendRow(self.create_not_editable_item(test))

    def clicked_tests(self, event):
        global json_object
        if len(self.object[3].selectedIndexes()) == 0:
            return
        self.object[0].model().clear()
        self.object[1].clear()
        self.object[2].clear()
        for labs in self.object[4].selectedIndexes():
            self.object[2].setText(event.data())
            for command in json_object[labs.data()][event.data()]:
                self.object[0].model().appendRow(self.create_item(command))

    @staticmethod
    def create_item(text):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled
                      | Qt.ItemIsDropEnabled | Qt.ItemIsEditable)
        return item

    @staticmethod
    def create_not_editable_item(text):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        return item

    def release_key(self, event):
        if not (event.key() == Qt.Key_Control or event.key() == Qt.Key_Return):
            return
        self.keys = []

    def label_return(self, event):
        self.object[5](event)
        if not (event.key() == Qt.Key_Control or event.key() == Qt.Key_Return):
            return
        self.keys.append(event.key())

        if len(self.keys) == 1:
            return

        if self.autotest:
            self.autotest_label_return()
            return

        text = self.object[1].toPlainText()
        if len(text) == 0:
            return
        item = self.create_item(text)
        if len(self.object[0].selectedIndexes()) > 0:
            self.object[0].model().insertRow(self.object[0].selectedIndexes()[0].row() + 1, item)
            self.object[0].clearSelection()
        else:
            self.object[0].model().appendRow(item)
        self.object[1].clear()
        self.object[0].scrollToBottom()

    def autotest_label_return(self):
        global chosen_filename
        if chosen_filename == None:
            msg = CusomMessageBox("Please, choose prolog source file")
            msg.exec()
            return

        text = self.object[1].toPlainText()
        if len(text) == 0:
            return

        answer = self.start_command(text)
        item = functions.create_item(text + '>' + answer)
        if len(self.object[0].selectedIndexes()) > 0:
            self.object[0].model().insertRow(self.object[0].selectedIndexes()[0].row() + 1, item)
            self.object[0].clearSelection()
        else:
            self.object[0].model().appendRow(item)
        self.object[1].clear()
        self.object[0].scrollToBottom()

    def save_pressed(self):
        global json_object
        if len(self.object[4].selectedIndexes()) == 0:
            return
        text = self.object[2].text()
        count = self.object[0].model().rowCount()
        if len(text) == 0 or count == 0:
            return

        if not(text in json_object[self.object[4].selectedIndexes()[0].data()]):
            self.object[3].model().appendRow(functions.create_not_editable_item(text))
        test = []
        for row in range(count):
            row = self.object[0].model().index(row, 0)
            test.append(self.object[0].model().itemData(row)[0])
        json_object[self.object[4].selectedIndexes()[0].data()][text] = test
        save_json()
        self.clear()

    def clear(self):
        self.object[1].clear()
        self.object[0].model().removeRows(0, self.object[0].model().rowCount())
        self.object[2].clear()

    def start_command(self, command):
        global prolog, chosen_filename
        if prolog == None:
            prolog = pexpect.spawn('prolog ' + chosen_filename)
            prolog.expect('.\r\n\r\n\?-')
        ret, res = get_output(prolog, command.encode())
        if ret == -1:
            return "Timeout exception"
        return res + ret

class formManager():

    def __init__(self, widget):
        self.mainWindow = form.Ui_MainWindow()
        self.mainWindow.setupUi(MainWindow=widget)

    # callback
    def clicked(self, event):
        global json_object
        self.mainWindow.t_tests.model().clear()
        for test in json_object[event.data()]:
            item = QStandardItem(test)
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            item.setCheckable(True)
            self.mainWindow.t_tests.model().appendRow(item)

    # callback
    def delete_key(self, event):
        if event.key() == Qt.Key_Delete:
            for index in self.mainWindow.t_labs.selectedIndexes():
                json_object.pop(index.data(), None)
                save_json()
                self.mainWindow.t_labs.model().removeRow(index.row())
        if event.key() == Qt.Key_Escape:
            self.mainWindow.t_labs.clearSelection()

    # callback
    def clear_labs(self):
        msg = CusomMessageBox("Are you sure, you want to delete all tests?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        ret = msg.exec_()
        if ret == QMessageBox.No:
            return
        global json_object
        self.mainWindow.t_labs.model().clear()
        self.mainWindow.t_tests.model().clear()
        self.mainWindow.m_tests.model().clear()
        self.mainWindow.a_tests.model().clear()
        self.m_functions.clear()
        self.a_functions.clear()
        json_object = OrderedDict()
        save_json()

    # callback
    def add_lab(self):
        global json_object
        text = self.mainWindow.t_label.text()
        if len(text) == 0 or text in json_object:
            return
        json_object[text] = OrderedDict()
        save_json()
        self.mainWindow.t_labs.model().appendRow(functions.create_not_editable_item(text))
        self.mainWindow.t_label.clear()

    def load_labs(self):
        global json_object
        self.mainWindow.t_labs.model().clear()
        self.mainWindow.a_labs.model().clear()
        self.mainWindow.m_labs.model().clear()
        for keys in json_object:
            self.mainWindow.t_labs.model().appendRow(functions.create_not_editable_item(keys))
        for keys in json_object:
            self.mainWindow.a_labs.model().appendRow(functions.create_not_editable_item(keys))
        for keys in json_object:
            self.mainWindow.m_labs.model().appendRow(functions.create_not_editable_item(keys))

    def clear_selections(self):
        self.load_labs()
        self.mainWindow.tabWidget.clearFocus()
        self.mainWindow.a_tests.model().clear()
        self.mainWindow.m_tests.model().clear()
        self.mainWindow.t_tests.model().clear()
        self.m_functions.clear()
        self.a_functions.clear()
        for index in self.mainWindow.a_labs.selectedIndexes():
            self.a_functions.clicked_labs(index)
        for index in self.mainWindow.m_labs.selectedIndexes():
            self.m_functions.clicked_labs(index)
        for index in self.mainWindow.t_labs.selectedIndexes():
            self.clicked(index)

    @staticmethod
    def fail_item(text):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsEnabled)
        item.setBackground(QBrush(QColor(255, 0, 0, 127)))
        return item

    @staticmethod
    def success_item(text):
        item = QStandardItem(text)
        item.setFlags(Qt.ItemIsEnabled)
        item.setBackground(QBrush(QColor(0, 255, 0, 127)))
        return item

    def start_all_tests(self):
        self.mainWindow.t_result.model().clear()
        global chosen_filename
        if chosen_filename == None:
            msg = CusomMessageBox("Please, choose prolog source file")
            msg.exec()
            return -1

        log = open('log.txt', 'w')
        for lab in self.mainWindow.t_labs.selectedIndexes():
            tests = json_object[lab.data()].items()
            for t in tests:
                name, tmp = t
                log.write(name + '\n')
                commands = []
                for c in tmp:
                    commands.append(c.split('>'))
                o, d = test(chosen_filename, commands)
                if d:
                    for c in d:
                        log.write(c + '\n')
                else:
                    log.write('OK\n')
                if o:
                    item = self.success_item(name)
                    self.mainWindow.t_result.model().appendRow(item)
                else:
                    item = self.fail_item(name)
                    self.mainWindow.t_result.model().appendRow(item)
        log.close()

    def start_selected_tests(self):
        self.mainWindow.t_result.model().clear()
        global chosen_filename
        if chosen_filename == None:
            msg = CusomMessageBox("Please, choose prolog source file")
            msg.exec()
            return -1

        log = open('log.txt', 'w')
        for lab in self.mainWindow.t_labs.selectedIndexes():
            model = self.mainWindow.t_tests.model()
            tests = [(model.index(row, 0).data(), json_object[lab.data()][model.index(row, 0).data()])
                     for row in range(model.rowCount()) if model.item(row).checkState() == QtCore.Qt.Checked]
            for t in tests:
                name, tmp = t
                log.write(name + '\n')
                commands = []
                for c in tmp:
                    commands.append(c.split('>'))
                o, d = test(chosen_filename, commands)
                if d:
                    for c in d:
                        log.write(c + '\n')
                else:
                    log.write('OK\n')
                if o:
                    item = self.success_item(name)
                    self.mainWindow.t_result.model().appendRow(item)
                else:
                    item = self.fail_item(name)
                    self.mainWindow.t_result.model().appendRow(item)
        log.close()

    def filename_callback(self):
        global chosen_filename, prolog
        chosen_filename = QFileDialog.getOpenFileName(filter='*.pl')[0]
        self.mainWindow.label_4.setText('Selected file: ' + chosen_filename)
        if not prolog == None:
            prolog.kill(0)
            prolog = pexpect.spawn('prolog ' + chosen_filename)
            prolog.expect('.\r\n\r\n\?-')

    def all_init(self):
        self.mainWindow.actionOpen.triggered.connect(self.filename_callback)

        # create all models
        self.mainWindow.m_tests.setModel(QStandardItemModel())
        self.mainWindow.t_tests.setModel(QStandardItemModel())
        self.mainWindow.a_tests.setModel(QStandardItemModel())
        self.mainWindow.m_test.setModel(QStandardItemModel())
        self.mainWindow.a_test.setModel(QStandardItemModel())
        self.mainWindow.t_labs.setModel(QStandardItemModel())
        self.mainWindow.m_labs.setModel(QStandardItemModel())
        self.mainWindow.a_labs.setModel(QStandardItemModel())
        self.mainWindow.t_result.setModel(QStandardItemModel())

        self.m_functions = functions(False, self.mainWindow.m_test, self.mainWindow.m_label, self.mainWindow.m_name,
                                     self.mainWindow.m_tests, self.mainWindow.m_labs,
                                     self.mainWindow.m_label.keyPressEvent)
        self.a_functions = functions(True, self.mainWindow.a_test, self.mainWindow.a_label, self.mainWindow.a_name,
                                     self.mainWindow.a_tests, self.mainWindow.a_labs,
                                     self.mainWindow.a_label.keyPressEvent)

        # add functions for key-delete and esc
        self.mainWindow.m_test.keyPressEvent = self.m_functions.key_press
        self.mainWindow.a_test.keyPressEvent = self.a_functions.key_press
        self.mainWindow.m_tests.keyPressEvent = self.m_functions.key_press_tests
        self.mainWindow.a_tests.keyPressEvent = self.a_functions.key_press_tests
        self.mainWindow.t_labs.keyPressEvent = self.delete_key

        # clicked callback
        self.mainWindow.t_labs.selectionModel().currentChanged.connect(self.clicked)
        self.mainWindow.a_labs.selectionModel().currentChanged.connect(self.a_functions.clicked_labs)
        self.mainWindow.m_labs.selectionModel().currentChanged.connect(self.m_functions.clicked_labs)
        self.mainWindow.a_tests.selectionModel().currentChanged.connect(self.a_functions.clicked_tests)
        self.mainWindow.m_tests.selectionModel().currentChanged.connect(self.m_functions.clicked_tests)
        self.mainWindow.a_tests.clicked[QtCore.QModelIndex].connect(self.a_functions.clicked_tests)
        self.mainWindow.m_tests.clicked[QtCore.QModelIndex].connect(self.m_functions.clicked_tests)
        self.mainWindow.t_labs.clicked[QtCore.QModelIndex].connect(self.clicked)
        self.mainWindow.a_labs.clicked[QtCore.QModelIndex].connect(self.a_functions.clicked_labs)
        self.mainWindow.m_labs.clicked[QtCore.QModelIndex].connect(self.m_functions.clicked_labs)
        self.mainWindow.tabWidget.tabBarClicked.connect(self.clear_selections)

        # when press return, then adds new element in list
        self.mainWindow.m_label.keyPressEvent = self.m_functions.label_return
        self.mainWindow.m_label.keyReleaseEvent = self.m_functions.release_key
        self.mainWindow.a_label.keyPressEvent = self.a_functions.label_return
        self.mainWindow.a_label.keyReleaseEvent = self.a_functions.release_key
        self.mainWindow.t_label.returnPressed.connect(self.add_lab)

        # add callback for save buttons
        self.mainWindow.m_save.pressed.connect(self.m_functions.save_pressed)
        self.mainWindow.a_save.pressed.connect(self.a_functions.save_pressed)
        self.mainWindow.t_add.pressed.connect(self.add_lab)

        # add callback for clear buttons
        self.mainWindow.m_clear.pressed.connect(self.m_functions.clear)
        self.mainWindow.a_clear.pressed.connect(self.a_functions.clear)
        self.mainWindow.t_clear.pressed.connect(self.clear_labs)

        self.mainWindow.t_start.pressed.connect(self.start_all_tests)
        self.mainWindow.t_selected.pressed.connect(self.start_selected_tests)
        self.load_labs()
        self.mainWindow.tabWidget.setCurrentIndex(0)
        self.mainWindow.tabWidget.clearFocus()

if __name__ == '__main__':
    open_json()
    app = QApplication(sys.argv)
    widget = QMainWindow()
    manager = formManager(widget)
    manager.all_init()
    widget.show()
    app.exec()