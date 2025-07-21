import sys
import os
import re
import ctypes
from ctypes import wintypes
import subprocess
import threading
import json
import requests
import concurrent.futures
import base64
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QScrollArea, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QDialog, QStackedWidget, QStatusBar,
                             QCheckBox, QFrame, QProgressBar, QGraphicsDropShadowEffect,
                             QLineEdit)
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon, QColor, QPainter
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSize, QEvent, QPropertyAnimation, QEasingCurve, QRect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_READER_PATH = os.path.join(BASE_DIR, "bin", "game_reader.exe")
ACHIEVEMENT_FETCHER_PATH = os.path.join(BASE_DIR, "bin", "achievement_fetcher.exe")
STEAM_POPPER_PATH = os.path.join(BASE_DIR, "bin", "steam_popper.exe")
IMAGE_CACHE_DIR = os.path.join(BASE_DIR, "cache", "image_cache")
APP_VALIDATION_CACHE_FILE = os.path.join(BASE_DIR, "cache", "app_validation_cache.json")
CARD_WIDTH = 215
CARD_IMAGE_HEIGHT = int(CARD_WIDTH * 0.46)
CARD_PADDING = 20

# --- ÍCONES SVG (Base64) ---
ICON_ADD_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iMjRweCIgZmlsbD0iI2YwZjBmMCI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0xOSAxM2gtNnY2aC0ydi02SDV2LTJoNlY1aDJ2Nmg2djJ6Ii8+PC9zdmc+"
ICON_CHECK_WHITE_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik05IDE2LjE3TDQuODMgMTJsLTEuNDIgMS40MUw5IDE5IDIxIDdsLTEuNDEtMS40MXoiLz48L3N2Zz4="
ICON_CHECK_GRAY_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzc3NCI+PHBhdGggZD0iTTkgMTYuMTdMNC44MyAxMmwtMS40MiAxLjQxTDkgMTkgMjEgN2wtMS44MS0xLjQxeiIvPjwvc3ZnPg=="
ICON_BACK_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iMjRweCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0yMCAxMUg3LjgzbDUuNTktNS41OUwxMiA0bC04IDggOCA4IDEuNDEtMS40MUw3LjgzIDEzSDIwdi0yeiIvPjwvc3ZnPg=="
ICON_SUCCESS_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iNDhweCIgZmlsbD0iIzI4YTc0NSI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0tMiAxNWwtNS01IDEuNDEtMS40MUwxMCAxNC4xN2w3LjU5LTcuNTlMMTkgOGwtOSA5eiIvPjwvc3ZnPg=="
ICON_INFO_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iNDhweCIgZmlsbD0iIzAwNzhmZiI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0xMSA3aDJ2MmgtMmptMCA0aDJ2NmgtMmptMS05QzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4="
ICON_ERROR_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iMjRweCIgZmlsbD0iI2RjMzk0MCI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0xIDE1aC0ydi0yaDJ2MnptMC00aC0yVjdoMnY2eiIvPjwvc3ZnPg=="
ICON_SEARCH_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDBweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0MHB4IiBmaWxsPSIjZTNlM2UzIj48cGF0aCBkPSJNNzkyLTEyMC42NyA1MzIuNjctMzgwcS0zMCAyNS4zMy02OS42NCAzOS42N1E0MjMuMzktMzI2IDM3OC42Ny0zMjZxLTEwOC40NCAwLTE4My41Ni03NS4xN1ExMjAtNDc2LjMzIDEyMC01ODMuMzN0NzUuMTctMTgyLjE3cTc1LjE2LTc1LjE3IDE4Mi41LTc1LjE3IDEwNy4zMyAwIDE4Mi4xNiA3NS4xNyA3NC44NCA3NS4xNyA3NC44NCAxODIuMjcgMCA0My4yMy0xNCA4Mi45LTE0IDM5LjY2LTQwLjY3IDczbDI2MCAyNTguNjYtNDggNDhabS00MTQtMjcycTc5LjE3IDAgMTM0LjU4LTU1LjgzUTU2OC01MDQuMzMgNTY4LTU4My4zM3EwLTc5LTU1LjQyLTEzNC44NFE0NTcuMTctNzc0IDM3OC03NzRxLTc5LjcyIDAtMTM1LjUzIDU1LjgzLTU1LjggNTUuODQtNTUuOCAxMzQuODR0NTUuOCAxMzQuODNxNTUuODEgNTUuODMgMTM1LjUzIDU1LjgzWiIvPjwvc3ZnPg=="

