from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal
from models.models import UserModel

FIELD = """
QLineEdit {
    background: #F8FAFF;
    border: 2px solid #E2E8F0;
    border-radius: 9px;
    padding: 11px 14px;
    font-size: 13px;
    color: #1E2235;
}
QLineEdit:focus { border-color: #2563EB; background: #FFFFFF; }
QLineEdit:hover { border-color: #94A3B8; }
"""

BTN_BLUE = """
QPushButton {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    border-radius: 9px;
    font-size: 14px;
    font-weight: bold;
    padding: 0;
}
QPushButton:hover   { background-color: #1D4ED8; }
QPushButton:pressed { background-color: #1E3A8A; }
"""


class LoginDialog(QDialog):
    login_success = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nusantara Recipe")
        self.setFixedSize(440, 590)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Hero header — gradient biru ungu
        header = QFrame()
        header.setStyleSheet(
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #1C2340,stop:0.5 #2563EB,stop:1 #8B5CF6);"
        )
        header.setFixedHeight(200)
        hl = QVBoxLayout(header)
        hl.setContentsMargins(0, 36, 0, 28)
        hl.setSpacing(8); hl.setAlignment(Qt.AlignCenter)

        logo = QLabel("🍛")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size:56px;background:transparent;")
        hl.addWidget(logo)

        app_name = QLabel("Nusantara Recipe")
        app_name.setAlignment(Qt.AlignCenter)
        app_name.setStyleSheet("color:#FFFFFF;font-size:22px;font-weight:bold;background:transparent;letter-spacing:0.5px;")
        hl.addWidget(app_name)

        tagline = QLabel("Warisan Resep Masakan Indonesia")
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet("color:rgba(255,255,255,0.55);font-size:12px;background:transparent;")
        hl.addWidget(tagline)
        root.addWidget(header)

        # White body
        body = QFrame()
        body.setStyleSheet("background:#FFFFFF;")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(32, 0, 32, 32)
        bl.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border:none; background:#FFFFFF; }
            QTabBar           { background:#FFFFFF; }
            QTabBar::tab {
                background:#EEF1F7; color:#64748B;
                border:none;
                padding:10px 28px; font-size:13px; font-weight:bold;
                border-radius:8px 8px 0 0; margin-right:3px;
            }
            QTabBar::tab:selected { background:#FFFFFF; color:#2563EB; }
            QTabBar::tab:hover:!selected { background:#E2E8F0; color:#334155; }
        """)
        self.tabs.addTab(self._login_tab(), "  Masuk  ")
        self.tabs.addTab(self._register_tab(), "  Daftar  ")
        bl.addWidget(self.tabs)
        root.addWidget(body)

    def _field(self, placeholder, echo=None):
        f = QLineEdit()
        f.setPlaceholderText(placeholder)
        f.setMinimumHeight(46)
        f.setStyleSheet(FIELD)
        if echo: f.setEchoMode(echo)
        return f

    def _login_tab(self):
        w = QWidget(); w.setStyleSheet("background:#FFFFFF;")
        ly = QVBoxLayout(w); ly.setSpacing(12); ly.setContentsMargins(0, 22, 0, 0)

        lbl = QLabel("Masuk ke akun Anda")
        lbl.setStyleSheet("color:#1E2235;font-size:16px;font-weight:bold;background:transparent;")
        ly.addWidget(lbl)

        self.login_username = self._field("👤  Username")
        self.login_password = self._field("🔒  Password", QLineEdit.Password)
        self.login_password.returnPressed.connect(self._do_login)
        ly.addWidget(self.login_username)
        ly.addWidget(self.login_password)

        ly.addSpacing(8)
        btn = QPushButton("Masuk")
        btn.setMinimumHeight(48); btn.setStyleSheet(BTN_BLUE)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._do_login)
        ly.addWidget(btn); ly.addStretch()
        return w

    def _register_tab(self):
        w = QWidget(); w.setStyleSheet("background:#FFFFFF;")
        ly = QVBoxLayout(w); ly.setSpacing(10); ly.setContentsMargins(0, 22, 0, 0)

        lbl = QLabel("Buat akun baru")
        lbl.setStyleSheet("color:#1E2235;font-size:16px;font-weight:bold;background:transparent;")
        ly.addWidget(lbl)

        self.reg_username = self._field("👤  Username (min. 3 karakter)")
        self.reg_email    = self._field("✉  Email")
        self.reg_password = self._field("🔒  Password (min. 6 karakter)", QLineEdit.Password)
        self.reg_confirm  = self._field("🔒  Konfirmasi Password", QLineEdit.Password)
        for f in [self.reg_username, self.reg_email, self.reg_password, self.reg_confirm]:
            ly.addWidget(f)

        btn = QPushButton("Daftar Sekarang")
        btn.setMinimumHeight(48); btn.setStyleSheet(BTN_BLUE)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self._do_register)
        ly.addWidget(btn); ly.addStretch()
        return w

    def _do_login(self):
        u = self.login_username.text().strip()
        p = self.login_password.text()
        if not u or not p:
            QMessageBox.warning(self,"Peringatan","Username dan password wajib diisi."); return
        user = UserModel.login(u, p)
        if user:
            self.login_success.emit(user); self.accept()
        else:
            QMessageBox.critical(self,"Gagal","Username atau password salah.")
            self.login_password.clear(); self.login_password.setFocus()

    def _do_register(self):
        u = self.reg_username.text().strip()
        e = self.reg_email.text().strip()
        p = self.reg_password.text()
        c = self.reg_confirm.text()
        if not u or not e or not p or not c:
            QMessageBox.warning(self,"Peringatan","Semua field wajib diisi."); return
        if len(u) < 3:
            QMessageBox.warning(self,"Peringatan","Username minimal 3 karakter."); return
        if "@" not in e:
            QMessageBox.warning(self,"Peringatan","Format email tidak valid."); return
        if len(p) < 6:
            QMessageBox.warning(self,"Peringatan","Password minimal 6 karakter."); return
        if p != c:
            QMessageBox.warning(self,"Peringatan","Konfirmasi password tidak cocok."); return
        ok, msg = UserModel.register(u, p, e)
        if ok:
            QMessageBox.information(self,"Berhasil",msg+"\nSilakan masuk.")
            self.tabs.setCurrentIndex(0)
            for f in [self.reg_username, self.reg_email, self.reg_password, self.reg_confirm]:
                f.clear()
        else:
            QMessageBox.critical(self,"Gagal",f"Registrasi gagal:\n{msg}")
