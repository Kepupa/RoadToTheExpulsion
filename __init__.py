import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QWidget, QLabel, QHBoxLayout, QLineEdit, QDialog, QFormLayout
)
import psycopg2

class MaterialsApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Materials Management")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Table widget
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.load_button = QPushButton("Load Materials")
        self.load_button.clicked.connect(self.load_materials)
        self.button_layout.addWidget(self.load_button)

        self.add_button = QPushButton("Add Material")
        self.add_button.clicked.connect(self.add_material_dialog)
        self.button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.button_layout.addWidget(self.delete_button)

        # Database connection
        self.conn = None
        self.connect_to_db()

    def connect_to_db(self):
        try:
            self.conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="pizda",
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
            cursor.execute("SELECT id, name, material_type, price, stock_quantity, unit FROM materials")
            materials = cursor.fetchall()

            self.table.setRowCount(len(materials))
            self.table.setColumnCount(6)
            self.table.setHorizontalHeaderLabels([
                "ID", "Name", "Type", "Price", "Stock", "Unit"
            ])

            for row_idx, row_data in enumerate(materials):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        except Exception as e:
            self.show_error(f"Error loading materials: {e}")
        finally:
            cursor.close()

    def add_material_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Material")
        form_layout = QFormLayout(dialog)

        name_input = QLineEdit()
        material_type_input = QLineEdit()
        price_input = QLineEdit()
        stock_input = QLineEdit()
        unit_input = QLineEdit()

        form_layout.addRow("Name:", name_input)
        form_layout.addRow("Type:", material_type_input)
        form_layout.addRow("Price:", price_input)
        form_layout.addRow("Stock:", stock_input)
        form_layout.addRow("Unit:", unit_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_material(
            name_input.text(),
            material_type_input.text(),
            price_input.text(),
            stock_input.text(),
            unit_input.text(),
            dialog
        ))
        form_layout.addWidget(add_button)

        dialog.exec_()

    def add_material(self, name, material_type, price, stock, unit, dialog):
        if not self.conn:
            self.show_error("No database connection")
            return


        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO materials (name, material_type, price, stock_quantity, unit)
                VALUES (%s, %s, %s, %s, %s)""",
                (name, material_type, float(price), int(stock), unit)
            )
            self.conn.commit()
            dialog.accept()
            self.load_materials()
        except Exception as e:
            self.show_error(f"Error adding material: {e}")
        finally:
            cursor.close()

    def delete_selected(self):
        if not self.conn:
            self.show_error("No database connection")
            return

        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.show_error("No row selected")
            return

        cursor = self.conn.cursor()
        try:
            for row in selected_rows:
                material_id = self.table.item(row.row(), 0).text()
                cursor.execute("DELETE FROM materials WHERE id = %s", (material_id,))
            self.conn.commit()
            self.load_materials()
        except Exception as e:
            self.show_error(f"Error deleting material: {e}")
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
