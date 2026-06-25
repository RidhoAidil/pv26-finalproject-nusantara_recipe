from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QFrame, QAbstractItemView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from models.models import RecipeModel, CategoryModel
from ui.recipe_dialog import RecipeDialog
from utils.export import export_to_csv, export_recipe_to_pdf


def _shadow(w, blur=18, dy=3, alpha=16):
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(blur); sh.setOffset(0, dy); sh.setColor(QColor(0,0,0,alpha))
    w.setGraphicsEffect(sh)


def _card(bg="#FFFFFF", radius=14):
    f = QFrame()
    f.setStyleSheet(f"QFrame{{background:{bg};border:none;border-radius:{radius}px;}}")
    _shadow(f)
    return f


S_DETAIL = "QPushButton{background:#DBEAFE;color:#1D4ED8;border:none;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:bold;}QPushButton:hover{background:#BFDBFE;}"
S_PDF    = "QPushButton{background:#D1FAE5;color:#065F46;border:none;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:bold;}QPushButton:hover{background:#A7F3D0;}"
S_EDIT   = "QPushButton{background:#FEF3C7;color:#92400E;border:none;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:bold;}QPushButton:hover{background:#FDE68A;}"
S_DEL    = "QPushButton{background:#FEE2E2;color:#991B1B;border:none;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:bold;}QPushButton:hover{background:#FECACA;}"


