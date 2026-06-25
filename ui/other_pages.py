from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGroupBox, QFormLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QDialog, QDialogButtonBox, QFrame, QGraphicsDropShadowEffect,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from models.models import UserModel, CategoryModel

# ── Shared inline button styles ───────────────────────────
_BTN = """
QPushButton {{
    background: {bg};
    color: #FFFFFF;
    border: none;
    border-radius: 7px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: bold;
    min-height: 30px;
}}
QPushButton:hover {{ background: {hover}; }}
QPushButton:pressed {{ background: {press}; }}
"""

STYLE_PRIMARY  = _BTN.format(bg="#10B981", hover="#2E7D32", press="#145226")
STYLE_DANGER   = _BTN.format(bg="#C0392B", hover="#E04535", press="#8B1A14")
STYLE_SUCCESS  = _BTN.format(bg="#10B981", hover="#2E7D32", press="#145226")
STYLE_OUTLINE  = """
QPushButton {
    background: #EEF1F7;
    color: #10B981;
    border: 1.5px solid #10B981;
    border-radius: 7px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: bold;
    min-height: 30px;
}
QPushButton:hover { background: #FFF0DC; color: #10B981; }
"""

def _card(radius=12):
    f = QFrame()
    f.setStyleSheet(f"""
        QFrame {{
            background: #EEF1F7;
            border: 1px solid #E2E8F0;
            border-radius: {radius}px;
        }}
    """)
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(16); sh.setOffset(0, 3)
    sh.setColor(QColor(0,0,0,18))
    f.setGraphicsEffect(sh)
    return f

def _section_title(text):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "color: #1E2235; font-size: 15px; font-weight: bold; background: transparent;"
    )
    return lbl

def _inline_btn(text, style, height=30, width=None):
    b = QPushButton(text)
    b.setStyleSheet(style)
    b.setFixedHeight(height)
    b.setCursor(Qt.PointingHandCursor)
    if width:
        b.setFixedWidth(width)
    return b


