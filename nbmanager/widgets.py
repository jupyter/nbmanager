from PyQt5 import QtGui, QtWidgets


class EditableLabel(QtWidgets.QLineEdit):
    default_stylesheet = '''
    QLineEdit:read-only {
        border: none;
        background: transparent;
    }
    QLineEdit {
        /*background: white;*/
    }
    '''

    @property
    def editable(self):
        return self._editable

    @editable.setter
    def editable(self, value: bool):
        self._editable = value

    def __init__(self, text: str, parent: QtWidgets.QWidget=None):
        super().__init__(text, parent)
        self._editable = True
        self.setReadOnly(True)
        self.setStyleSheet(self.default_stylesheet)
        self.editingFinished.connect(self.make_read_only)

    def make_read_only(self):
        self.unsetCursor()
        self.setSelection(0, 0)
        self.setReadOnly(True)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if not self.editable:
            return
        self.setReadOnly(False)
        self.selectAll()
