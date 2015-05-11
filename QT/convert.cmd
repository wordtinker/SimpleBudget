::CALL pyrcc5 -o iconset_rc.py iconset.qrc
CALL pyuic5 -o mainWindow.py mainWindow.ui
CALL pyuic5 -o manageAccounts.py manageAccounts.ui
CALL pyuic5 -o manageTransaction.py manageTransaction.ui
CALL pyuic5 -o transactionsRoll.py transactionsRoll.ui
CALL pyuic5 -o manageCategories.py manageCategories.ui
CALL pyuic5 -o manageBudget.py manageBudget.ui
pause