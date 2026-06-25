from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QSpinBox, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QGroupBox, QScrollArea, QWidget, QAbstractItemView, QFrame,
    QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from models.models import CategoryModel

FIELD_STYLE = """
QLineEdit, QTextEdit, QSpinBox {
    background: #FFFFFF; border: 1.5px solid #E0E0E0;
    border-radius: 7px; padding: 9px 12px;
    font-size: 14px; color: #212121;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
    border-color: #2E7D32; border-width: 2px;
}
"""
COMBO_STYLE = """
QComboBox {
    background: #FFFFFF; border: 1.5px solid #E0E0E0;
    border-radius: 7px; padding: 9px 12px;
    font-size: 14px; color: #212121;
}
QComboBox:focus { border-color: #2E7D32; border-width: 2px; }
"""
LABEL_STYLE = "color: #424242; font-size: 13px; font-weight: bold; background: transparent;"


class RecipeDialog(QDialog):
    def __init__(self, parent=None, recipe=None, ingredients=None, steps=None):
        super().__init__(parent)
        self.recipe = recipe
        self.init_ingredients = ingredients or []
        self.init_steps = steps or []
        self.setWindowTitle("Edit Resep" if recipe else "Tambah Resep Baru")

        # Ukuran dialog menyesuaikan layar agar tidak terasa sempit di layar besar,
        # tapi tetap punya batas wajar di layar kecil.
        screen = QGuiApplication.primaryScreen()
        avail = screen.availableGeometry() if screen else None
        if avail:
            w = min(900, int(avail.width() * 0.75))
            h = min(820, int(avail.height() * 0.85))
        else:
            w, h = 820, 760
        self.resize(w, h)
        self.setMinimumSize(720, 600)

        self._build_ui()
        if recipe:
            self._populate(recipe, ingredients, steps)

    def _build_ui(self):
        self.setStyleSheet("QDialog { background: #F5F5F5; }")
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # ── Header bar ──
        header = QFrame()
        header.setStyleSheet("background: #2E7D32;")
        header.setFixedHeight(56)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)
        title_lbl = QLabel("✏️  Edit Resep" if self.recipe else "🍳  Tambah Resep Baru")
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold; background: transparent;")
        hl.addWidget(title_lbl)
        hl.addStretch()
        main.addWidget(header)

        # ── Scrollable content ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background: #F5F5F5;")
        container = QWidget()
        container.setStyleSheet("background: #F5F5F5;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)
        scroll.setWidget(container)
        main.addWidget(scroll, 1)

        # ── Info Dasar ──
        grp_info = self._make_group("📋  Informasi Resep")
        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form.setRowWrapPolicy(QFormLayout.WrapLongRows)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Contoh: Soto Ayam Lamongan")
        self.name_edit.setMinimumHeight(42)
        self.name_edit.setStyleSheet(FIELD_STYLE)
        form.addRow(self._lbl("Nama Resep *"), self.name_edit)

        self.category_cb = QComboBox()
        self.category_cb.setMinimumHeight(42)
        self.category_cb.setStyleSheet(COMBO_STYLE)
        cats = CategoryModel.get_all()
        self._cat_map = {c["name"]: c["id"] for c in cats}
        self.category_cb.addItems([c["name"] for c in cats])
        form.addRow(self._lbl("Kategori *"), self.category_cb)

        self.region_edit = QLineEdit()
        self.region_edit.setPlaceholderText("Contoh: Jawa Tengah, Bali, Sumatera Barat")
        self.region_edit.setMinimumHeight(42)
        self.region_edit.setStyleSheet(FIELD_STYLE)
        form.addRow(self._lbl("Daerah Asal"), self.region_edit)

        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Deskripsi singkat resep ini...")
        self.desc_edit.setMinimumHeight(90)
        self.desc_edit.setMaximumHeight(110)
        self.desc_edit.setStyleSheet(FIELD_STYLE)
        form.addRow(self._lbl("Deskripsi"), self.desc_edit)

        row_nums = QHBoxLayout(); row_nums.setSpacing(12)
        self.cook_time_spin = QSpinBox()
        self.cook_time_spin.setRange(1, 9999)
        self.cook_time_spin.setSuffix(" menit")
        self.cook_time_spin.setMinimumHeight(42)
        self.cook_time_spin.setStyleSheet(FIELD_STYLE)
        self.servings_spin = QSpinBox()
        self.servings_spin.setRange(1, 999)
        self.servings_spin.setSuffix(" porsi")
        self.servings_spin.setMinimumHeight(42)
        self.servings_spin.setStyleSheet(FIELD_STYLE)
        row_nums.addWidget(self.cook_time_spin)
        row_nums.addWidget(self.servings_spin)
        form.addRow(self._lbl("Waktu & Porsi *"), row_nums)

        grp_info.layout().addLayout(form)
        layout.addWidget(grp_info)

        # ── Bahan ──
        grp_ing = self._make_group("🥕  Bahan-Bahan")
        ing_v = grp_ing.layout()

        hint_ing = QLabel("Tambahkan satu per satu bahan yang dibutuhkan, lalu isi jumlah dan satuannya.")
        hint_ing.setStyleSheet("color: #9E9E9E; font-size: 12px; background: transparent;")
        hint_ing.setWordWrap(True)
        ing_v.addWidget(hint_ing)

        self.ing_table = QTableWidget(0, 3)
        self.ing_table.setHorizontalHeaderLabels(["Nama Bahan", "Jumlah", "Satuan"])
        self.ing_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ing_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.ing_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.ing_table.setColumnWidth(1, 120)
        self.ing_table.setColumnWidth(2, 120)
        self.ing_table.setMinimumHeight(150)
        self.ing_table.verticalHeader().setVisible(False)
        self.ing_table.setAlternatingRowColors(True)
        self.ing_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ing_table.setStyleSheet("QTableWidget { font-size: 13px; }")
        ing_v.addWidget(self.ing_table)

        ing_btns = QHBoxLayout(); ing_btns.setSpacing(10)
        btn_add_ing = self._btn("+  Tambah Bahan", primary=True)
        btn_add_ing.clicked.connect(lambda: self._add_ingredient_row())
        btn_del_ing = self._btn("🗑  Hapus Baris Dipilih", danger=True)
        btn_del_ing.clicked.connect(self._del_ingredient_row)
        ing_btns.addWidget(btn_add_ing)
        ing_btns.addWidget(btn_del_ing)
        ing_btns.addStretch()
        ing_v.addLayout(ing_btns)
        layout.addWidget(grp_ing)

        # ── Langkah ──
        grp_steps = self._make_group("👨‍🍳  Cara Memasak")
        steps_v = grp_steps.layout()

        hint_steps = QLabel("Tulis langkah memasak secara berurutan. Nomor urut otomatis diperbarui.")
        hint_steps.setStyleSheet("color: #9E9E9E; font-size: 12px; background: transparent;")
        hint_steps.setWordWrap(True)
        steps_v.addWidget(hint_steps)

        self.steps_table = QTableWidget(0, 2)
        self.steps_table.setHorizontalHeaderLabels(["No", "Langkah"])
        self.steps_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.steps_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.steps_table.setColumnWidth(0, 50)
        self.steps_table.setMinimumHeight(150)
        self.steps_table.verticalHeader().setVisible(False)
        self.steps_table.setAlternatingRowColors(True)
        self.steps_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.steps_table.setStyleSheet("QTableWidget { font-size: 13px; }")
        steps_v.addWidget(self.steps_table)

        step_btns = QHBoxLayout(); step_btns.setSpacing(10)
        btn_add_step = self._btn("+  Tambah Langkah", primary=True)
        btn_add_step.clicked.connect(lambda: self._add_step_row())
        btn_del_step = self._btn("🗑  Hapus Baris Dipilih", danger=True)
        btn_del_step.clicked.connect(self._del_step_row)
        step_btns.addWidget(btn_add_step)
        step_btns.addWidget(btn_del_step)
        step_btns.addStretch()
        steps_v.addLayout(step_btns)
        layout.addWidget(grp_steps)

        layout.addStretch()

        # ── Footer bar (selalu terlihat, tidak ikut scroll) ──
        footer = QFrame()
        footer.setStyleSheet("background: #FFFFFF; border-top: 1px solid #E0E0E0;")
        footer.setFixedHeight(72)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 12, 24, 12)
        fl.setSpacing(12)

        self.required_hint = QLabel("* wajib diisi")
        self.required_hint.setStyleSheet("color: #9E9E9E; font-size: 12px; background: transparent;")
        fl.addWidget(self.required_hint)
        fl.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.setMinimumSize(120, 44)
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #FFFFFF; color: #616161;
                border: 1.5px solid #E0E0E0; border-radius: 8px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #F5F5F5; border-color: #BDBDBD; }
        """)
        btn_cancel.clicked.connect(self.reject)
        fl.addWidget(btn_cancel)

        btn_save = QPushButton("💾  Simpan Resep")
        btn_save.setMinimumSize(170, 44)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #2E7D32; color: #FFFFFF;
                border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #388E3C; }
            QPushButton:pressed { background: #1B5E20; }
        """)
        btn_save.clicked.connect(self._validate_and_accept)
        fl.addWidget(btn_save)

        main.addWidget(footer)

    # ── Helper builders ──────────────────────────────────
    def _make_group(self, title: str) -> QGroupBox:
        grp = QGroupBox(title)
        grp.setStyleSheet("""
            QGroupBox {
                background: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                margin-top: 14px;
                padding: 18px 16px 16px 16px;
                font-size: 14px;
                font-weight: bold;
                color: #2E7D32;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px; top: 2px;
                padding: 0 6px;
                background: #FFFFFF;
            }
        """)
        v = QVBoxLayout(grp)
        v.setSpacing(12)
        v.setContentsMargins(4, 10, 4, 4)
        return grp

    def _lbl(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(LABEL_STYLE)
        lbl.setMinimumWidth(120)
        return lbl

    def _btn(self, text, primary=False, danger=False) -> QPushButton:
        btn = QPushButton(text)
        btn.setMinimumHeight(38)
        btn.setCursor(Qt.PointingHandCursor)
        if primary:
            btn.setStyleSheet("""
                QPushButton {
                    background: #E8F5E9; color: #2E7D32;
                    border: 1.5px solid #A5D6A7; border-radius: 7px;
                    font-size: 13px; font-weight: bold; padding: 0 16px;
                }
                QPushButton:hover { background: #C8E6C9; }
            """)
        elif danger:
            btn.setStyleSheet("""
                QPushButton {
                    background: #FFEBEE; color: #C62828;
                    border: 1.5px solid #FFCDD2; border-radius: 7px;
                    font-size: 13px; font-weight: bold; padding: 0 16px;
                }
                QPushButton:hover { background: #FFCDD2; }
            """)
        return btn

    # ── Table row management ────────────────────────────
    def _add_ingredient_row(self, name="", amount="", unit=""):
        row = self.ing_table.rowCount()
        self.ing_table.insertRow(row)
        self.ing_table.setItem(row, 0, QTableWidgetItem(name))
        self.ing_table.setItem(row, 1, QTableWidgetItem(amount))
        self.ing_table.setItem(row, 2, QTableWidgetItem(unit))
        self.ing_table.setRowHeight(row, 38)
        if not name:
            self.ing_table.scrollToBottom()
            self.ing_table.setCurrentCell(row, 0)
            self.ing_table.editItem(self.ing_table.item(row, 0))

    def _del_ingredient_row(self):
        rows = sorted({idx.row() for idx in self.ing_table.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "Info", "Pilih dulu baris bahan yang ingin dihapus (klik nomor barisnya).")
            return
        for row in rows:
            self.ing_table.removeRow(row)

    def _add_step_row(self, instruction=""):
        row = self.steps_table.rowCount()
        self.steps_table.insertRow(row)
        no_item = QTableWidgetItem(str(row + 1))
        no_item.setFlags(Qt.ItemIsEnabled)
        no_item.setTextAlignment(Qt.AlignCenter)
        self.steps_table.setItem(row, 0, no_item)
        self.steps_table.setItem(row, 1, QTableWidgetItem(instruction))
        self.steps_table.setRowHeight(row, 40)
        if not instruction:
            self.steps_table.scrollToBottom()
            self.steps_table.setCurrentCell(row, 1)
            self.steps_table.editItem(self.steps_table.item(row, 1))

    def _del_step_row(self):
        rows = sorted({idx.row() for idx in self.steps_table.selectedIndexes()}, reverse=True)
        if not rows:
            QMessageBox.information(self, "Info", "Pilih dulu baris langkah yang ingin dihapus (klik nomor barisnya).")
            return
        for row in rows:
            self.steps_table.removeRow(row)
        for i in range(self.steps_table.rowCount()):
            item = self.steps_table.item(i, 0)
            if item:
                item.setText(str(i + 1))

    def _populate(self, recipe, ingredients, steps):
        self.name_edit.setText(recipe.get("name", ""))
        cat_name = recipe.get("category_name", "")
        idx = self.category_cb.findText(cat_name)
        if idx >= 0:
            self.category_cb.setCurrentIndex(idx)
        self.region_edit.setText(recipe.get("origin_region", ""))
        self.desc_edit.setPlainText(recipe.get("description", ""))
        self.cook_time_spin.setValue(recipe.get("cook_time_minutes", 1))
        self.servings_spin.setValue(recipe.get("servings", 1))
        for ing in (ingredients or []):
            self._add_ingredient_row(ing["name"], ing.get("amount", ""), ing.get("unit", ""))
        for step in (steps or []):
            self._add_step_row(step["instruction"])

    def _validate_and_accept(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validasi", "Nama resep wajib diisi.")
            self.name_edit.setFocus()
            return
        if len(name) < 3:
            QMessageBox.warning(self, "Validasi", "Nama resep minimal 3 karakter.")
            self.name_edit.setFocus()
            return

        valid_ing = [
            row for row in range(self.ing_table.rowCount())
            if (self.ing_table.item(row, 0) and self.ing_table.item(row, 0).text().strip())
        ]
        if not valid_ing:
            reply = QMessageBox.question(
                self, "Konfirmasi",
                "Belum ada bahan yang diisi. Tetap simpan resep tanpa bahan?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        self.accept()

    def get_data(self) -> dict:
        ingredients = []
        for row in range(self.ing_table.rowCount()):
            name = (self.ing_table.item(row, 0) or QTableWidgetItem("")).text().strip()
            if name:
                ingredients.append({
                    "name": name,
                    "amount": (self.ing_table.item(row, 1) or QTableWidgetItem("")).text().strip(),
                    "unit": (self.ing_table.item(row, 2) or QTableWidgetItem("")).text().strip(),
                })
        steps = []
        for row in range(self.steps_table.rowCount()):
            inst = (self.steps_table.item(row, 1) or QTableWidgetItem("")).text().strip()
            if inst:
                steps.append(inst)
        cat_name = self.category_cb.currentText()
        return {
            "name": self.name_edit.text().strip(),
            "category_id": self._cat_map.get(cat_name, 1),
            "origin_region": self.region_edit.text().strip(),
            "description": self.desc_edit.toPlainText().strip(),
            "cook_time_minutes": self.cook_time_spin.value(),
            "servings": self.servings_spin.value(),
            "ingredients": ingredients,
            "steps": steps,
        }