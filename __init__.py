import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QLabel, QHBoxLayout,
    QLineEdit, QDialog, QFormLayout, QMessageBox
)
import psycopg2

class MaterialsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Materials Management")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.load_button = QPushButton("Load Materials")
        self.load_button.clicked.connect(self.load_materials)
        self.button_layout.addWidget(self.load_button)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search materials...")
        self.button_layout.addWidget(self.search_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_materials)
        self.button_layout.addWidget(self.search_button)


        self.delete_button = QPushButton("Delete Material")
        self.delete_button.clicked.connect(self.delete_material)
        self.button_layout.addWidget(self.delete_button)


        self.add_button = QPushButton("Add Material")
        self.add_button.clicked.connect(self.add_material_dialog)
        self.button_layout.addWidget(self.add_button)


        self.conn = None
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.conn = psycopg2.connect(
                dbname="db",
                user="postgres",
                password="1234",
                host="localhost",
                port="5432"
            )
        except Exception as e:
            self.show_error(f"Error connecting to database: {e}")

    def load_materials(self):
        if not self.conn:
            self.show_error("No database connection")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id_material, title_material, material_type, picture, price, storage_quality, min_quality, pack_quality, unit FROM materials")
            materials = cursor.fetchall()

            self.table.setRowCount(len(materials))
            self.table.setColumnCount(9)
            self.table.setHorizontalHeaderLabels([
                "ID", "Name", "Type", "Picture", "Price", "Storage", "Min", "Pack", "Unit"
            ])

            for row_idx, row_data in enumerate(materials):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            self.show_error(f"Error loading materials: {e}")
        finally:
            cursor.close()

    def search_materials(self):
        if not self.conn:
            self.show_error("No database connection")
            return

        search_text = self.search_input.text()
        if not search_text:
            self.show_error("Search field is empty")
            return

        cursor = self.conn.cursor()
        try:
            query = """
                SELECT id_material, title_material, material_type, picture, price, storage_quality, min_quality, pack_quality, unit
                FROM materials
                WHERE title_material ILIKE %s OR material_type ILIKE %s
            """
            cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
            materials = cursor.fetchall()

            self.table.setRowCount(len(materials))
            self.table.setColumnCount(9)
            self.table.setHorizontalHeaderLabels([
                "ID", "Name", "Type", "Picture", "Price", "Storage", "Min", "Pack", "Unit"
            ])


            for row_idx, row_data in enumerate(materials):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            self.show_error(f"Error searching materials: {e}")
        finally:
            cursor.close()

    def add_material_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Material")
        form_layout = QFormLayout(dialog)

        name_input = QLineEdit()
        material_type_input = QLineEdit()
        picture_input = QLineEdit()
        price_input = QLineEdit()
        storage_input = QLineEdit()
        min_input = QLineEdit()
        pack_input = QLineEdit()
        unit_input = QLineEdit()

        form_layout.addRow("Name:", name_input)
        form_layout.addRow("Type:", material_type_input)
        form_layout.addRow("Picture:", picture_input)
        form_layout.addRow("Price:", price_input)
        form_layout.addRow("Storage:", storage_input)
        form_layout.addRow("Min Quality:", min_input)
        form_layout.addRow("Pack Quality:", pack_input)
        form_layout.addRow("Unit:", unit_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_material(
            name_input.text(),
            material_type_input.text(),
            picture_input.text(),
            price_input.text(),
            storage_input.text(),
            min_input.text(),
            pack_input.text(),
            unit_input.text(),
            dialog
        ))
        form_layout.addWidget(add_button)

        dialog.exec_()


    def delete_material(self):
        if not self.conn:
            self.show_error("No database connection")
            return

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_error("No row selected for deletion")
            return

        material_id = self.table.item(selected_rows[0].row(), 0).text()


        reply = QMessageBox.question(self, 'Confirm Deletion',
                                     f"Are you sure you want to delete material with ID {material_id}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            try:
                cursor.execute("DELETE FROM materials WHERE id_material = %s", (material_id,))
                self.conn.commit()
                self.load_materials()
            except Exception as e:
                self.show_error(f"Error deleting material: {e}")
            finally:
                cursor.close()

    def add_material(self, name, material_type, picture, price, storage, min_quality, pack_quality, unit, dialog):
        if not self.conn:
            self.show_error("No database connection")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO materials (title_material, material_type, picture, price, storage_quality, min_quality, pack_quality, unit)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, material_type, picture, float(price), int(storage), int(min_quality), int(pack_quality), unit))
            self.conn.commit()
            dialog.accept()
            self.load_materials()
        except Exception as e:
            self.show_error(f"Error adding material: {e}")
        finally:
            cursor.close()

    def show_error(self, message):
        error_label = QLabel(message)
        error_label.setStyleSheet("color: red;")
        self.layout.addWidget(error_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MaterialsApp()
    window.show()
    sys.exit(app.exec_())
