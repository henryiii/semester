#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, uic
import sys
import os
from . import newsemester
import webbrowser

Slot = QtCore.pyqtSlot
Signal = QtCore.pyqtSignal
LoadUI = uic.loadUi

if getattr(sys, 'frozen', None):
     LOCDIR = sys._MEIPASS
else:
     LOCDIR = os.path.dirname(__file__)

class PandasTableModel(QtCore.QAbstractTableModel):
    def __init__(self, datain, parent=None):
        super(PandasTableModel, self).__init__(parent)
        self._data = datain
        self.changed = False

    def rowCount(self, parent):
        return len(self._data.index)

    def columnCount(self, parent):
        return len(self._data.columns)+(1 if self._data.index.name else 0)

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if self._data.index.name:
                return self._data.reset_index().columns[col]
        return None

    def data(self,index,role):
        'Used to add editing existing table cells'
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return None
        if self._data.index.name:
            return self._data.reset_index().iat[index.row(),index.column()]
        else:
            return self._data.iat[index.row(),index.column()]

    def setData(self, index, value, role):
        if self._data.index.name:
            name = self._data.index.name
            lst = self._data.reset_index()
            lst.iat[index.row(),index.column()] = str(value.toString())
            self._data = lst.set_index(name)
        else:
            self._data.iat[index.row(),index.column()] = str(value.toString())
        self.dataChanged.emit(index, index)
        self.changed = True
        return True

    def removeRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginRemoveRows(parent,row,row+count-1)
        self._data.drop(self._data.index[row:row+count],inplace=True)
        self.endRemoveRows()
        self.changed = True
        return True

    def insertRows(self, row, count, parent=QtCore.QModelIndex()):
        self.beginInsertRows(parent,row,row+count-1)
        for i in range(count):
            self._data = self._data.reindex(self._data.index.insert(i+row,
                'Num_{}'.format(len(self._data.index)) if self._data.index.name else len(self._data.index)))
            self._data.fillna('',inplace=True)
        self.endInsertRows()
        self.changed = True
        return True

    def swaprows(self, index, rowdir):
        row = index.row()
        rowother = row + rowdir
        name = self._data.index.name
        data = self._data.reset_index() if name else self._data
        oldrow = data.ix[row]

        self.removeRows(row,1)
        self.insertRows(rowother,1)

        data = self._data.reset_index() if name else self._data
        data.ix[rowother] = oldrow
        self._data = data.set_index(name) if name else data

        index = self.index(rowother,0)
        index2 = self.index(rowother,len(self._data.columns))
        self.dataChanged.emit(index,index2)
        self.changed = True

    def flags(self, index):
        return (QtCore.QAbstractTableModel.flags(self, index) |  QtCore.Qt.ItemIsEditable)

    def row_move(self, view, direction):
            selectionModel = view.selectionModel()
            rows = selectionModel.selectedRows()
            if rows:
                row = rows[0].row()
                if row+direction >= 0 and row+direction < len(self._data.index):
                    self.swaprows(rows[0], direction)
                    index = self.createIndex(row+direction,0)
                    selectionModel.select(index, QtGui.QItemSelectionModel.ClearAndSelect
                                                |QtGui.QItemSelectionModel.Rows)

    def row_add(self, view):
        selectionModel = view.selectionModel()
        rows = selectionModel.selectedRows()
        if rows:
            self.insertRows(rows[0].row(),len(rows))
        else:
            self.insertRows(len(self.tamod.data.index),1)

    def row_rem(self, view):
        selectionModel = view.selectionModel()
        rows = selectionModel.selectedRows()
        if rows:
            self.removeRows(rows[0].row(),len(rows))


