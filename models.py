from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt,\
    QAbstractListModel, QVariant, QAbstractTableModel
from decimal import Decimal


class TreeItem:
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            item = self.itemData[column]
            if isinstance(item, Decimal):
                return "{0:.2f}".format(item)
            else:
                return item
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class TreeModel(QAbstractItemModel):
    def __init__(self, header):
        super().__init__()

        self.rootItem = TreeItem(header)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == Qt.UserRole:
            return item.itemData

        if role != Qt.DisplayRole:
            return None

        return item.data(index.column())

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class ListModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.items = []

    # Basic methods

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        # User role for returning whole Item
        if role == Qt.UserRole:
            return QVariant(self.items[index.row()])

        if role != Qt.DisplayRole:
            return QVariant()

        item = self.items[index.row()]
        return QVariant(item[0])

    # Editable model methods

    def setData(self, index, value, role=None):
        if index.isValid():
            self.items[index.row()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.items.insert(position, None)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.items.pop(position)
        self.endRemoveRows()
        return True

    def addItem(self, item):
        row = 0
        self.insertRows(row, 1)
        self.setData(self.index(row), item)


class TableModel(QAbstractTableModel):
    """
    Simmple basis model in Qt.
    Data is stored in the list.
    For more complex structures subclass QAbstractModel directly.
    Model needs a list of headers to work properly
    """

    def __init__(self, headers):
        super().__init__()

        self.headers = headers
        self.items = []

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.headers)

    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()
        if role == Qt.UserRole:
            return self.items[index.row()]
        elif role != Qt.DisplayRole:
            return QVariant()

        data = self.items[index.row()][index.column()]
        if isinstance(data, Decimal):
            return "{0:.2f}".format(data)
        else:
            return QVariant(data)

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headers[col])
        return QVariant()

    def setData(self, index, value, role=None):
        if index.isValid():
            self.items[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.items.insert(position, [None] * self.columnCount())
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            self.items.pop(position)
        self.endRemoveRows()
        return True

    def prepare(self):
        self.removeRows(0, self.rowCount())

    def addRow(self, item):
        self.insertRows(0, 1)
        self.items[0] = item
        self.dataChanged.emit(self.index(0, 0), self.index(0, 0))
        return 0  # row


class CategoryListModel(ListModel):
    def data(self, index, role=None):
        if not index.isValid():
            return QVariant()

        # User role for returning whole Item
        if role == Qt.UserRole:
            return QVariant(self.items[index.row()])

        if role != Qt.DisplayRole:
            return QVariant()

        item = self.items[index.row()]
        return QVariant(item.parent + '::' + item.name)