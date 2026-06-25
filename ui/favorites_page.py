from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QFrame,
    QAbstractItemView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from models.models import FavoriteModel


def _shadow(w, blur=18, dy=3, alpha=16):
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(blur); sh.setOffset(0, dy); sh.setColor(QColor(0,0,0,alpha))
    w.setGraphicsEffect(sh)


def _card(bg="#FFFFFF", radius=14):
    f = QFrame()
    f.setStyleSheet(f"QFrame{{background:{bg};border:none;border-radius:{radius}px;}}")
    _shadow(f)
    return f


S_DETAIL = "QPushButton{background:#DBEAFE;color:#1D4ED8;border:none;border-radius:6px;padding:3px 12px;font-size:11px;font-weight:bold;min-height:28px;}QPushButton:hover{background:#BFDBFE;}"
S_REMOVE = "QPushButton{background:#FEE2E2;color:#991B1B;border:none;border-radius:6px;padding:3px 12px;font-size:11px;font-weight:bold;min-height:28px;}QPushButton:hover{background:#FECACA;}"


class FavoritesPage(QWidget):
    recipe_selected = Signal(int)

    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._favs = []
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#EEF1F7;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        lv = QVBoxLayout(); lv.setSpacing(4)
        title = QLabel("Resep Favorit")
        title.setStyleSheet("color:#1E2235;font-size:24px;font-weight:bold;")
        sub = QLabel("Resep masakan yang sudah kamu simpan ❤")
        sub.setStyleSheet("color:#64748B;font-size:13px;")
        lv.addWidget(title); lv.addWidget(sub)
        hdr.addLayout(lv); hdr.addStretch()
        layout.addLayout(hdr)

        # Empty state card
        self.empty_card = _card("#FFFFFF")
        self.empty_card.setMinimumHeight(340)
        el = QVBoxLayout(self.empty_card)
        el.setAlignment(Qt.AlignCenter); el.setSpacing(16)

        heart_outer = QFrame()
        heart_outer.setFixedSize(96, 96)
        heart_outer.setStyleSheet("QFrame{background:#FEE2E2;border-radius:48px;border:none;}")
        hcl = QVBoxLayout(heart_outer)
        hcl.setContentsMargins(0,0,0,0); hcl.setAlignment(Qt.AlignCenter)
        heart = QLabel("🤍")
        heart.setStyleSheet("font-size:42px;background:transparent;")
        heart.setAlignment(Qt.AlignCenter)
        hcl.addWidget(heart)
        el.addWidget(heart_outer, alignment=Qt.AlignCenter)

        e_title = QLabel("Belum ada resep favorit")
        e_title.setStyleSheet("color:#1E2235;font-size:17px;font-weight:bold;background:transparent;")
        e_title.setAlignment(Qt.AlignCenter)

        e_sub = QLabel("Buka halaman Detail Resep, lalu klik tombol\n♡ Favorit untuk menyimpan resep ke sini.")
        e_sub.setStyleSheet("color:#94A3B8;font-size:13px;background:transparent;")
        e_sub.setAlignment(Qt.AlignCenter)

        el.addWidget(e_title); el.addWidget(e_sub)
        layout.addWidget(self.empty_card)

        # Table card
        self.table_card = _card()
        tl = QVBoxLayout(self.table_card); tl.setContentsMargins(0,0,0,0); tl.setSpacing(0)

        hdr_strip = QWidget()
        hdr_strip.setStyleSheet("background:#EF4444;border-radius:14px 14px 0 0;")
        hs = QHBoxLayout(hdr_strip); hs.setContentsMargins(18,13,18,13)
        hs_lbl = QLabel("❤  Resep Favorit Saya")
        hs_lbl.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        hs.addWidget(hs_lbl); hs.addStretch()
        self.count_lbl = QLabel("")
        self.count_lbl.setStyleSheet("color:rgba(255,255,255,0.75);font-size:12px;background:transparent;")
        hs.addWidget(self.count_lbl)
        tl.addWidget(hdr_strip)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["  Nama Resep","Kategori","Daerah Asal","Waktu","Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 195)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setMouseTracking(True)
        self.table.cellClicked.connect(self._cell_clicked)
        self.table.cellEntered.connect(self._cell_hover)
        tl.addWidget(self.table)
        layout.addWidget(self.table_card)
        self.table_card.hide()

    def refresh(self):
        favs = FavoriteModel.get_user_favorites(self.current_user["id"])
        self._favs = favs

        if not favs:
            self.empty_card.show(); self.table_card.hide()
            return

        self.empty_card.hide(); self.table_card.show()
        self.table.setRowCount(0)

        for r in favs:
            row = self.table.rowCount()
            self.table.insertRow(row)

            ni = QTableWidgetItem(f"  {r['name']}")
            ni.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 0, ni)

            for col, key in [(1,"category_name"),(2,"origin_region")]:
                item = QTableWidgetItem(r.get(key,"—"))
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(row, col, item)

            t = QTableWidgetItem(f"{r.get('cook_time_minutes',0)} mnt")
            t.setTextAlignment(Qt.AlignCenter)
            t.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 3, t)

            rid = r["id"]
            w = QWidget(); w.setStyleSheet("background:transparent;")
            wl = QHBoxLayout(w); wl.setContentsMargins(8,6,8,6); wl.setSpacing(8)

            bd = QPushButton("Detail"); bd.setStyleSheet(S_DETAIL)
            bd.setFixedHeight(28); bd.setCursor(Qt.PointingHandCursor)
            bd.clicked.connect(lambda _, i=rid: self.recipe_selected.emit(i))

            br = QPushButton("✕  Hapus"); br.setStyleSheet(S_REMOVE)
            br.setFixedHeight(28); br.setCursor(Qt.PointingHandCursor)
            br.clicked.connect(lambda _, i=rid: self._remove(i))

            wl.addWidget(bd); wl.addWidget(br); wl.addStretch()
            self.table.setCellWidget(row, 4, w)
            self.table.setRowHeight(row, 48)

        self.count_lbl.setText(f"{len(favs)} resep tersimpan")

    def _cell_clicked(self, row, col):
        if col == self.table.columnCount()-1: return
        if row < len(self._favs): self.recipe_selected.emit(self._favs[row]["id"])

    def _cell_hover(self, row, col):
        cur = Qt.ArrowCursor if col == self.table.columnCount()-1 else Qt.PointingHandCursor
        self.table.viewport().setCursor(cur)

    def _remove(self, recipe_id):
        FavoriteModel.toggle(self.current_user["id"], recipe_id)
        self.refresh()
