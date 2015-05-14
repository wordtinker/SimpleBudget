from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import Qt
from models import TreeModel, TreeItem
import ui.manageCategories
from utils import Category, show_warning


class CategoriesManager(ui.manageCategories.Ui_Dialog, QDialog):
    def __init__(self, storage):
        super().__init__()
        self.setupUi(self)

        self.storage = storage

        # Connect signals and slots
        self.addBtn.clicked.connect(self.add_category)
        self.deleteBtn.clicked.connect(self.delete_category)
        # Show the list of available parent categories
        self.show_available_parents()
        # Show existing categories
        self.show_categories()

    def show_available_parents(self):
        self.categoryParent.clear()

        parents = self.storage.select_parents()
        parents = (p for p, *_ in parents)
        self.categoryParent.addItems(parents)

        self.categoryParent.addItem('')
        self.categoryParent.setCurrentText('')

    def show_categories(self):
        cat_model = TreeModel(('Categories', ))
        self.categoriesView.setModel(cat_model)

        categories = self.storage.select_parents()
        categories = (Category(*c) for c in categories)
        for category in categories:
            item = TreeItem(category, cat_model.rootItem)
            cat_model.rootItem.appendChild(item)

            subs = self.storage.select_subcategories(category.name)
            subs = (Category(*c) for c in subs)
            for sub in subs:
                sub_item = TreeItem(sub, item)
                item.appendChild(sub_item)

        self.categoriesView.expandAll()

    def add_category(self):
        name = self.caregoryName.text()
        if name == '':
            return

        parent = self.categoryParent.currentText()
        if parent == '':
            addition = self.storage.add_category(name)
        else:
            addition = self.storage.add_subcategory(name, parent)

        if not addition:
            show_warning("Category already exists.")
        else:
            self.show_categories()
            if parent == '':
                self.show_available_parents()

    def delete_category(self):
        index_list = self.categoriesView.selectedIndexes()
        if index_list and index_list[0].isValid():
            index = index_list[0]
            category = index.data(Qt.UserRole)

            if category.parent is not None:
                deletion = self.storage.delete_subcategory(category.id)
            else:
                deletion = self.storage.delete_category(category.name)

            if not deletion:
                show_warning("Can't delete category")
            else:
                self.show_categories()
                if category.parent is None:
                    self.show_available_parents()