# --- Estilo (Stylesheet) ---
ESTILO = """
    QMainWindow, QDialog, QScrollArea > QWidget > QWidget {
        background-color: #1e1e1e;
    }
    QWidget {
        color: #e0e0e0;
        font-family: "Segoe UI";
    }
    QScrollArea, QFrame {
        border: none;
        background-color: transparent;
    }
    #GameCard {
        background-color: #2d2d2d;
        border-radius: 8px;
    }
    #GameCard:hover {
        border: 1px solid #0078ff;
    }
    #AchievementCard {
        background-color: #2d2d2d;
        border-radius: 8px;
    }
    #AchievementCard:hover {
        background-color: #3c3c3c;
    }
    QLabel#TitleLabel {
        font-size: 20pt;
        font-weight: bold;
        padding-left: 10px;
    }
    QPushButton {
        background-color: #3c3c3c;
        color: #f0f0f0;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-size: 10pt;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    QPushButton:focus {
        outline: none;
    }
    QPushButton#AccentButton {
        background-color: #0078ff;
        color: white;
    }
    QPushButton#AccentButton:hover {
        background-color: #005fcc;
    }
    QPushButton#ToggleButton {
        border-radius: 6px;
        background-color: #222222;
        border: 1px solid #444;
    }
    QPushButton#ToggleButton:hover {
        background-color: #333333;
        border: 1px solid #555;
    }
    QPushButton#ToggleButton[selected="true"] {
        background-color: #0078ff;
        border: 1px solid #0078ff;
    }
    QPushButton#ToggleButton[achieved="true"] {
        background-color: #2d2d2d;
        border: 1px solid #444;
    }
    QStatusBar {
        font-size: 10pt;
    }
    QProgressBar {
        border: 1px solid #444;
        border-radius: 5px;
        text-align: center;
        color: #e0e0e0;
    }
    QProgressBar::chunk {
        background-color: #0078ff;
        border-radius: 5px;
    }
    QScrollBar:vertical {
        border: none;
        background: #1e1e1e;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #3c3c3c;
        min-height: 25px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #555;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QLineEdit {
        background-color: #2d2d2d;
        border: 1px solid #4a4a4a;
        border-radius: 5px;
        padding: 5px 10px;
        color: #f0f0f0;
        font-size: 10pt;
    }
    QLineEdit:focus {
        border: 1px solid #0078ff;
        outline: none;
    }
"""

class CustomDialog(QDialog):
    def __init__(self, parent, title, message, dialog_type='info'):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(400)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        container = QFrame(self)
        container.setStyleSheet("background-color: rgba(30, 30, 30, 0.98); border-radius: 10px;")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        icon_label = QLabel(self)
        icon_label.setFixedSize(48, 48)
        
        if dialog_type == 'success':
            pixmap = QPixmap(); pixmap.loadFromData(base64.b64decode(ICON_SUCCESS_B64), "svg")
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        elif dialog_type == 'error':
            pixmap = QPixmap(); pixmap.loadFromData(base64.b64decode(ICON_ERROR_B64), "svg")
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            pixmap = QPixmap(); pixmap.loadFromData(base64.b64decode(ICON_INFO_B64), "svg")
            icon_label.setPixmap(pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)

        message_label = QLabel(message, self)
        message_label.setFont(QFont("Segoe UI", 10))
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label, 1, Qt.AlignmentFlag.AlignCenter)

        ok_button = QPushButton("OK", self)
        ok_button.setObjectName("AccentButton")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, 0, Qt.AlignmentFlag.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

# --- Classes de Eventos Customizados ---
class UpdateLoadingEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 1)
    def __init__(self, text, value, maximum): super().__init__(self.TYPE); self.text = text; self.value = value; self.maximum = maximum
class BuildGridEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 2)
    def __init__(self, games): super().__init__(self.TYPE); self.games = games
class ShowAchievementsEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 3)
    def __init__(self, appid): super().__init__(self.TYPE); self.appid = appid
class DisplayAchievementsEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 4)
    def __init__(self, data): super().__init__(self.TYPE); self.data = data
class ShowMessageEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 5)
    def __init__(self, title, message, dialog_type): super().__init__(self.TYPE); self.title = title; self.message = message; self.dialog_type = dialog_type

