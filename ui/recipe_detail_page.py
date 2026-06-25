from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QFileDialog, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from models.models import RecipeModel, FavoriteModel
from utils.export import export_recipe_to_pdf


def _shadow(w, blur=18, dy=3, alpha=16):
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(blur); sh.setOffset(0, dy); sh.setColor(QColor(0,0,0,alpha))
    w.setGraphicsEffect(sh)


def _card(bg="#FFFFFF", radius=14):
    f = QFrame()
    f.setStyleSheet(f"QFrame{{background:{bg};border:none;border-radius:{radius}px;}}")
    _shadow(f)
    return f


class RecipeDetailPage(QWidget):
    back_requested = Signal()
    edit_requested = Signal(int)

    def __init__(self, current_user: dict, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self.is_admin = current_user.get("role") == "admin"
        self.recipe_id = None
        self.recipe = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background:#EEF1F7;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Top bar (ungu — tema detail resep) ────────────────
        topbar = QWidget()
        topbar.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #8B5CF6,stop:1 #6D28D9);"
        )
        topbar.setFixedHeight(60)
        top = QHBoxLayout(topbar)
        top.setContentsMargins(24, 0, 24, 0); top.setSpacing(10)

        btn_back = QPushButton("←  Kembali")
        btn_back.setFixedHeight(36)
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.18);color:#FFFFFF;border:none;"
            "border-radius:8px;font-weight:bold;padding:0 16px;}"
            "QPushButton:hover{background:rgba(255,255,255,0.28);}"
        )
        btn_back.clicked.connect(self.back_requested.emit)
        top.addWidget(btn_back)
        top.addStretch()

        self.btn_fav = QPushButton("♡  Favorit")
        self.btn_fav.setFixedHeight(36)
        self.btn_fav.setCursor(Qt.PointingHandCursor)
        self.btn_fav.setStyleSheet(
            "QPushButton{background:rgba(255,255,255,0.18);color:#FFFFFF;border:none;"
            "border-radius:8px;font-weight:bold;padding:0 16px;}"
            "QPushButton:hover{background:rgba(239,68,68,0.5);}"
        )
        self.btn_fav.clicked.connect(self._toggle_favorite)
        top.addWidget(self.btn_fav)

        btn_pdf = QPushButton("📄  Export PDF")
        btn_pdf.setFixedHeight(36)
        btn_pdf.setCursor(Qt.PointingHandCursor)
        btn_pdf.setStyleSheet(
            "QPushButton{background:#10B981;color:#FFF;border:none;"
            "border-radius:8px;font-weight:bold;padding:0 16px;}"
            "QPushButton:hover{background:#059669;}"
        )
        btn_pdf.clicked.connect(self._export_pdf)
        top.addWidget(btn_pdf)

        if self.is_admin:
            btn_edit = QPushButton("✏  Edit")
            btn_edit.setFixedHeight(36)
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setStyleSheet(
                "QPushButton{background:#F59E0B;color:#FFF;border:none;"
                "border-radius:8px;font-weight:bold;padding:0 16px;}"
                "QPushButton:hover{background:#D97706;}"
            )
            btn_edit.clicked.connect(self._edit)
            top.addWidget(btn_edit)

            btn_del = QPushButton("🗑  Hapus")
            btn_del.setFixedHeight(36)
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setStyleSheet(
                "QPushButton{background:#EF4444;color:#FFF;border:none;"
                "border-radius:8px;font-weight:bold;padding:0 16px;}"
                "QPushButton:hover{background:#DC2626;}"
            )
            btn_del.clicked.connect(self._delete)
            top.addWidget(btn_del)

        layout.addWidget(topbar)

        # ── Scrollable body ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setStyleSheet("background:#EEF1F7;")
        body = QWidget(); body.setStyleSheet("background:#EEF1F7;")
        self.content_layout = QVBoxLayout(body)
        self.content_layout.setContentsMargins(28, 24, 28, 28)
        self.content_layout.setSpacing(16)
        scroll.setWidget(body)
        layout.addWidget(scroll)

        # ── Hero card (judul + badge info) ────────────────────
        self.hero = _card("#FFFFFF")
        hl = QVBoxLayout(self.hero)
        hl.setContentsMargins(0, 0, 0, 0); hl.setSpacing(0)

        hero_top = QWidget()
        hero_top.setStyleSheet("background:#8B5CF6;border-radius:14px 14px 0 0;")
        ht = QVBoxLayout(hero_top)
        ht.setContentsMargins(22, 20, 22, 18); ht.setSpacing(10)

        self.title_label = QLabel("Pilih resep untuk melihat detail")
        self.title_label.setStyleSheet("color:#FFFFFF;font-size:22px;font-weight:bold;background:transparent;")
        self.title_label.setWordWrap(True)
        ht.addWidget(self.title_label)

        self.meta_row = QHBoxLayout(); self.meta_row.setSpacing(10)
        ht.addLayout(self.meta_row)
        hl.addWidget(hero_top)
        self.content_layout.addWidget(self.hero)

        # ── Dua kolom: kiri (deskripsi + bahan) | kanan (langkah) ──
        cols = QHBoxLayout(); cols.setSpacing(16)

        # Kolom kiri
        left = QVBoxLayout(); left.setSpacing(16)

        # Deskripsi — biru muda
        desc_card = _card()
        dl = QVBoxLayout(desc_card); dl.setContentsMargins(0,0,0,0); dl.setSpacing(0)
        dh = QWidget(); dh.setStyleSheet("background:#2563EB;border-radius:14px 14px 0 0;")
        dhl = QHBoxLayout(dh); dhl.setContentsMargins(18,12,18,12)
        dh_lbl = QLabel("📝  Deskripsi"); dh_lbl.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        dhl.addWidget(dh_lbl)
        dl.addWidget(dh)
        self.desc_label = QLabel("")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color:#334155;font-size:13px;line-height:1.7;padding:16px 20px;background:transparent;")
        dl.addWidget(self.desc_label)
        left.addWidget(desc_card)

        # Bahan — hijau teal
        ing_card = _card()
        il = QVBoxLayout(ing_card); il.setContentsMargins(0,0,0,0); il.setSpacing(0)
        ih = QWidget(); ih.setStyleSheet("background:#0D9488;border-radius:14px 14px 0 0;")
        ihl = QHBoxLayout(ih); ihl.setContentsMargins(18,12,18,12)
        ih_lbl = QLabel("🥬  Bahan-Bahan"); ih_lbl.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        ihl.addWidget(ih_lbl)
        il.addWidget(ih)

        self.ing_table = QTableWidget(0, 3)
        self.ing_table.setHorizontalHeaderLabels(["Bahan","Jumlah","Satuan"])
        self.ing_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ing_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.ing_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.ing_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.ing_table.verticalHeader().setVisible(False)
        self.ing_table.setAlternatingRowColors(True)
        self.ing_table.setMaximumHeight(250)
        self.ing_table.setFrameShape(QFrame.NoFrame)
        il.addWidget(self.ing_table)
        left.addWidget(ing_card)
        left.addStretch()
        cols.addLayout(left, 1)

        # Kolom kanan — langkah: oranye
        steps_card = _card()
        sl = QVBoxLayout(steps_card); sl.setContentsMargins(0,0,0,0); sl.setSpacing(0)
        sh_w = QWidget(); sh_w.setStyleSheet("background:#F97316;border-radius:14px 14px 0 0;")
        shl = QHBoxLayout(sh_w); shl.setContentsMargins(18,12,18,12)
        sh_lbl = QLabel("👨‍🍳  Cara Memasak"); sh_lbl.setStyleSheet("font-weight:bold;color:#FFFFFF;font-size:14px;background:transparent;")
        shl.addWidget(sh_lbl)
        sl.addWidget(sh_w)

        steps_body = QWidget(); steps_body.setStyleSheet("background:#FFFFFF;border-radius:0 0 14px 14px;")
        self.steps_container = QVBoxLayout(steps_body)
        self.steps_container.setContentsMargins(16, 14, 16, 16)
        self.steps_container.setSpacing(10)
        sl.addWidget(steps_body)
        cols.addWidget(steps_card, 1)

        self.content_layout.addLayout(cols)
        self.content_layout.addStretch()

    def _badge(self, icon, text, color, bg):
        lbl = QLabel(f"{icon}  {text}")
        lbl.setStyleSheet(
            f"background:{bg};color:{color};font-size:12px;font-weight:bold;"
            f"border-radius:12px;padding:5px 14px;"
        )
        return lbl

    def load_recipe(self, recipe_id: int):
        self.recipe_id = recipe_id
        recipe, ingredients, steps = RecipeModel.get_by_id(recipe_id)
        if not recipe: return
        self.recipe = recipe
        self.ingredients = ingredients
        self.steps = steps

        self.title_label.setText(recipe["name"])

        # Badge info
        while self.meta_row.count():
            item = self.meta_row.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        badges = [
            ("📂", recipe.get("category_name","-"), "#1D4ED8", "#DBEAFE"),
            ("📍", recipe.get("origin_region","-"),  "#065F46", "#D1FAE5"),
            ("⏱",  f"{recipe.get('cook_time_minutes',0)} menit", "#92400E", "#FEF3C7"),
            ("🍽",  f"{recipe.get('servings',1)} porsi",          "#6D28D9", "#EDE9FE"),
        ]
        for icon, text, color, bg in badges:
            self.meta_row.addWidget(self._badge(icon, text, color, bg))
        self.meta_row.addStretch()

        # Deskripsi
        self.desc_label.setText(recipe.get("description") or "Tidak ada deskripsi.")

        # Bahan
        self.ing_table.setRowCount(0)
        for ing in ingredients:
            row = self.ing_table.rowCount()
            self.ing_table.insertRow(row)
            self.ing_table.setItem(row, 0, QTableWidgetItem(f"  {ing['name']}"))
            amt = QTableWidgetItem(ing.get("amount",""))
            amt.setTextAlignment(Qt.AlignCenter)
            self.ing_table.setItem(row, 1, amt)
            unit = QTableWidgetItem(ing.get("unit",""))
            unit.setTextAlignment(Qt.AlignCenter)
            self.ing_table.setItem(row, 2, unit)
            self.ing_table.setRowHeight(row, 40)

        # Langkah
        while self.steps_container.count():
            item = self.steps_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        STEP_COLORS = ["#F97316","#8B5CF6","#2563EB","#10B981","#EF4444","#0D9488","#F59E0B"]
        for s in steps:
            color = STEP_COLORS[(s['step_no']-1) % len(STEP_COLORS)]
            sf = QFrame()
            sf.setStyleSheet(
                f"QFrame{{background:#FFF8F5;border-left:4px solid {color};"
                f"border-radius:8px;}}"
            )
            sfl = QHBoxLayout(sf); sfl.setContentsMargins(12,10,12,10); sfl.setSpacing(12)

            nc = QFrame(); nc.setFixedSize(28,28)
            nc.setStyleSheet(f"background:{color};border-radius:14px;")
            nci = QVBoxLayout(nc); nci.setContentsMargins(0,0,0,0); nci.setAlignment(Qt.AlignCenter)
            nl = QLabel(str(s['step_no']))
            nl.setAlignment(Qt.AlignCenter)
            nl.setStyleSheet("color:#FFFFFF;font-weight:bold;font-size:12px;background:transparent;")
            nci.addWidget(nl)

            inst = QLabel(s["instruction"])
            inst.setWordWrap(True)
            inst.setStyleSheet("color:#1E2235;font-size:13px;line-height:1.6;background:transparent;")
            sfl.addWidget(nc); sfl.addWidget(inst, 1)
            self.steps_container.addWidget(sf)

        # Favorit
        is_fav = FavoriteModel.is_favorite(self.current_user["id"], recipe_id)
        self._update_fav_btn(is_fav)

    def _update_fav_btn(self, is_fav):
        if is_fav:
            self.btn_fav.setText("❤  Favorit")
            self.btn_fav.setStyleSheet(
                "QPushButton{background:#EF4444;color:#FFF;border:none;"
                "border-radius:8px;font-weight:bold;padding:0 16px;}"
                "QPushButton:hover{background:#DC2626;}"
            )
        else:
            self.btn_fav.setText("♡  Favorit")
            self.btn_fav.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.18);color:#FFFFFF;border:none;"
                "border-radius:8px;font-weight:bold;padding:0 16px;}"
                "QPushButton:hover{background:rgba(239,68,68,0.5);}"
            )

    def _toggle_favorite(self):
        if not self.recipe_id: return
        FavoriteModel.toggle(self.current_user["id"], self.recipe_id)
        is_fav = FavoriteModel.is_favorite(self.current_user["id"], self.recipe_id)
        self._update_fav_btn(is_fav)

    def _export_pdf(self):
        if not self.recipe: return
        safe = self.recipe["name"].replace(" ","_").replace("/","-")
        path, _ = QFileDialog.getSaveFileName(self,"Simpan PDF",f"{safe}.pdf","PDF Files (*.pdf)")
        if path:
            ok, r = export_recipe_to_pdf(self.recipe, self.ingredients, self.steps, path)
            if ok: QMessageBox.information(self,"Berhasil",f"PDF disimpan:\n{r}")
            else: QMessageBox.critical(self,"Gagal",r)

    def _edit(self):
        if self.recipe_id: self.edit_requested.emit(self.recipe_id)

    def _delete(self):
        if not self.recipe: return
        if QMessageBox.question(self,"Konfirmasi",f"Hapus \"{self.recipe['name']}\"?",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            ok, msg = RecipeModel.delete(self.recipe_id)
            if ok: self.back_requested.emit()
            else: QMessageBox.critical(self,"Gagal",msg)
