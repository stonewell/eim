from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication

app = QApplication([])

tree = QTreeWidget()
tree.setHeaderLabels([''])
tree.setHeaderHidden(True)
tree.setRootIsDecorated(False)

data = ({"label": "Ben", "section": "Human"},
        {"label": "Steve", "section": "Human"},
        {"label": "Alpha12", "section": "Robot"},
        {"label": "Mike", "section": "Toaster"})

sections = {}
for d in data:
    sections.setdefault(d['section'], []).append(d['label'])

for section, labels in sections.items():
    section_item = QTreeWidgetItem(tree, [section])

    for label in labels:
        QTreeWidgetItem(section_item, [label])

    section_item.setExpanded(True)

tree.expandAll()
tree.setItemsExpandable(False)
tree.show()
app.exec()