class SearchLineEdit(QLineEdit):
    def __init__(self, parent=None, search_icon=None):
        super().__init__(parent)
        self.search_icon = search_icon
        self.icon_padding = 10         # Espaçamento entre o ícone e a borda esquerda
        self.text_padding = 5          # Espaçamento do texto em relação ao ícone
        self.setTextMargins(self.icon_padding + 16 + self.text_padding, 0, 0, 0)
        self.setPlaceholderText("Pesquisar conquistas...")

    def paintEvent(self, event):
        # Primeiro, deixa o QLineEdit desenhar a si mesmo
        super().paintEvent(event)

        if self.search_icon:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # tamanho do ícone
            icon_size = 16
            
            # Posição X para o ícone (distância da borda esquerda)
            icon_x = self.icon_padding
            
            # Posição Y para o ícone (centralizado verticalmente)
            icon_y = (self.height() - icon_size) // 2

            # Desenha o ícone
            painter.drawPixmap(icon_x, icon_y, icon_size, icon_size, self.search_icon.pixmap(icon_size, icon_size))

            painter.end()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAO - Steam Achievement Override")
        app_icon_path = os.path.join(BASE_DIR, "src", "icons", "icon.ico")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        self.setGeometry(100, 100, 1024, 400)
        self.setMinimumSize(800, 600)
        self.setStyleSheet(ESTILO)

        self.game_card_map = {}
        self.app_validation_cache = {}
        self.all_games_list = []
        self.currently_displayed_games = []
        self.current_appid = None
        self.current_game_name = ""
        self.achievement_widgets = {}
        self.all_achievements_data = []

        self.load_icons()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.create_loading_panel()
        self.create_games_panel()
        self.create_achievements_panel()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.create_cache_directory()
        self.check_binary_files()
        
        self.start_loading_process()

    def load_icons(self):
        self.icon_add = self.create_icon_from_b64(ICON_ADD_B64)
        self.icon_check_white = self.create_icon_from_b64(ICON_CHECK_WHITE_B64)
        self.icon_check_gray = self.create_icon_from_b64(ICON_CHECK_GRAY_B64)
        self.icon_back = self.create_icon_from_b64(ICON_BACK_B64)
        self.icon_search = self.create_icon_from_b64(ICON_SEARCH_B64)

    def create_icon_from_b64(self, b64_data):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(b64_data), "svg")
        return QIcon(pixmap)

    def create_cache_directory(self):
        if not os.path.exists(IMAGE_CACHE_DIR): os.makedirs(IMAGE_CACHE_DIR)

    def check_binary_files(self):
        for binary in [GAME_READER_PATH, ACHIEVEMENT_FETCHER_PATH, STEAM_POPPER_PATH]:
            if not os.path.exists(binary):
                self.show_custom_message("Erro Crítico", f"Arquivo necessário não encontrado:\n{binary}", "error")
                sys.exit(1)
    
    def create_loading_panel(self):
        self.loading_panel = QWidget()
        main_layout = QVBoxLayout(self.loading_panel)

        # --- Criação do ícone e Canvas (sem alteração) ---
        icon_path = os.path.join(BASE_DIR, "src", "icons", "icon.png")
        original_pixmap = QPixmap(icon_path)
        icon_size = 400
        padding = 30
        canvas_size = icon_size + (padding * 2)
        canvas_pixmap = QPixmap(canvas_size, canvas_size)
        canvas_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(canvas_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        target_rect = QRect(padding, padding, icon_size, icon_size)
        painter.drawPixmap(target_rect, original_pixmap)
        painter.end()
        
        icon_label = QLabel()
        icon_label.setPixmap(canvas_pixmap)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # --- Efeito de Brilho (Glow) ---
        glow_effect = QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(25)
        glow_effect.setOffset(0, 0)
        
        icon_label.setGraphicsEffect(glow_effect)
        
        # --- NOVO: ANIMAÇÃO DO BRILHO PULSANTE ---
        self.glow_animation = QPropertyAnimation(glow_effect, b"color")
        
        # Duração de cada ciclo (ida e volta) em milissegundos
        self.glow_animation.setDuration(2000)
        
        # Cor inicial (azul com baixa opacidade)
        start_color = QColor("#0078ff")
        start_color.setAlpha(100) # Quase invisível
        self.glow_animation.setStartValue(start_color)
        
        # Cor final
        end_color = QColor("#0078ff")
        end_color.setAlpha(255) # Brilho máximo
        self.glow_animation.setKeyValueAt(0.5, end_color)
        
        # Volta para a cor inicial no final
        self.glow_animation.setEndValue(start_color)
        
        # Faz a animação repetir para sempre
        self.glow_animation.setLoopCount(-1)
        
        # Inicia a animação
        self.glow_animation.start()

        # Layout horizontal para o ícone
        icon_layout = QHBoxLayout()
        icon_layout.addStretch(1)
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch(1)

        # Criação dos outros widgets
        self.loading_status_label = QLabel("Buscando jogos instalados...")
        self.loading_status_label.setFont(QFont("Segoe UI", 10))
        self.loading_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.loading_progress_bar = QProgressBar()
        self.loading_progress_bar.setFixedWidth(400)
        self.loading_progress_bar.setTextVisible(False)
        
        progress_bar_layout = QHBoxLayout()
        progress_bar_layout.addStretch(1)
        progress_bar_layout.addWidget(self.loading_progress_bar)
        progress_bar_layout.addStretch(1)

        # Organização do Layout Final
        main_layout.addStretch(1)
        main_layout.addLayout(icon_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.loading_status_label)
        main_layout.addLayout(progress_bar_layout)
        main_layout.addStretch(1)
        
        self.stacked_widget.addWidget(self.loading_panel)

    def create_games_panel(self):
        self.games_panel = QWidget()
        layout = QVBoxLayout(self.games_panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)
        self.grid_layout.setSpacing(CARD_PADDING)
        
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)
        self.stacked_widget.addWidget(self.games_panel)

    def create_achievements_panel(self):
        self.achievements_panel = QWidget()
        main_layout = QVBoxLayout(self.achievements_panel)
        main_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, CARD_PADDING)

        title_bar = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(self.icon_back)
        back_button.setIconSize(QSize(24, 24))
        back_button.setObjectName("AccentButton")
        back_button.setFixedSize(50, 40)
        back_button.clicked.connect(self.show_games_panel)
        
        self.ach_title_label = QLabel("Conquistas")
        self.ach_title_label.setObjectName("TitleLabel")
        
        self.achievement_search_input = SearchLineEdit(self, search_icon=self.icon_search)
        self.achievement_search_input.setFixedHeight(40)
        self.achievement_search_input.setFixedWidth(200)
        self.achievement_search_input.textChanged.connect(self.filter_achievements)

        title_bar.addWidget(back_button)
        title_bar.addWidget(self.ach_title_label)
        title_bar.addStretch(1) 
        title_bar.addWidget(self.achievement_search_input) 
        
        main_layout.addLayout(title_bar)


        ach_scroll = QScrollArea()
        ach_scroll.setWidgetResizable(True)
        ach_scroll.setFrameShape(QFrame.Shape.NoFrame)
        ach_scroll_content = QWidget()
        self.ach_list_layout = QVBoxLayout(ach_scroll_content)
        self.ach_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ach_list_layout.setSpacing(10)
        ach_scroll.setWidget(ach_scroll_content)
        main_layout.addWidget(ach_scroll)

        self.unlock_button = QPushButton("Desbloquear Conquistas Selecionadas")
        self.unlock_button.setObjectName("AccentButton")
        self.unlock_button.setFixedHeight(40)
        self.unlock_button.clicked.connect(self.unlock_selected_achievements)
        main_layout.addWidget(self.unlock_button)
        
        self.stacked_widget.addWidget(self.achievements_panel)

    def start_loading_process(self):
        self.stacked_widget.setCurrentWidget(self.loading_panel)
        self.worker_thread = threading.Thread(target=self._master_loader_thread, daemon=True)
        self.worker_thread.start()

    def build_grid(self, games_list):
        self.currently_displayed_games = games_list
        
        for i in reversed(range(self.grid_layout.count())): 
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        self.game_card_map.clear()

        width = self.scroll_area.viewport().width()
        num_columns = max(1, (width - CARD_PADDING) // (CARD_WIDTH + CARD_PADDING))

        for i, game in enumerate(games_list):
            row, col = i // num_columns, i % num_columns
            card = self.create_game_card(game)
            self.grid_layout.addWidget(card, row, col, Qt.AlignmentFlag.AlignTop)
        
        for i in range(self.grid_layout.columnCount()):
            self.grid_layout.setColumnStretch(i, 0)
        for i in range(self.grid_layout.rowCount()):
            self.grid_layout.setRowStretch(i, 0)

        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)
        self.grid_layout.setColumnStretch(num_columns, 1)

    def create_game_card(self, game):
        appid, name = game['appid'], game['name']
        card = QFrame()
        card.setObjectName("GameCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(8)
        
        image_label = QLabel()
        image_label.setFixedSize(CARD_WIDTH, CARD_IMAGE_HEIGHT)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("background-color: #3c3c3c; border-radius: 4px;")
        
        path = os.path.join(IMAGE_CACHE_DIR, f"{appid}.jpg")
        if os.path.exists(path):
            pixmap = QPixmap(path)
            image_label.setPixmap(pixmap.scaled(CARD_WIDTH, CARD_IMAGE_HEIGHT, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        else:
            image_label.setText("Sem Imagem")

        display_name = name if len(name) <= 35 else name[:32] + "..."
        title_label = QLabel(display_name)
        title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        card_layout.addWidget(image_label)
        card_layout.addWidget(title_label)
        
        card.mousePressEvent = lambda event, a=appid, n=name: self.on_game_select(a, n)
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        return card

    def on_game_select(self, appid, game_name):
        self.current_appid = appid
        self.current_game_name = game_name
        appid_str = str(appid)

        if appid_str in self.app_validation_cache:
            if self.app_validation_cache[appid_str]:
                self._show_achievements_for_valid_game()
            else:
                self.show_custom_message("Informação", "Este aplicativo não possui conquistas na Steam.", "info")
        else:
            self.status_bar.showMessage(f"Verificando conquistas para {game_name}...")
            threading.Thread(target=self._check_and_display_achievements_worker, args=(appid,), daemon=True).start()

    def show_custom_message(self, title, message, dialog_type='info'):
        dialog = CustomDialog(self, title, message, dialog_type)
        dialog.exec()

    def resizeEvent(self, event):
        if self.stacked_widget.currentWidget() == self.games_panel:
            self.build_grid(self.currently_displayed_games)
        super().resizeEvent(event)

    def _master_loader_thread(self):
        try:
            QApplication.instance().postEvent(self, UpdateLoadingEvent("Buscando jogos instalados...", 0, 0))
            bin_dir = os.path.dirname(GAME_READER_PATH)
            result = subprocess.run([GAME_READER_PATH], capture_output=True, text=True, check=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW, cwd=bin_dir)
            games_dict = {int(m.group(2)): m.group(1).strip() for line in result.stdout.splitlines() if (m := re.match(r'^(.*) \(AppID: (\d+)\)$', line.strip()))}
            self.all_games_list = sorted([{'appid': appid, 'name': name} for appid, name in games_dict.items()], key=lambda g: g['name'])

            appids_with_images = self._fetch_all_images_parallel(self.all_games_list)
            games_to_display = [game for game in self.all_games_list if game['appid'] in appids_with_images]

            QApplication.instance().postEvent(self, BuildGridEvent(games_to_display))
            self._background_validation_worker(games_to_display)
        except Exception as e:
            print(f"Erro Crítico no Carregamento: {e}")
            QApplication.instance().postEvent(self, ShowMessageEvent("Erro Crítico", f"Falha ao carregar a lista de jogos:\n{e}", "error"))

    def _fetch_all_images_parallel(self, games_to_fetch):
        total = len(games_to_fetch)
        QApplication.instance().postEvent(self, UpdateLoadingEvent(f"Baixando 0/{total} imagens...", 0, total))
        
        appids_with_images = set()
        
        def check_and_download(appid, index):
            path = os.path.join(IMAGE_CACHE_DIR, f"{appid}.jpg")
            if os.path.exists(path):
                appids_with_images.add(appid)
            else:
                try:
                    r = requests.get(f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg", timeout=5)
                    if r.status_code == 200:
                        with open(path, 'wb') as f: f.write(r.content)
                        appids_with_images.add(appid)
                except: pass
            
            QApplication.instance().postEvent(self, UpdateLoadingEvent(f"Baixando {index + 1}/{total} imagens...", index + 1, total))

        with concurrent.futures.ThreadPoolExecutor(max_workers=(os.cpu_count() or 1) * 2) as executor:
            list(executor.map(check_and_download, [g['appid'] for g in games_to_fetch], range(total)))
        
        return appids_with_images

    def _background_validation_worker(self, games_list):
        if os.path.exists(APP_VALIDATION_CACHE_FILE):
            try:
                with open(APP_VALIDATION_CACHE_FILE, 'r') as f: self.app_validation_cache = json.load(f)
            except: pass
        for i, game in enumerate(games_list):
            appid_str = str(game['appid'])
            self.status_bar.showMessage(f"Validando: {i+1}/{len(games_list)} - {game['name'][:20]}...")
            if appid_str not in self.app_validation_cache:
                try:
                    subprocess.run([ACHIEVEMENT_FETCHER_PATH, appid_str], capture_output=True, text=True, check=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
                    self.app_validation_cache[appid_str] = True
                except subprocess.CalledProcessError: self.app_validation_cache[appid_str] = False
        with open(APP_VALIDATION_CACHE_FILE, 'w') as f: json.dump(self.app_validation_cache, f)
        self.status_bar.showMessage("Pronto.", 5000)

    def _check_and_display_achievements_worker(self, appid):
        try:
            subprocess.run([ACHIEVEMENT_FETCHER_PATH, str(appid)], capture_output=True, text=True, check=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            QApplication.instance().postEvent(self, ShowAchievementsEvent(appid))
        except subprocess.CalledProcessError:
            QApplication.instance().postEvent(self, ShowMessageEvent("Informação", "Este aplicativo não possui conquistas na Steam.", "info"))
        except Exception as e:
            QApplication.instance().postEvent(self, ShowMessageEvent("Erro", f"Ocorreu um erro inesperado:\n{e}", "error"))

    def _show_achievements_for_valid_game(self):
        self.status_bar.showMessage(f"Buscando conquistas para {self.current_game_name}...")
        self.ach_title_label.setText(self.current_game_name)
        self.stacked_widget.setCurrentWidget(self.achievements_panel)

        self.achievement_search_input.clear() 

        for i in reversed(range(self.ach_list_layout.count())): 
            widget = self.ach_list_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None) # Remove o widget da interface
        self.achievement_widgets.clear() # Limpa o dicionário de referência dos widgets
        self.all_achievements_data = [] # Limpa a lista de dados para evitar reuso de dados antigos


        threading.Thread(target=self.fetch_achievements_worker, args=(self.current_appid,), daemon=True).start()

    def fetch_achievements_worker(self, appid):
        try:
            result = subprocess.run([ACHIEVEMENT_FETCHER_PATH, str(appid)], capture_output=True, text=True, check=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            data = json.loads(result.stdout)
            # Armazena todos os dados das conquistas para futura filtragem
            self.all_achievements_data = sorted(data, key=lambda x: x['isAchieved']) 
            QApplication.instance().postEvent(self, DisplayAchievementsEvent(data))
        except Exception as e:
            QApplication.instance().postEvent(self, ShowMessageEvent("Erro", f"Falha ao buscar detalhes das conquistas:\n{e}", "error"))

    def display_achievements(self, achievements_to_display):
        # Limpa o layout existente
        for i in reversed(range(self.ach_list_layout.count())): 
            self.ach_list_layout.itemAt(i).widget().setParent(None)
        self.achievement_widgets.clear()

        if not achievements_to_display:
            self.unlock_button.hide()
            self.ach_list_layout.addWidget(QLabel("Nenhuma conquista encontrada com os critérios de busca."), alignment=Qt.AlignmentFlag.AlignCenter)
            return

        self.unlock_button.show()
        for ach in achievements_to_display:
            widget = self.create_achievement_widget(ach)
            self.ach_list_layout.addWidget(widget)

    def create_achievement_widget(self, ach_data):
        widget = QFrame(); widget.setObjectName("AchievementCard")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 10, 15, 10)
        
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        icon_label.setStyleSheet("background-color: #444; border-radius: 4px;")
        if 'icon_base64' in ach_data and ach_data['icon_base64']:
            try:
                icon_data = base64.b64decode(ach_data['icon_base64'])
                side = int(math.sqrt(len(icon_data) / 4))
                if side * side * 4 == len(icon_data):
                    q_image = QImage(icon_data, side, side, QImage.Format.Format_RGBA8888)
                    pixmap = QPixmap.fromImage(q_image)
                    icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            except Exception as e:
                print(f"Erro ao processar ícone: {e}")

        toggle_button = QPushButton()
        toggle_button.setObjectName("ToggleButton")
        toggle_button.setFixedSize(36, 36)
        toggle_button.setIconSize(QSize(24, 24))
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        name_label = QLabel(ach_data['name']); name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        desc_label = QLabel(ach_data['description']); desc_label.setWordWrap(True)
        text_layout.addWidget(name_label); text_layout.addWidget(desc_label)
        
        api_name = ach_data['apiName']
        is_achieved = ach_data['isAchieved']
        
        self.achievement_widgets[api_name] = {'selected': False, 'initial_state': is_achieved, 'button': toggle_button, 'name': ach_data['name']}

        def update_visual_state():
            data = self.achievement_widgets[api_name]
            if is_achieved:
                toggle_button.setIcon(self.icon_check_gray)
                toggle_button.setProperty("achieved", True)
                toggle_button.setEnabled(False)
            elif data['selected']:
                toggle_button.setIcon(self.icon_check_white)
                toggle_button.setProperty("selected", True)
            else:
                toggle_button.setIcon(self.icon_add)
                toggle_button.setProperty("selected", False)
            
            toggle_button.style().unpolish(toggle_button)
            toggle_button.style().polish(toggle_button)

        def toggle_selection():
            if not is_achieved:
                data = self.achievement_widgets[api_name]
                data['selected'] = not data['selected']
                update_visual_state()

        toggle_button.clicked.connect(toggle_selection)
        update_visual_state()

        layout.addWidget(icon_label)
        layout.addSpacing(15)
        layout.addWidget(toggle_button)
        layout.addSpacing(15)
        layout.addLayout(text_layout, 1)
        return widget

    def filter_achievements(self, text):
        search_text = text.lower()
        if not search_text:
            # Se a caixa de pesquisa estiver vazia, exibe todas as conquistas
            self.display_achievements(self.all_achievements_data)
        else:
            # Filtra as conquistas cujo nome contém o texto da pesquisa
            filtered_achievements = [
                ach for ach in self.all_achievements_data 
                if search_text in ach['name'].lower()
            ]
            self.display_achievements(filtered_achievements)

    def unlock_selected_achievements(self):
        to_unlock = [name for name, data in self.achievement_widgets.items() if data['selected'] and not data['initial_state']]
        if not to_unlock:
            self.show_custom_message("Info", "Nenhuma nova conquista foi selecionada.", "info")
            return
        try:
            command = [STEAM_POPPER_PATH, str(self.current_appid)] + to_unlock
            subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW)
            self.show_custom_message("Sucesso", "Conquista(s) desbloqueada(s) com sucesso!", "success")
            # Recarrega as conquistas para atualizar os estados
            self._show_achievements_for_valid_game() 
        except Exception as e:
            self.show_custom_message("Erro", f"Falha ao executar o desbloqueador: {e}", "error")

    def show_games_panel(self):
        self.stacked_widget.setCurrentWidget(self.games_panel)
        self.status_bar.showMessage("Pronto.", 3000)

    def customEvent(self, event):
        if event.type() == UpdateLoadingEvent.TYPE:
            self.loading_status_label.setText(event.text)
            self.loading_progress_bar.setMaximum(event.maximum)
            self.loading_progress_bar.setValue(event.value)
        elif event.type() == BuildGridEvent.TYPE:
            self.currently_displayed_games = event.games # Guarda a lista de jogos
            self.stacked_widget.setCurrentWidget(self.games_panel) # 1. Mostra a tela primeiro
            self.build_grid(event.games) # 2. Desenha a grade DEPOIS
            self.status_bar.show()
        elif event.type() == ShowAchievementsEvent.TYPE: self._show_achievements_for_valid_game()
        elif event.type() == DisplayAchievementsEvent.TYPE: 
            self.all_achievements_data = sorted(event.data, key=lambda x: x['isAchieved']) 
            self.display_achievements(self.all_achievements_data) 
        elif event.type() == ShowMessageEvent.TYPE:
            self.show_custom_message(event.title, event.message, event.dialog_type)
            self.status_bar.showMessage("Pronto.", 3000)

if __name__ == '__main__':

    myappid = u'sao.override.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())