# ═══════════════════════════════════════════════════════════
class ProfilePage(QWidget):
    profile_updated = Signal(dict)

    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(0)

        # Scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setSpacing(18)
        layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(container)
        outer.addWidget(scroll)

        # ── Header ──────────────────────────────────────
        hdr = QHBoxLayout()
        left = QVBoxLayout(); left.setSpacing(2)
        title = QLabel("Profil Saya")
        title.setStyleSheet("color: #1E2235; font-size: 22px; font-weight: bold;")
        sub = QLabel("Kelola informasi akun Anda")
        sub.setStyleSheet("color: #718096; font-size: 12px;")
        left.addWidget(title); left.addWidget(sub)
        hdr.addLayout(left); hdr.addStretch()
        layout.addLayout(hdr)

        # ── Identity card ────────────────────────────────
        id_card = _card()
        id_layout = QHBoxLayout(id_card)
        id_layout.setContentsMargins(20, 16, 20, 16)
        id_layout.setSpacing(16)

        avatar = QLabel("👑" if self.current_user.get("role") == "admin" else "👤")
        avatar.setStyleSheet("font-size: 36px; background: transparent;")
        avatar.setFixedWidth(54)
        id_layout.addWidget(avatar)

        info_v = QVBoxLayout(); info_v.setSpacing(4)
        name_lbl = QLabel(self.current_user.get("username", ""))
        name_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #1E2235; background: transparent;")

        role_text = "Admin" if self.current_user.get("role") == "admin" else "User"
        role_color = "#10B981" if self.current_user.get("role") == "admin" else "#10B981"
        role_pill = QLabel(f"  {role_text}  ")
        role_pill.setStyleSheet(f"""
            background: {role_color}; color: #FFFFFF;
            border-radius: 10px; font-size: 11px; font-weight: bold;
            padding: 2px 0;
        """)
        role_pill.setFixedHeight(22)
        role_pill.setFixedWidth(60)
        role_pill.setAlignment(Qt.AlignCenter)

        joined = QLabel(f"📅  Bergabung sejak {self.current_user.get('created_at', '-')[:10]}")
        joined.setStyleSheet("color: #718096; font-size: 12px; background: transparent;")

        row_top = QHBoxLayout(); row_top.setSpacing(10)
        row_top.addWidget(name_lbl); row_top.addWidget(role_pill); row_top.addStretch()
        info_v.addLayout(row_top)
        info_v.addWidget(joined)
        id_layout.addLayout(info_v, 1)
        layout.addWidget(id_card)

        # ── Edit profile card ────────────────────────────
        edit_card = _card()
        edit_layout = QVBoxLayout(edit_card)
        edit_layout.setContentsMargins(20, 16, 20, 20)
        edit_layout.setSpacing(14)

        edit_layout.addWidget(_section_title("✏  Edit Informasi Profil"))

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background: #EDF2F7; border: none; max-height: 1px;")
        edit_layout.addWidget(sep)

        FIELD_STYLE = """
            QLineEdit {
                background: #F8FAFC; border: 1.5px solid #E2E8F0;
                border-radius: 8px; padding: 8px 12px;
                font-size: 13px; color: #1E2235;
            }
            QLineEdit:focus { border-color: #10B981; background: #FFFDF9; }
        """
        LABEL_STYLE = "color: #10B981; font-size: 13px; font-weight: bold; background: transparent;"

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        lbl_u = QLabel("Username"); lbl_u.setStyleSheet(LABEL_STYLE)
        self.username_edit = QLineEdit(self.current_user.get("username", ""))
        self.username_edit.setMinimumHeight(38); self.username_edit.setStyleSheet(FIELD_STYLE)
        form.addRow(lbl_u, self.username_edit)

        lbl_e = QLabel("Email"); lbl_e.setStyleSheet(LABEL_STYLE)
        self.email_edit = QLineEdit(self.current_user.get("email", ""))
        self.email_edit.setMinimumHeight(38); self.email_edit.setStyleSheet(FIELD_STYLE)
        form.addRow(lbl_e, self.email_edit)
        edit_layout.addLayout(form)

        btn_save = _inline_btn("💾  Simpan Perubahan", STYLE_PRIMARY, height=40)
        btn_save.clicked.connect(self._save_profile)
        btn_save.setFixedWidth(200)
        edit_layout.addWidget(btn_save, alignment=Qt.AlignLeft)
        layout.addWidget(edit_card)

        # ── Change password card ─────────────────────────
        pw_card = _card()
        pw_layout = QVBoxLayout(pw_card)
        pw_layout.setContentsMargins(20, 16, 20, 20)
        pw_layout.setSpacing(14)

        pw_layout.addWidget(_section_title("🔒  Ganti Password"))

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background: #EDF2F7; border: none; max-height: 1px;")
        pw_layout.addWidget(sep2)

        PW_STYLE = FIELD_STYLE + " QLineEdit { letter-spacing: 2px; }"

        pw_form = QFormLayout()
        pw_form.setSpacing(10)
        pw_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        for attr, lbl_txt, ph in [
            ("old_pw",     "Password Lama",  "Password saat ini"),
            ("new_pw",     "Password Baru",   "Min. 6 karakter"),
            ("confirm_pw", "Konfirmasi",      "Ulangi password baru"),
        ]:
            lbl = QLabel(lbl_txt); lbl.setStyleSheet(LABEL_STYLE)
            field = QLineEdit(); field.setEchoMode(QLineEdit.Password)
            field.setPlaceholderText(ph); field.setMinimumHeight(38)
            field.setStyleSheet(FIELD_STYLE)
            setattr(self, attr, field)
            pw_form.addRow(lbl, field)
        pw_layout.addLayout(pw_form)

        btn_pw = _inline_btn("🔑  Ganti Password", STYLE_DANGER, height=40)
        btn_pw.clicked.connect(self._change_password)
        btn_pw.setFixedWidth(200)
        pw_layout.addWidget(btn_pw, alignment=Qt.AlignLeft)
        layout.addWidget(pw_card)

        layout.addStretch()

    def _save_profile(self):
        username = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        if not username or not email:
            QMessageBox.warning(self, "Peringatan", "Username dan email tidak boleh kosong.")
            return
        if len(username) < 3:
            QMessageBox.warning(self, "Peringatan", "Username minimal 3 karakter.")
            return
        if "@" not in email:
            QMessageBox.warning(self, "Peringatan", "Format email tidak valid.")
            return
        ok, msg = UserModel.update_profile(self.current_user["id"], username, email)
        if ok:
            self.current_user["username"] = username
            self.current_user["email"] = email
            self.profile_updated.emit(self.current_user)
            QMessageBox.information(self, "Berhasil", msg)
        else:
            QMessageBox.critical(self, "Gagal", msg)

    def _change_password(self):
        old = self.old_pw.text()
        new = self.new_pw.text()
        confirm = self.confirm_pw.text()
        if not old or not new or not confirm:
            QMessageBox.warning(self, "Peringatan", "Semua field password wajib diisi.")
            return
        if len(new) < 6:
            QMessageBox.warning(self, "Peringatan", "Password baru minimal 6 karakter.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Peringatan", "Password dan konfirmasi tidak cocok.")
            return
        ok, msg = UserModel.change_password(self.current_user["id"], old, new)
        if ok:
            QMessageBox.information(self, "Berhasil", msg)
            self.old_pw.clear(); self.new_pw.clear(); self.confirm_pw.clear()
        else:
            QMessageBox.critical(self, "Gagal", msg)