class NewSem(QtGui.QMainWindow):
    def __init__(self):
        super(NewSem,self).__init__()

        # Set up the user interface from Designer.
        LoadUI(os.path.join(LOCDIR,"newsem.ui"), self)

        self.allinfo = newsemester.AllInfo()
        self.setupUI()

        self.show()

    def setupUI(self):
        self.load_ta()
        self.load_lab()
        self.load_sched()

        self.button_ta_add.clicked.connect(self.row_ta_add)
        self.button_lab_add.clicked.connect(self.row_lab_add)
        self.button_sched_add.clicked.connect(self.row_sched_add)

        self.button_ta_rem.clicked.connect(self.row_ta_rem)
        self.button_lab_rem.clicked.connect(self.row_lab_rem)
        self.button_sched_rem.clicked.connect(self.row_sched_rem)

        self.button_ta_up.clicked.connect(self.row_ta_up)
        self.button_lab_up.clicked.connect(self.row_lab_up)
        self.button_sched_up.clicked.connect(self.row_sched_up)

        self.button_ta_down.clicked.connect(self.row_ta_down)
        self.button_lab_down.clicked.connect(self.row_lab_down)
        self.button_sched_down.clicked.connect(self.row_sched_down)

        self.button_ta_save.clicked.connect(self.ta_save)
        self.button_lab_save.clicked.connect(self.lab_save)
        self.button_sched_save.clicked.connect(self.sched_save)

        self.actionHandout.triggered.connect(self.create_handout)
        self.actionSyllabus_selected.triggered.connect(self.create_syllabus_ta)
        self.actionSyllabi_all.triggered.connect(self.create_syllabi_all)
       # self.actionSyllabus_selected.triggered.connect(self.create_setup)
        self.actionSchedule.triggered.connect(self.create_schedule)
        self.actionWebpage.triggered.connect(self.create_webpage)
        self.actionLab_setup.triggered.connect(self.create_setup)
        self.actionMake_all.triggered.connect(self.create_all)

    # Loading functions

    def load_ta(self):
        self.allinfo.talistload()
        self.tamod = PandasTableModel(self.allinfo.talist, self)
        self.table_ta.setModel(self.tamod)
        self.table_ta.resizeColumnsToContents()

    def load_lab(self):
        self.allinfo.lablistload()
        self.labmod = PandasTableModel(self.allinfo.lablist, self)
        self.table_lab.setModel(self.labmod)
        self.table_lab.resizeColumnsToContents()

    def load_sched(self):
        self.allinfo.schedulelistload()
        self.schedmod = PandasTableModel(self.allinfo.schedulelist, self)
        self.table_sched.setModel(self.schedmod)
        self.table_sched.resizeColumnsToContents()

    # Add and subtract rows fns

    @Slot()
    def row_ta_rem(self):
        self.tamod.row_rem(self.table_ta)
    @Slot()
    def row_lab_rem(self):
        self.labmod.row_rem(self.table_lab)
    @Slot()
    def row_sched_rem(self):
        self.schedmod.row_rem(self.table_sched)

    @Slot()
    def row_ta_add(self):
        self.tamod.row_add(self.table_ta)
    @Slot()
    def row_lab_add(self):
        self.labmod.row_add(self.table_lab)
    @Slot()
    def row_sched_add(self):
        self.schedmod.row_add(self.table_sched)

    @Slot()
    def row_ta_up(self):
        self.tamod.row_move(self.table_ta, -1)
    @Slot()
    def row_lab_up(self):
        self.labmod.row_move(self.table_lab, -1)
    @Slot()
    def row_sched_up(self):
        self.schedmod.row_move(self.table_sched, -1)

    @Slot()
    def row_ta_down(self):
        self.tamod.row_move(self.table_ta, 1)
    @Slot()
    def row_lab_down(self):
        self.labmod.row_move(self.table_lab, 1)
    @Slot()
    def row_sched_down(self):
        self.schedmod.row_move(self.table_sched, 1)

    @Slot()
    def ta_save(self):
        self.allinfo.talist = self.tamod._data
        self.allinfo.talistsave()
        self.tamod.changed = False
    @Slot()
    def lab_save(self):
        self.allinfo.lablist = self.labmod._data
        self.allinfo.lablistsave()
        self.labmod.changed = False
    @Slot()
    def sched_save(self):
        self.allinfo.schedulelist = self.schedmod._data
        self.allinfo.schedulelistsave()
        self.schedmod.changed = False

    def prepare_files(self):
        self.allinfo.talist = self.tamod._data
        self.allinfo.lablist = self.labmod._data
        self.allinfo.schedulelist = self.schedmod._data
        self.allinfo.write_latex_template()

    @Slot()
    def create_handout(self):
        self.prepare_files()
        webbrowser.open(self.allinfo.make_latex_handout())

    @Slot()
    def create_syllabi_all(self):
        self.prepare_files()
        self.allinfo.make_latex_syllabi()

    @Slot()
    def create_syllabus_ta(self):
        self.prepare_files()
        selectionModel = self.table_ta.selectionModel()
        rows = selectionModel.selectedRows()
        row = rows[0].row() if rows else 0
        webbrowser.open(self.allinfo.make_latex_syllabus(self.allinfo.talist.index[row]))

    @Slot()
    def create_schedule(self):
        self.prepare_files()
        webbrowser.open(self.allinfo.make_latex_schedule())

    @Slot()
    def create_setup(self):
        self.prepare_files()
        webbrowser.open(self.allinfo.write_email_talist())

    @Slot()
    def create_webpage(self):
        self.prepare_files()

        self.allinfo.write_html_talist()
        self.allinfo.write_html_classlist()

        answer = QtGui.QMessageBox.question(self,
                "Update files",
                "Do you want to update the files in the web folder?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)

        if answer == QtGui.QMessageBox.Yes:
            newsemester.copy_web_files()
            answer = QtGui.QMessageBox.question(self,
                    "Upload files",
                    "Do you want to upload the files in the web folder?",
                    QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if answer == QtGui.QMessageBox.Yes:
                newsemester.send_web_files()

    @Slot()
    def create_all(self):
        self.prepare_files()
        self.allinfo.make_latex_handout()
        self.allinfo.make_latex_schedule()
        self.allinfo.make_latex_syllabi()
        self.allinfo.write_email_talist()
        self.allinfo.write_html_talist()
        self.allinfo.write_html_classlist()

    def closeEvent(self, event):
        if self.tamod.changed or self.labmod.changed or self.schedmod.changed:
            answer = QtGui.QMessageBox.question(self,
                "Save before quiting",
                "Do you want to save all the changes?",
                QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel)

            if answer==QtGui.QMessageBox.Save:
                self.ta_save()
                self.lab_save()
                self.sched_save()
                event.accept()
            elif answer==QtGui.QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    mainapp = NewSem()
    app.exec_()
    return mainapp


if __name__ == '__main__':
    self = main()