class RecipeListPage(QWidget):
    recipe_selected = Signal(int)

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.is_admin = current_user.get("role") == "admin"
        self._sort_col = "name"; self._sort_order = "ASC"
        self._recipes = []
        self._build_ui(); self.refresh()

    def _build_ui(self):
        self.setStyleSheet("background:#EEF1F7;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 22)
        layout.setSpacing(16)

        # ── Header ────────────────────────────────────────────
        hdr = QHBoxLayout()
        lv = QVBoxLayout(); lv.setSpacing(4)
        title = QLabel("Daftar Resep")
        title.setStyleSheet("color:#1E2235;font-size:24px;font-weight:bold;")
        sub = QLabel("Jelajahi koleksi resep masakan Nusantara")
        sub.setStyleSheet("color:#64748B;font-size:13px;")
        lv.addWidget(title); lv.addWidget(sub)
        hdr.addLayout(lv); hdr.addStretch()

        if self.is_admin:
            btn_add = QPushButton("＋  Tambah Resep")
            btn_add.setMinimumHeight(42)
            btn_add.setStyleSheet(
                "QPushButton{background:#10B981;color:#FFF;border:none;border-radius:10px;"
                "font-size:13px;font-weight:bold;padding:0 22px;}"
                "QPushButton:hover{background:#059669;}"
            )
            btn_add.setCursor(Qt.PointingHandCursor)
            btn_add.clicked.connect(self._add_recipe)
            hdr.addWidget(btn_add)
        layout.addLayout(hdr)

        # ── Search & filter bar ───────────────────────────────
        bar = _card("#FFFFFF", 12)
        bl = QHBoxLayout(bar); bl.setContentsMargins(16, 12, 16, 12); bl.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍  Cari nama resep atau daerah asal...")
        self.search_edit.setMinimumHeight(40)
        self.search_edit.textChanged.connect(self.refresh)
        bl.addWidget(self.search_edit, 3)

        self.cat_filter = QComboBox()
        self.cat_filter.setMinimumHeight(40); self.cat_filter.setMinimumWidth(175)
        self.cat_filter.addItem("🗂  Semua Kategori", None)
        for c in CategoryModel.get_all():
            self.cat_filter.addItem(c["name"], c["id"])
        self.cat_filter.currentIndexChanged.connect(self.refresh)
        bl.addWidget(self.cat_filter, 2)

        self.sort_cb = QComboBox()
        self.sort_cb.setMinimumHeight(40); self.sort_cb.setMinimumWidth(165)
        self.sort_cb.addItems(["↑ Nama A–Z","↓ Nama Z–A","⏱ Waktu Singkat","⏱ Waktu Lama"])
        self.sort_cb.currentIndexChanged.connect(self._on_sort)
        bl.addWidget(self.sort_cb, 2)

        btn_csv = QPushButton("📥  Export CSV")
        btn_csv.setMinimumHeight(40)
        btn_csv.setStyleSheet(
            "QPushButton{background:#EFF6FF;color:#2563EB;border:none;"
            "border-radius:8px;font-size:12px;font-weight:bold;padding:0 16px;}"
            "QPushButton:hover{background:#DBEAFE;}"
        )
        btn_csv.setCursor(Qt.PointingHandCursor)
        btn_csv.clicked.connect(self._export_csv)
        bl.addWidget(btn_csv)
        layout.addWidget(bar)

        # ── Table card ────────────────────────────────────────
        # Header strip — warna hijau (tema halaman resep)
        tc = _card()
        tl = QVBoxLayout(tc); tl.setContentsMargins(0,0,0,0); tl.setSpacing(0)

        hdr_strip = QWidget()
        hdr_strip.setStyleSheet("background:#10B981;border-radius:14px 14px 0 0;")
        hs = QHBoxLayout(hdr_strip); hs.setContentsMargins(18,12,18,12)
        hs_lbl = QLabel("📋  Semua Resep")
        hs_lbl.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        hs.addWidget(hs_lbl); hs.addStretch()
        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet("color:rgba(255,255,255,0.75);font-size:12px;background:transparent;")
        hs.addWidget(self.count_lbl)
        tl.addWidget(hdr_strip)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Nama Resep","Kategori","Daerah Asal","Waktu","Porsi","Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 300 if self.is_admin else 185)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setMouseTracking(True)
        self.table.cellClicked.connect(self._cell_clicked)
        self.table.cellEntered.connect(self._cell_hover)
        tl.addWidget(self.table)
        layout.addWidget(tc)

    def _on_sort(self, idx):
        m = [("name","ASC"),("name","DESC"),("cook_time_minutes","ASC"),("cook_time_minutes","DESC")]
        self._sort_col, self._sort_order = m[idx]
        self.refresh()

    def refresh(self):
        recipes = RecipeModel.get_all(
            self.search_edit.text().strip(),
            self.cat_filter.currentData(),
            self._sort_col, self._sort_order
        )
        self._recipes = recipes
        self.table.setRowCount(0)

        for r in recipes:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, val in enumerate([
                r["name"], r.get("category_name",""),
                r.get("origin_region","—"),
                f"{r.get('cook_time_minutes',0)} mnt",
                f"{r.get('servings',1)} porsi"
            ]):
                item = QTableWidgetItem(f"  {val}" if col==0 else val)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                if col in (3,4): item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

            rid = r["id"]
            w = QWidget(); w.setStyleSheet("background:transparent;")
            wl = QHBoxLayout(w); wl.setContentsMargins(8,5,8,5); wl.setSpacing(6)

            def mk(text, style, slot):
                b = QPushButton(text); b.setStyleSheet(style)
                b.setFixedHeight(28); b.setCursor(Qt.PointingHandCursor)
                b.clicked.connect(slot); return b

            wl.addWidget(mk("Detail", S_DETAIL, lambda _, i=rid: self.recipe_selected.emit(i)))
            wl.addWidget(mk("PDF",    S_PDF,    lambda _, i=rid: self._export_pdf(i)))
            if self.is_admin:
                wl.addWidget(mk("Edit",  S_EDIT, lambda _, i=rid: self._edit_recipe(i)))
                wl.addWidget(mk("Hapus", S_DEL,  lambda _, i=rid: self._delete_recipe(i)))
            wl.addStretch()
            self.table.setCellWidget(row, 5, w)
            self.table.setRowHeight(row, 48)

        n = len(recipes)
        self.count_lbl.setText(f"{n} resep ditemukan")

    def _cell_clicked(self, row, col):
        if col == self.table.columnCount()-1: return
        if row < len(self._recipes): self.recipe_selected.emit(self._recipes[row]["id"])

    def _cell_hover(self, row, col):
        cur = Qt.ArrowCursor if col == self.table.columnCount()-1 else Qt.PointingHandCursor
        self.table.viewport().setCursor(cur)

    def _add_recipe(self):
        dlg = RecipeDialog(self)
        if dlg.exec():
            d = dlg.get_data()
            ok, msg = RecipeModel.add(d["name"],d["category_id"],d["origin_region"],
                d["description"],d["cook_time_minutes"],d["servings"],
                self.current_user["id"],d["ingredients"],d["steps"])
            if ok: QMessageBox.information(self,"Berhasil",msg); self.refresh()
            else: QMessageBox.critical(self,"Gagal",msg)

    def _edit_recipe(self, rid):
        r, i, s = RecipeModel.get_by_id(rid)
        if not r: return
        dlg = RecipeDialog(self, r, i, s)
        if dlg.exec():
            d = dlg.get_data()
            ok, msg = RecipeModel.update(rid,d["name"],d["category_id"],d["origin_region"],
                d["description"],d["cook_time_minutes"],d["servings"],d["ingredients"],d["steps"])
            if ok: self.refresh()
            else: QMessageBox.critical(self,"Gagal",msg)

    def _delete_recipe(self, rid):
        r, _, _ = RecipeModel.get_by_id(rid)
        if not r: return
        if QMessageBox.question(self,"Konfirmasi",f"Hapus \"{r['name']}\"?",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            ok, msg = RecipeModel.delete(rid)
            if ok: self.refresh()
            else: QMessageBox.critical(self,"Gagal",msg)

    def _export_csv(self):
        if not self._recipes: QMessageBox.information(self,"Info","Tidak ada data."); return
        path, _ = QFileDialog.getSaveFileName(self,"Simpan CSV","daftar_resep.csv","CSV Files (*.csv)")
        if path:
            ok, r = export_to_csv(self._recipes, path)
            if ok: QMessageBox.information(self,"Berhasil",f"Disimpan:\n{r}")
            else: QMessageBox.critical(self,"Gagal",r)

    def _export_pdf(self, rid):
        r, i, s = RecipeModel.get_by_id(rid)
        if not r: return
        path, _ = QFileDialog.getSaveFileName(self,"Simpan PDF",
            f"{r['name'].replace(' ','_')}.pdf","PDF Files (*.pdf)")
        if path:
            ok, res = export_recipe_to_pdf(r, i, s, path)
            if ok: QMessageBox.information(self,"Berhasil",f"Disimpan:\n{res}")
            else: QMessageBox.critical(self,"Gagal",res)