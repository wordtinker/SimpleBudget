from PyQt5.QtWidgets import QDialog
from PyQt5.Qt import Qt
from models import TreeModel, TreeItem
import ui.manageCategories
from utils import show_warning


class CategoriesManager(ui.manageCategories.Ui_Dialog, QDialog):
    """
    GUI that handles creation and deletion of categories.
    """
    def __init__(self, orm):
        super().__init__()
        self.setupUi(self)

        self.orm = orm

        # Connect signals and slots
        self.addBtn.clicked.connect(self.add_category)
        self.deleteBtn.clicked.connect(self.delete_category)
        # Show the list of available parent categories
        self.show_available_parents()
        # Show existing categories
        self.show_categories()

    def show_available_parents(self):
        """
        Fetches the list of categories from DB and puts them into box.
        """
        self.categoryParent.clear()

        parents = self.orm.fetch_parents()
        self.categoryParent.addItems([p.name for p in parents])

        self.categoryParent.addItem('')
        self.categoryParent.setCurrentText('')

    def show_categories(self):
        """
        Fetches the categories and subcategories from DB, builds tree
        and shows it in the GUI.
        """
        cat_model = TreeModel(('Categories', ))
        self.categoriesView.setModel(cat_model)

        categories = self.orm.fetch_parents()
        for category in categories:
            item = TreeItem(category, cat_model.rootItem)
            cat_model.rootItem.appendChild(item)

            subs = self.orm.fetch_subcategories_for_parent(category)

            for sub in subs:
                sub_item = TreeItem(sub, item)
                item.appendChild(sub_item)

        self.categoriesView.expandAll()

    def add_category(self):
        """
        Gets the name of new category and creates category or subcategory
        in DB. On success reloads all categories in the GUI.
        """
        name = self.caregoryName.text()
        if name == '':
            return
        parent = self.categoryParent.currentText()

        addition = self.orm.add_category(name, parent)
        if not addition:
            show_warning("Category already exists.")
        else:
            self.show_categories()
            if parent == '':
                self.show_available_parents()

    def delete_category(self):
        """
        Tries to delete selected category from DB. On success reloads
        all categories in the GUI.
        """
        index_list = self.categoriesView.selectedIndexes()
        if index_list and index_list[0].isValid():
            index = index_list[0]
            category = index.data(Qt.UserRole)

            deletion = self.orm.delete_category(category)
            if not deletion:
                show_warning("Can't delete category")
            else:
                self.show_categories()
                if category.parent is None:
                    self.show_available_parents()
