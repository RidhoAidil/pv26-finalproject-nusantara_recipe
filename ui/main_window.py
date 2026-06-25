import os, sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QStackedWidget, QMessageBox, QFrame, QFileDialog,
    QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from ui.dashboard_page import DashboardPage
from ui.recipe_list_page import RecipeListPage
from ui.recipe_detail_page import RecipeDetailPage
from ui.favorites_page import FavoritesPage
from ui.other_pages import ProfilePage, CategoryPage
from ui.recipe_dialog import RecipeDialog
from models.models import RecipeModel

# (key, icon, label, accent_color)
NAV = [
    ("dashboard",  "🏠", "Dashboard",    "#2563EB"),
    ("recipes",    "📋", "Daftar Resep", "#10B981"),
    ("favorites",  "❤",  "Favorit",      "#EF4444"),
    ("profile",    "👤", "Profil Saya",  "#F97316"),
]
ADMIN_NAV = [("categories", "🗂", "Kelola Kategori", "#06B6D4")]


def _shadow(widget, blur=20, offset=(0,4), alpha=18):
    sh = QGraphicsDropShadowEffect()
    sh.setBlurRadius(blur)
    sh.setOffset(*offset)
    sh.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(sh)


class MainWindow(QMainWindow):
    def __init__(self, current_user: dict):
        super().__init__()
        self.current_user = current_user
        self.is_admin = current_user.get("role") == "admin"
        self.setWindowTitle("Nusantara Recipe")
        self.setMinimumSize(1140, 700)
        self._load_styles()
        self._build_menu()
        self._build_ui()
        self._build_statusbar()
        self.showMaximized()

    def _load_styles(self):
        p = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "style.qss"))
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _build_menu(self):
        mb = self.menuBar()
        fm = mb.addMenu("File")
        a = QAction("Export Semua Resep (CSV)", self)
        a.triggered.connect(self._export_csv); fm.addAction(a)
        fm.addSeparator()
        _qa("Logout", fm, self._logout)
        _qa("Keluar", fm, self.close)

        rm = mb.addMenu("Resep")
        _qa("Daftar Resep", rm, lambda: self._show("recipes"))
        _qa("Favorit Saya", rm, lambda: self._show("favorites"))
        if self.is_admin:
            rm.addSeparator()
            _qa("+ Tambah Resep Baru", rm, self._quick_add)

        hm = mb.addMenu("Help")
        _qa("Tentang Aplikasi", hm, self._about)

    def _build_ui(self):
        central = QWidget()
        central.setStyleSheet("background: #EEF1F7;")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────
        sb_frame = QFrame()
        sb_frame.setObjectName("sidebar")
        sb_frame.setFixedWidth(228)
        sb = QVBoxLayout(sb_frame)
        sb.setContentsMargins(0, 0, 0, 0)
        sb.setSpacing(0)

        # Brand
        brand = QWidget()
        brand.setStyleSheet("background: #131929;")
        bl = QVBoxLayout(brand)
        bl.setContentsMargins(20, 22, 20, 18)
        bl.setSpacing(4)
        logo = QLabel("🍛  Nusantara Recipe")
        logo.setStyleSheet("color:#FFFFFF;font-size:16px;font-weight:bold;background:transparent;letter-spacing:0.3px;")
        tagline = QLabel("Warisan Resep Nusantara")
        tagline.setStyleSheet("color:rgba(255,255,255,0.4);font-size:11px;background:transparent;")
        bl.addWidget(logo); bl.addWidget(tagline)
        sb.addWidget(brand)

        # User pill
        user_bar = QWidget()
        user_bar.setStyleSheet("background: #1C2340;")
        ul = QHBoxLayout(user_bar)
        ul.setContentsMargins(16, 12, 16, 12)
        ul.setSpacing(10)

        av_frame = QFrame()
        av_frame.setFixedSize(38, 38)
        av_frame.setStyleSheet("background:#2563EB;border-radius:19px;")
        afl = QVBoxLayout(av_frame)
        afl.setContentsMargins(0,0,0,0)
        afl.setAlignment(Qt.AlignCenter)
        av_lbl = QLabel("👑" if self.is_admin else "👤")
        av_lbl.setStyleSheet("font-size:17px;background:transparent;")
        av_lbl.setAlignment(Qt.AlignCenter)
        afl.addWidget(av_lbl)
        ul.addWidget(av_frame)

        uv = QVBoxLayout(); uv.setSpacing(1)
        uname = QLabel(self.current_user['username'])
        uname.setStyleSheet("font-weight:bold;font-size:13px;color:#FFFFFF;background:transparent;")
        urole = QLabel("Administrator" if self.is_admin else "Pengguna")
        urole.setStyleSheet("font-size:10px;color:#64748B;background:transparent;")
        uv.addWidget(uname); uv.addWidget(urole)
        ul.addLayout(uv, 1)
        sb.addWidget(user_bar)

        sb.addSpacing(12)

        nav_lbl = QLabel("MENU UTAMA")
        nav_lbl.setStyleSheet("color:#3D4A6B;font-size:10px;font-weight:bold;letter-spacing:1.5px;padding:0 18px 6px 18px;background:transparent;")
        sb.addWidget(nav_lbl)

        self._nav_btns = {}
        all_nav = NAV + (ADMIN_NAV if self.is_admin else [])
        for key, icon, label, _ in all_nav:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setCheckable(True)
            btn.setFixedHeight(44)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self._show(k))
            self._nav_btns[key] = btn
            sb.addWidget(btn)

        sb.addStretch()

        # Bottom separator + logout
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setStyleSheet("background:#2D3A57;border:none;max-height:1px;margin:0 14px;")
        sb.addWidget(div)
        sb.addSpacing(6)

        btn_out = QPushButton("  🚪   Keluar / Logout")
        btn_out.setFixedHeight(44)
        btn_out.setCursor(Qt.PointingHandCursor)
        btn_out.setStyleSheet("""
            QPushButton {
                background:transparent;color:#64748B;border:none;
                padding:0 16px;text-align:left;font-size:13px;border-radius:10px;margin:0 10px;
            }
            QPushButton:hover { background:rgba(239,68,68,0.15);color:#F87171; }
        """)
        btn_out.clicked.connect(self._logout)
        sb.addWidget(btn_out)
        sb.addSpacing(10)
        root.addWidget(sb_frame)

        # ── Content ────────────────────────────────────────────
        content = QWidget()
        content.setStyleSheet("background:#EEF1F7;")
        cl = QVBoxLayout(content); cl.setContentsMargins(0,0,0,0); cl.setSpacing(0)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:#EEF1F7;")
        cl.addWidget(self.stack)
        root.addWidget(content, 1)

        self.p_dash   = DashboardPage(self.current_user)
        self.p_list   = RecipeListPage(self.current_user)
        self.p_detail = RecipeDetailPage(self.current_user)
        self.p_fav    = FavoritesPage(self.current_user)
        self.p_prof   = ProfilePage(self.current_user)
        self.p_list.recipe_selected.connect(self._open_detail)
        self.p_fav.recipe_selected.connect(self._open_detail)
        self.p_dash.recipe_selected.connect(self._open_detail)
        self.p_detail.back_requested.connect(lambda: self._show("recipes"))
        self.p_detail.edit_requested.connect(self._edit_from_detail)
        self.p_prof.profile_updated.connect(self._on_profile_updated)
        for p in [self.p_dash, self.p_list, self.p_detail, self.p_fav, self.p_prof]:
            self.stack.addWidget(p)

        self._page_map = {
            "dashboard": self.p_dash, "recipes": self.p_list,
            "detail": self.p_detail,  "favorites": self.p_fav,
            "profile": self.p_prof,
        }
        if self.is_admin:
            self.p_cat = CategoryPage()
            self.stack.addWidget(self.p_cat)
            self._page_map["categories"] = self.p_cat

        self._show("dashboard")

    def _build_statusbar(self):
        sb = self.statusBar()
        lbl = QLabel("Nusantara Recipe  ·  Final Project Pemrograman Visual 2025/2026")
        sb.addPermanentWidget(lbl)

    def _show(self, key: str):
        page = self._page_map.get(key)
        if not page: return
        self.stack.setCurrentWidget(page)
        if key == "dashboard":   self.p_dash.refresh()
        elif key == "recipes":   self.p_list.refresh()
        elif key == "favorites": self.p_fav.refresh()
        for k, btn in self._nav_btns.items():
            btn.setChecked(k == key)

    def _open_detail(self, rid):
        self.p_detail.load_recipe(rid)
        self.stack.setCurrentWidget(self.p_detail)
        for btn in self._nav_btns.values(): btn.setChecked(False)

    def _edit_from_detail(self, rid):
        r, i, s = RecipeModel.get_by_id(rid)
        if not r: return
        dlg = RecipeDialog(self, r, i, s)
        if dlg.exec():
            d = dlg.get_data()
            ok, msg = RecipeModel.update(rid, d["name"], d["category_id"], d["origin_region"],
                d["description"], d["cook_time_minutes"], d["servings"], d["ingredients"], d["steps"])
            if ok: QMessageBox.information(self,"Berhasil",msg); self.p_detail.load_recipe(rid)
            else:  QMessageBox.critical(self,"Gagal",msg)

    def _quick_add(self):
        dlg = RecipeDialog(self)
        if dlg.exec():
            d = dlg.get_data()
            ok, msg = RecipeModel.add(d["name"], d["category_id"], d["origin_region"],
                d["description"], d["cook_time_minutes"], d["servings"],
                self.current_user["id"], d["ingredients"], d["steps"])
            if ok: QMessageBox.information(self,"Berhasil",msg); self._show("recipes")
            else:  QMessageBox.critical(self,"Gagal",msg)

    def _export_csv(self):
        recipes = RecipeModel.get_all()
        if not recipes: QMessageBox.information(self,"Info","Belum ada resep."); return
        path, _ = QFileDialog.getSaveFileName(self,"Simpan CSV","semua_resep.csv","CSV Files (*.csv)")
        if path:
            from utils.export import export_to_csv
            ok, r = export_to_csv(recipes, path)
            if ok: QMessageBox.information(self,"Berhasil",f"Diekspor ke:\n{r}")
            else:  QMessageBox.critical(self,"Gagal",r)

    def _on_profile_updated(self, user):
        self.current_user.update(user)
        self.statusBar().showMessage("✓  Profil berhasil diperbarui.", 3000)

    def _logout(self):
        if QMessageBox.question(self,"Logout","Yakin ingin keluar?",
            QMessageBox.Yes|QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            from ui.login_dialog import LoginDialog
            self.hide()
            login = LoginDialog()
            login.login_success.connect(self._re_login)
            if login.exec() != LoginDialog.Accepted: sys.exit(0)

    def _re_login(self, user):
        w = MainWindow(user); w.show(); self.close()

    def _about(self):
        QMessageBox.about(self, "Tentang Nusantara Recipe",
            "<h3>🍛 Nusantara Recipe</h3>"
            "<p>Aplikasi manajemen resep masakan Indonesia berbasis PySide6.</p>"
            "<p>Final Project — Pemrograman Visual Sem. Genap 2025/2026</p>")


def _qa(label, menu, slot):
    a = QAction(label, menu.parent() if hasattr(menu, 'parent') else None)
    a.triggered.connect(slot)
    menu.addAction(a)
    return a
