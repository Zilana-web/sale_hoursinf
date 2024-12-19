from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QWidget, QMessageBox, QTableWidget, QTableWidgetItem, \
    QInputDialog, QLabel, QFileDialog, QHBoxLayout, QLineEdit, QDialog, QHeaderView
from PyQt6.QtCore import Qt, QSize, QFile, QTextStream
from view_image import ImageViewer
import utils
from openpyxl import Workbook

class MainWindow(QMainWindow):
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user_id, self.role = user
        self.setWindowTitle("Продажа жилья")
        self.is_dark_theme = False
        self.setGeometry(100, 100, 800, 600)
        utils.center_window(self)
        layout = QVBoxLayout()

        self.theme_button = QPushButton("", self)
        self.theme_button.setFixedSize(40, 40)
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignRight)

        # Поле для поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Поиск по адресу или цене")
        search_layout.addWidget(self.search_input)

        search_button = QPushButton("Поиск", self)
        search_button.setIcon(QIcon("icons/search.png"))
        search_button.clicked.connect(self.search_properties)
        search_layout.addWidget(search_button)

        layout.addLayout(search_layout)

        if self.role == "admin":
            self.init_admin_ui(layout)
        else:
            self.init_user_ui(layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.apply_stylesheet()

    def apply_stylesheet(self):
        file = QFile("styles/light_theme.css")
        if not file.exists():
            QMessageBox.warning(self, "Ошибка", "Файл стилей не найден")
            return
        file.open(QFile.OpenModeFlag.ReadOnly)
        stylesheet = QTextStream(file).readAll()
        self.setStyleSheet(stylesheet)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        theme_file = "styles/dark_theme.css" if self.is_dark_theme else "styles/light_theme.css"

        file = QFile(theme_file)
        if not file.exists():
            QMessageBox.warning(self, "Ошибка", "Файл стилей не найден")
            return
        file.open(QFile.OpenModeFlag.ReadOnly)
        stylesheet = QTextStream(file).readAll()
        self.setStyleSheet(stylesheet)

        icon = QIcon("icons/moon.png") if self.is_dark_theme else QIcon("icons/sun.png")
        self.theme_button.setIcon(icon)

    def init_admin_ui(self, layout):
        self.properties_table = QTableWidget(self)
        self.refresh_properties()
        layout.addWidget(self.properties_table)

        add_button = QPushButton("Добавить жилье", self)
        add_button.setIcon(QIcon("icons/add.png"))
        add_button.clicked.connect(self.add_property)
        layout.addWidget(add_button)

        edit_button = QPushButton("Редактировать жилье", self)
        edit_button.setIcon(QIcon("icons/edit.png"))
        edit_button.clicked.connect(self.edit_property)
        layout.addWidget(edit_button)

        delete_button = QPushButton("Удалить жилье", self)
        delete_button.setIcon(QIcon("icons/delete.png"))
        delete_button.clicked.connect(self.delete_property)
        layout.addWidget(delete_button)

        export_button = QPushButton("Экспорт в Excel", self)
        export_button.clicked.connect(self.export_to_excel)
        layout.addWidget(export_button)

    def init_user_ui(self, layout):
        self.properties_table = QTableWidget(self)
        self.refresh_properties()
        layout.addWidget(self.properties_table)

        view_button = QPushButton("Просмотреть", self)
        view_button.setIcon(QIcon("icons/view.png"))
        view_button.clicked.connect(self.view_property)
        layout.addWidget(view_button)

        purchase_button = QPushButton("Купить", self)
        purchase_button.clicked.connect(self.purchase_property)
        layout.addWidget(purchase_button)

        history_button = QPushButton("История покупок", self)
        history_button.clicked.connect(self.view_purchase_history)
        layout.addWidget(history_button)

    def refresh_properties(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT id, address, price, image FROM properties where isAvailable = 1")
        properties = cursor.fetchall()
        self.properties_table.clear()
        self.properties_table.setSortingEnabled(False)
        self.properties_table.setRowCount(len(properties))
        self.properties_table.setColumnCount(4)
        self.properties_table.setHorizontalHeaderLabels(["ID", "Адрес", "Цена", "Изображения"])
        self.header = self.properties_table.horizontalHeader()

        self.properties_table.hideColumn(0)
        self.properties_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        

        self.properties_table.setColumnWidth(3, 120)

        for row, (prop_id, address, price, image) in enumerate(properties):
            self.properties_table.setRowHeight(row, 80)
            prop_id_item = QTableWidgetItem(str(prop_id))
            prop_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            prop_id_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            prop_id_item.setData(Qt.ItemDataRole.UserRole, prop_id)
            self.properties_table.setItem(row, 0, prop_id_item)

            address_item = QTableWidgetItem(address)
            address_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.properties_table.setItem(row, 1, address_item)

            price_item = QTableWidgetItem(f"{price:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.properties_table.setItem(row, 2, price_item)

            if image:
                first_image = image
                label = QLabel()
                pixmap = QPixmap(first_image).scaled(120, 80, Qt.AspectRatioMode.KeepAspectRatio)
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                self.properties_table.setCellWidget(row, 3, label)
            else:
                self.properties_table.setItem(row, 3, QTableWidgetItem("Нет изображений"))
        self.properties_table.setSortingEnabled(True)
    def export_to_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить таблицу как Excel",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if not file_path:
            return 

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Properties"

        headers = ["ID", "Адрес", "Цена"]
        sheet.append(headers)

        row_count = self.properties_table.rowCount()
        col_count = self.properties_table.columnCount()

        for row in range(row_count):
            excel_row = []
            for col in range(col_count):
                item = self.properties_table.item(row, col)
                excel_row.append(item.text() if item else "")
            sheet.append(excel_row)

        try:
            workbook.save(file_path)
            QMessageBox.information(self, "Успех", "Таблица успешно экспортирована в Excel!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def add_property(self):
        address, ok1 = QInputDialog.getText(self, "Добавить жилье", "Адрес:")
        if not ok1 or not address:
            return

        price, ok2 = QInputDialog.getDouble(self, "Добавить жилье", "Цена:")
        if not ok2:
            return

        image_paths, _ = QFileDialog.getOpenFileNames(
            self, "Выбрать изображение", "", "Изображение (*.png *.jpg *.jpeg)", 
        )
        image = image_paths[0] if image_paths else None

        with self.db.conn:
            self.db.conn.execute(
                "INSERT INTO properties (address, price, image) VALUES (?, ?, ?)",
                (address, price, image),
            )
        QMessageBox.information(self, "Успех", "Жилье добавлено")
        self.refresh_properties()

    def view_property(self):
        selected_items = self.properties_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите жилье для просмотра")
            return

        prop_id = selected_items[0].text()
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT image FROM properties WHERE id = ?", (prop_id,))
        result = cursor.fetchone()

        if not result or not result[0]:
            QMessageBox.warning(self, "Ошибка", "Нет доступных изображений")
            return

        image = result[0]
        try:
            image_viewer = ImageViewer(image)
            image_viewer.exec()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть изображения: {str(e)}")

    def edit_property(self):
        selected_row = self.properties_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите жилье для редактирования")
            return

        prop_id = self.properties_table.item(selected_row, 0).data()
        address = self.properties_table.item(selected_row, 1).text()
        price = float(self.properties_table.item(selected_row, 2).text())

        new_address, ok1 = QInputDialog.getText(self, "Редактировать жилье", "Новый адрес:", text=address)
        if not ok1 or not new_address:
            return

        new_price, ok2 = QInputDialog.getDouble(self, "Редактировать жилье", "Новая цена:", value=price)
        if not ok2:
            return

        image_path, _ = QFileDialog.getOpenFileName(self, "Выбрать изображение", "", "Изображения (*.png *.jpg *.jpeg)")
        if not image_path:
            image_path = self.db.conn.execute("SELECT image FROM properties WHERE id = ?", (prop_id,)).fetchone()[0]

        with self.db.conn:
            self.db.conn.execute(
                "UPDATE properties SET address = ?, price = ?, image = ? WHERE id = ?",
                (new_address, new_price, image_path, prop_id),
            )
        QMessageBox.information(self, "Успех", "Жилье обновлено")
        self.refresh_properties()

    def delete_property(self):
        selected_row = self.properties_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите жилье для удаления")
            return

        prop_id = self.properties_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Удаление жилья", "Вы уверены, что хотите удалить выбранное жилье?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            with self.db.conn:
                self.db.conn.execute("DELETE FROM properties WHERE id = ?", (prop_id,))
            QMessageBox.information(self, "Успех", "Жилье удалено")
            self.refresh_properties()

    def search_properties(self):
        query = self.search_input.text()
        if not query.strip():
            self.refresh_properties()
            return

        cursor = self.db.conn.cursor()
        cursor.execute(
            "SELECT id, address, price, image FROM properties WHERE address LIKE ? OR price LIKE ?",
            (f"%{query}%", f"%{query}%")
        )
        properties = cursor.fetchall()

        self.properties_table.setRowCount(len(properties))
        for row, (prop_id, address, price, image) in enumerate(properties):
            self.properties_table.setItem(row, 0, QTableWidgetItem(str(prop_id)))
            self.properties_table.setItem(row, 1, QTableWidgetItem(address))
            self.properties_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))

            if image:
                label = QLabel()
                pixmap = QPixmap(image.split(";")[0]).scaled(120, 80, Qt.AspectRatioMode.KeepAspectRatio)
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.properties_table.setCellWidget(row, 3, label)
            else:
                self.properties_table.setItem(row, 3, QTableWidgetItem("Нет изображений"))

    def purchase_property(self):
        selected_items = self.properties_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите жилье для покупки")
            return

        prop_id = int(self.properties_table.item(self.properties_table.currentRow(), 0).data(Qt.ItemDataRole.UserRole))
        cursor = self.db.conn.cursor()
        
        cursor.execute("SELECT id, address, price FROM properties WHERE id = ?", (prop_id,))
        property_info = cursor.fetchone()
        if not property_info:
            QMessageBox.warning(self, "Ошибка", "Выбранное жилье недоступно")
            return

        address, price = property_info[1], property_info[2]

        # Подтверждение покупки
        confirm = QMessageBox.question(
            self, "Подтверждение покупки",
            f"Вы уверены, что хотите купить жилье по адресу {address} за {price:.2f}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            with self.db.conn:
                self.db.conn.execute(
                    "INSERT INTO purchase_history (user_id, property_id) VALUES (?, ?)",
                    (self.user_id, prop_id)
                )
                self.db.conn.execute(
                    "UPDATE properties SET isAvailable = 0 WHERE id = ?",
                    (prop_id,)
                )
                self.db.conn.commit()
            QMessageBox.information(self, "Успех", "Покупка успешно завершена!")
            self.refresh_properties()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить покупку: {str(e)}")

    def view_purchase_history(self):
        cursor = self.db.conn.cursor()
        cursor.execute("select properties.id, properties.address, properties.price, purchase_history.purchase_date from purchase_history join properties on purchase_history.property_id = properties.id where purchase_history.user_id = ?", (self.user_id,))
        history = cursor.fetchall()
        if not history:
            QMessageBox.information(self, "История покупок", "У вас нет записей о покупках.")
            return

        history_window = QDialog(self)
        history_window.setWindowTitle("История покупок")
        history_window.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        table = QTableWidget(len(history), 4)
        table.setHorizontalHeaderLabels(["ID", "Адрес", "Цена", "Дата покупки"])
        table.header = table.horizontalHeader()
        table.header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        table.header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        for row, (prop_id, address, price, purchase_date) in enumerate(history):
            table.setItem(row, 0, QTableWidgetItem(str(prop_id)))
            table.setItem(row, 1, QTableWidgetItem(address))
            table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
            table.setItem(row, 3, QTableWidgetItem(purchase_date))
        
        layout.addWidget(table)

        close_button = QPushButton("Закрыть", history_window)
        close_button.clicked.connect(history_window.close)
        layout.addWidget(close_button)

        history_window.setLayout(layout)
        history_window.exec()