# ═══════════════════════════════════════════════════════════
class CategoryDialog(QDialog):
    def __init__(self, parent=None, category=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Kategori" if category else "Tambah Kategori")
        self.setFixedSize(420, 240)
        self.setStyleSheet("""
            QDialog { background: #EEF1F7; }
            QLabel  { color: #1E2235; font-size: 13px; font-weight: bold; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        FIELD = """
            QLineEdit {
                background: #EEF1F7; border: 1.5px solid #E2E8F0;
                border-radius: 8px; padding: 8px 12px;
                font-size: 13px; color: #1E2235;
            }
            QLineEdit:focus { border-color: #10B981; }
        """
        form = QFormLayout(); form.setSpacing(10)

        self.name_edit = QLineEdit(category["name"] if category else "")
        self.name_edit.setMinimumHeight(38); self.name_edit.setStyleSheet(FIELD)
        self.name_edit.setPlaceholderText("Nama kategori (wajib)")
        form.addRow("Nama *", self.name_edit)

        self.desc_edit = QLineEdit(category.get("description","") if category else "")
        self.desc_edit.setMinimumHeight(38); self.desc_edit.setStyleSheet(FIELD)
        self.desc_edit.setPlaceholderText("Deskripsi singkat (opsional)")
        form.addRow("Deskripsi", self.desc_edit)
        layout.addLayout(form)

        btns = QHBoxLayout(); btns.setSpacing(10)
        btn_cancel = _inline_btn("Batal", STYLE_OUTLINE, height=38, width=100)
        btn_cancel.clicked.connect(self.reject)
        btn_save   = _inline_btn("💾  Simpan", STYLE_PRIMARY, height=38, width=120)
        btn_save.clicked.connect(self._validate)
        btns.addStretch(); btns.addWidget(btn_cancel); btns.addWidget(btn_save)
        layout.addLayout(btns)

    def _validate(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama kategori wajib diisi.")
            return
        self.accept()

    def get_data(self):
        return {"name": self.name_edit.text().strip(),
                "description": self.desc_edit.text().strip()}


# ═══════════════════════════════════════════════════════════
class CategoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cats = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        left = QVBoxLayout(); left.setSpacing(2)
        title = QLabel("Kelola Kategori")
        title.setStyleSheet("color: #1E2235; font-size: 22px; font-weight: bold;")
        sub = QLabel("Tambah, edit, atau hapus kategori resep")
        sub.setStyleSheet("color: #718096; font-size: 12px;")
        left.addWidget(title); left.addWidget(sub)
        hdr.addLayout(left); hdr.addStretch()

        btn_add = _inline_btn("  +  Tambah Kategori", STYLE_PRIMARY, height=40)
        btn_add.setMinimumWidth(170)
        btn_add.clicked.connect(self._add)
        hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        # Table wrapped in card
        table_card = _card()
        tc_layout = QVBoxLayout(table_card)
        tc_layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nama Kategori", "Deskripsi", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 160)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setFrameShape(QFrame.NoFrame)
        tc_layout.addWidget(self.table)
        layout.addWidget(table_card)

        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet("color: #718096; font-style: italic; font-size: 12px;")
        layout.addWidget(self.count_lbl)

    def refresh(self):
        cats = CategoryModel.get_all()
        self._cats = cats
        self.table.setRowCount(0)

        for c in cats:
            row = self.table.rowCount()
            self.table.insertRow(row)

            id_item = QTableWidgetItem(str(c["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 0, id_item)

            for col, key in [(1, "name"), (2, "description")]:
                item = QTableWidgetItem(c.get(key, ""))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(row, col, item)

            cid = c["id"]
            w = QWidget(); w.setStyleSheet("background: transparent;")
            wl = QHBoxLayout(w)
            wl.setContentsMargins(8, 4, 8, 4); wl.setSpacing(8)

            btn_edit = _inline_btn("✏ Edit", STYLE_PRIMARY, height=28)
            btn_edit.clicked.connect(lambda _, i=cid: self._edit(i))

            btn_del = _inline_btn("✕ Hapus", STYLE_DANGER, height=28)
            btn_del.clicked.connect(lambda _, i=cid: self._delete(i))

            wl.addWidget(btn_edit); wl.addWidget(btn_del); wl.addStretch()
            self.table.setCellWidget(row, 3, w)
            self.table.setRowHeight(row, 44)

        self.count_lbl.setText(f"{len(cats)} kategori terdaftar")

    def _add(self):
        dlg = CategoryDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = CategoryModel.add(data["name"], data["description"])
            if ok:
                self.refresh()
            else:
                QMessageBox.critical(self, "Gagal", msg)

    def _edit(self, cat_id):
        cat = next((c for c in self._cats if c["id"] == cat_id), None)
        if not cat: return
        dlg = CategoryDialog(self, cat)
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = CategoryModel.update(cat_id, data["name"], data["description"])
            if ok:
                self.refresh()
            else:
                QMessageBox.critical(self, "Gagal", msg)

    def _delete(self, cat_id):
        cat = next((c for c in self._cats if c["id"] == cat_id), None)
        if not cat: return
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus",
            f"Hapus kategori \"{cat['name']}\"?\nResep terkait mungkin terdampak.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok, msg = CategoryModel.delete(cat_id)
            if ok:
                self.refresh()
            else:
                QMessageBox.critical(self, "Gagal", f"Gagal hapus:\n{msg}")