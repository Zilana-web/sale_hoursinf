import sqlite3
from PyQt6.QtWidgets import QApplication
from database import Database
from login_window import LoginWindow




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    db = Database()
    db.create_tables()
    # db.seed_data()
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())
