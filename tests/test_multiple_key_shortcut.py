from PySide6.QtWidgets import QApplication, QMessageBox, QToolBar
from PySide6.QtCore import QEvent, QObject, QCoreApplication
from PySide6.QtGui import QAction, QKeySequence, QShortcut

def beep():
    print('beep')

app = QApplication([])

toolbar = QToolBar()
toolbar.show()

action = QAction("Action", toolbar, shortcut=QKeySequence("Ctrl+X, Ctrl+C"), triggered=beep)
toolbar.addAction(action)

QShortcut("Ctrl+X, Ctrl+D", toolbar, beep)

app.exec()
