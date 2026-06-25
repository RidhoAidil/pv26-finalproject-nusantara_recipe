from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from models.models import RecipeModel, CategoryModel


def _shadow(w, blur=18, dy=3, alpha=16):
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(blur); sh.setOffset(0, dy); sh.setColor(QColor(0,0,0,alpha))
    w.setGraphicsEffect(sh)


def _card(bg="#FFFFFF", radius=14):
    f = QFrame()
    f.setStyleSheet(f"QFrame{{background:{bg};border:none;border-radius:{radius}px;}}")
    _shadow(f)
    return f


class StatCard(QFrame):
    """Kartu statistik berwarna penuh — setiap kartu punya tema warna berbeda."""
    def __init__(self, icon, label, value, bg_from, bg_to, text_color="#FFFFFF", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 {bg_from}, stop:1 {bg_to});
                border: none;
                border-radius: 16px;
            }}
        """)
        _shadow(self, blur=22, dy=5, alpha=30)
        self.setMinimumHeight(118)

        ly = QVBoxLayout(self)
        ly.setContentsMargins(22, 18, 22, 18)
        ly.setSpacing(10)

        top = QHBoxLayout()
        self.val_lbl = QLabel(value)
        self.val_lbl.setStyleSheet(f"font-size:36px;font-weight:bold;color:{text_color};background:transparent;")
        top.addWidget(self.val_lbl)
        top.addStretch()

        icon_bg = QFrame()
        icon_bg.setFixedSize(48, 48)
        icon_bg.setStyleSheet("background:rgba(255,255,255,0.22);border-radius:24px;")
        ibl = QVBoxLayout(icon_bg)
        ibl.setContentsMargins(0,0,0,0); ibl.setAlignment(Qt.AlignCenter)
        il = QLabel(icon)
        il.setStyleSheet("font-size:22px;background:transparent;"); il.setAlignment(Qt.AlignCenter)
        ibl.addWidget(il)
        top.addWidget(icon_bg)
        ly.addLayout(top)

        ll = QLabel(label)
        ll.setStyleSheet(f"font-size:12px;color:rgba(255,255,255,0.8);background:transparent;font-weight:600;")
        ly.addWidget(ll)

    def set_value(self, v):
        self.val_lbl.setText(v)


class DashboardPage(QWidget):
    recipe_selected = Signal(int)

    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._recent_recipes = []
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#EEF1F7;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(20)

        # ── Header ────────────────────────────────────────────
        hdr = QHBoxLayout()
        lv = QVBoxLayout(); lv.setSpacing(4)
        title = QLabel("Dashboard")
        title.setStyleSheet("color:#1E2235;font-size:24px;font-weight:bold;")
        sub = QLabel("Ringkasan data resep masakan Nusantara")
        sub.setStyleSheet("color:#64748B;font-size:13px;")
        lv.addWidget(title); lv.addWidget(sub)
        hdr.addLayout(lv); hdr.addStretch()

        greet = QLabel(f"👋  Halo, {self.current_user['username']}!")
        greet.setStyleSheet(
            "background:#DBEAFE;color:#1D4ED8;font-size:13px;font-weight:bold;"
            "border-radius:20px;padding:8px 18px;"
        )
        hdr.addWidget(greet)
        layout.addLayout(hdr)

        # ── Stat cards ────────────────────────────────────────
        row = QHBoxLayout(); row.setSpacing(16)
        self.c_recipes = StatCard("📖","Total Resep Tersedia","0","#2563EB","#1D4ED8")
        self.c_cats    = StatCard("🗂", "Kategori Masakan",   "0","#10B981","#059669")
        self.c_regions = StatCard("📍","Daerah Asal",        "0","#8B5CF6","#7C3AED")
        for c in [self.c_recipes, self.c_cats, self.c_regions]:
            row.addWidget(c)
        layout.addLayout(row)

        # ── Bottom 2 cards ────────────────────────────────────
        bot = QHBoxLayout(); bot.setSpacing(16)

        # Recent recipes — accent biru
        rc = _card()
        rl = QVBoxLayout(rc); rl.setContentsMargins(0,0,0,0); rl.setSpacing(0)

        rh_wrap = QWidget()
        rh_wrap.setStyleSheet("background:#2563EB;border-radius:14px 14px 0 0;")
        rh = QHBoxLayout(rh_wrap); rh.setContentsMargins(18,14,18,14)
        rt = QLabel("📋  Resep Terbaru")
        rt.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        rh.addWidget(rt); rh.addStretch()
        hint = QLabel("Klik baris untuk detail →")
        hint.setStyleSheet("color:rgba(255,255,255,0.65);font-size:11px;background:transparent;")
        rh.addWidget(hint)
        rl.addWidget(rh_wrap)

        self.recent_tbl = QTableWidget(0, 3)
        self.recent_tbl.setHorizontalHeaderLabels(["Nama Resep","Kategori","Tanggal"])
        self.recent_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.recent_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.recent_tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.recent_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_tbl.verticalHeader().setVisible(False)
        self.recent_tbl.setAlternatingRowColors(True)
        self.recent_tbl.setFrameShape(QFrame.NoFrame)
        self.recent_tbl.setMinimumHeight(200)
        self.recent_tbl.setMouseTracking(True)
        self.recent_tbl.cellClicked.connect(self._recent_clicked)
        self.recent_tbl.cellEntered.connect(lambda r,c: self.recent_tbl.viewport().setCursor(Qt.PointingHandCursor))
        rl.addWidget(self.recent_tbl)
        bot.addWidget(rc, 3)

        # Category count — accent hijau
        cc = _card()
        cl = QVBoxLayout(cc); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)

        ch_wrap = QWidget()
        ch_wrap.setStyleSheet("background:#10B981;border-radius:14px 14px 0 0;")
        ch = QHBoxLayout(ch_wrap); ch.setContentsMargins(18,14,18,14)
        ct = QLabel("🗂  Resep per Kategori")
        ct.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        ch.addWidget(ct); ch.addStretch()
        cl.addWidget(ch_wrap)

        self.cat_tbl = QTableWidget(0, 2)
        self.cat_tbl.setHorizontalHeaderLabels(["Kategori","Jumlah"])
        self.cat_tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cat_tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.cat_tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cat_tbl.verticalHeader().setVisible(False)
        self.cat_tbl.setAlternatingRowColors(True)
        self.cat_tbl.setFrameShape(QFrame.NoFrame)
        cl.addWidget(self.cat_tbl)
        bot.addWidget(cc, 2)

        layout.addLayout(bot)

    def refresh(self):
        stats = RecipeModel.get_stats()
        self.c_recipes.set_value(str(stats["total_recipes"]))
        self.c_cats.set_value(str(stats["total_categories"]))
        self.c_regions.set_value(str(stats["total_regions"]))

        self.recent_tbl.setRowCount(0)
        self._recent_recipes = stats["recent"]
        for r in stats["recent"]:
            row = self.recent_tbl.rowCount()
            self.recent_tbl.insertRow(row)
            for col, val in enumerate([r["name"], r.get("category_name",""), r.get("created_at","")[:10]]):
                item = QTableWidgetItem(f"  {val}" if col==0 else val)
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.recent_tbl.setItem(row, col, item)
            self.recent_tbl.setRowHeight(row, 42)

        cat_data = CategoryModel.get_recipe_count_per_category()
        self.cat_tbl.setRowCount(0)
        for r in cat_data:
            row = self.cat_tbl.rowCount()
            self.cat_tbl.insertRow(row)
            self.cat_tbl.setItem(row, 0, QTableWidgetItem(f"  {r['name']}"))
            cnt = QTableWidgetItem(str(r["total"]))
            cnt.setTextAlignment(Qt.AlignCenter)
            if r["total"] > 0:
                cnt.setForeground(QColor("#10B981"))
            self.cat_tbl.setItem(row, 1, cnt)
            self.cat_tbl.setRowHeight(row, 42)

    def _recent_clicked(self, row, col):
        if row < len(self._recent_recipes):
            rid = self._recent_recipes[row].get("id")
            if rid: self.recipe_selected.emit(rid)
