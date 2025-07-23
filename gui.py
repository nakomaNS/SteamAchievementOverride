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
import datetime
import time

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, 
                             QScrollArea, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QDialog, QStackedWidget, QStatusBar,
                             QCheckBox, QFrame, QProgressBar, QGraphicsDropShadowEffect,
                             QLineEdit, QRadioButton, QButtonGroup)
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon, QColor, QPainter
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QSize, QEvent, QPropertyAnimation, QRect

if getattr(sys, 'frozen', False):
    GLOBAL_BASE_DIR = os.path.dirname(sys.executable)
    GLOBAL_PACKAGED_RESOURCES_PATH = sys._MEIPASS
else:
    GLOBAL_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    GLOBAL_PACKAGED_RESOURCES_PATH = os.path.dirname(os.path.abspath(__file__))

CARD_WIDTH = 215
CARD_IMAGE_HEIGHT = int(CARD_WIDTH * 0.46)
CARD_PADDING = 20


ICON_ADD_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iMjRweCIgZmlsbD0iI2YwZjBmMCI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0xOSAxM2gtNnY2aC0ydi02SDV2LTJoNlY1aDJ2Nmg2djJ6Ii8+PC9zdmc+"
ICON_CHECK_WHITE_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik05IDE2LjE3TDQuODMgMTJsLTEuNDIgMS40MUw5IDE5IDIxIDdsLTEuNDEtMS40MXoiLz48L3N2Zz4="
ICON_CHECK_GRAY_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzc3NCI+PHBhdGggZD0iTTkgMTYuMTdMNC44MyAxMmwtMS40MiAxLjQxTDkgMTkgMjEgN2wtMS44MS0xLjQxeiIvPjwvc3ZnPg=="
ICON_BACK_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iMjRweCIgZmlsbD0iI0ZGRkZGRiI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0yMCAxMUg3LjgzbDUuNTktNS41OUwxMiA0bC04IDggOCA4IDEuNDEtMS40MUw3LjgzIDEzSDIwdi0yeiIvPjwvc3ZnPg=="
ICON_SUCCESS_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0OHB4IiBmaWxsPSIjRkZGRkZGIj48cGF0aCBkPSJNMjk0LTI0MiA3MC00NjZsNDMtNDMgMTgxIDE4MSA0MyA0My00MyA0M1ptMTcwIDBMMjQwLTQ2Nmw0My00MyAxODEgMTgxIDM4NC0zODQgNDMgNDMtNDI3IDQyN1ptMC0xNzAtNDMtNDMgMjU3LTI1NyA0MyA0My0yNTcgMjU3WiIvPjwvc3ZnPg=="
ICON_INFO_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAwIDI0IDI0IiB3aWR0aD0iNDhweCIgZmlsbD0iIzAwNzhmZiI+PHBhdGggZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSIvPjxwYXRoIGQ9Ik0xMSA3aDJ2MmgtMmptMCA0aDJ2NmgtMmptMS05QzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Z34="
ICON_ERROR_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0OHB4IiBmaWxsPSIjRkZGRkZGIj48cGF0aCBkPSJtMjQ5LTIwNy00Mi00MiAyMzEtMjMxLTIzMS0yMzEgNDItNDIgMjMxIDIzMSAyMzEtMjMxIDQyIDQyLTIzMSAyMzEgMjMxIDIzMS00MiA0Mi0yMzEtMjMxLTIzMSAyMzFaIi8+PC9zdmc+"
ICON_SEARCH_DARK_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDBweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0MHB4IiBmaWxsPSIjZTNlM2UzIj48cGF0aCBkPSJNNzkyLTEyMC42NyA1MzIuNjctMzgwcS0zMCAyNS4zMy02OS42NCAzOS42N1E0MjMuMzktMzI2IDM3OC42Ny0zMjZxLTEwOC40NCAwLTE4My41Ni03NS4xN1ExMjAtNDc2LjMzIDEyMC01ODMuMzN0NzUuMTctMTgyLjE3cTc1LjE2LTc1LjE3IDE4Mi41LTc1LjE3IDEwNy4zMyAwIDE4Mi4xNiA3NS4xNyA3NC44NCA3NS4xNyA3NC44NCAxODIuMjcgMCA0My4yMy0xNCA4Mi45LTE0IDM5LjY2LTQwLjY3IDczbDI2MCAyNTguNjYtNDggNDhabS00MTQtMjcycTc5LjE3IDAgMTM0LjU4LTU1LjgzUTU2OC01MDQuMzMgNTY4LTU4My4zM3EwLTc5LTU1LjQyLTEzNC44NFE0NTcuMTctNzc0IDM3OC03NzRxLTc5LjcyIDAtMTM1LjUzIDU1LjgzLTU1LjggNTUuODQtNTUuOCAxMzQuODR0NTUuOCAxMzQuODNxNTUuODEgNTUuODMgMTM1LjUzIDU1LjgzWiIvPjwvc3ZnPg=="
ICON_SEARCH_LIGHT_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0OHB4IiBmaWxsPSIjMDAwMDAwIj48cGF0aCBkPSJNNzk2LTEyMSA1MzMtMzg0cS0zMCAyNi02OS45NiA0MC41UTQyMy4wOC0zMjkgMzc4LTMyOXEtMTA4LjE2IDAtMTgzLjA4LTc1UTEyMC00NzkgMTIwLTU4NXQ3NS0xODFxNzUtNzUgMTgxLjUtNzV0MTgxIDc1UTYzMi02OTEgNjMyLTU4NC44NSA2MzItNTQyIDYxOC01MDJxLTE0IDQwLTQyIDc1bDI2NCAyNjItNDQgNDRaTTM3Ny0zODlxODEuMjUgMCAxMzguMTMtNTcuNVE1NzItNTA0IDU3Mi01ODV0LTU2Ljg3LTEzOC41UTQ1OC4yNS03ODEgMzc3LTc4MXEtODIuMDggMC0xMzkuNTQgNTcuNVExODAtNjY2IDE4MC01ODV0NTcuNDYgMTM4LjVRMjk0LjkyLTM4OSAzNzctMzg5WiIvPjwvc3ZnPg=="
ICON_SETTINGS_DARK_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0OHB4IiBmaWxsPSIjZTNlM2UzIj48cGF0aCBkPSJtMzg4LTgwLTIwLTEyNnEtMTktNy00MC0xOXQtMzctMjVsLTExOCA1NC05My0xNjQgMTA4LTc5cS0yLTktMi41LTIwLjVUMTg1LTQ4MHEwLTktLjUtMjAuNVQxODgtNTUxTDgwLTYwMGw5My0xNjQgMTE4IDU0cTE2LTEzIDM3LTI1dDQwLTE4bDIwLTEyN2gxODRsMjAgMTI2cTE5IDcgNDAuNSAxOC41VDY2OS03MTBsMTE4LTU0IDkzIDE2NC0xMDggNzdxMiAxMCAyLjUgMjEuNXQuNSAyMS41cTAgMTAtLjUgMjF0LTIuNSAyMWwxMDggNzgtOTMgMTY0LTExOC01NHEtMTYgMTMtMzYuNSAyNS41VDU5Mi0yMDZMNTcyLTgwSDM4OFptNDgtNjhoODhsMTQtMTEycTMzLTggNjIuNS0yNXQ1My41LTQxbDEwNiA0NiA0MC03Mi05NC02OXE0LTE3IDYuNS0zMy41VDcxNS00ODBxMC0xNy0yLTMzLjV0LTctMzMuNWw5NC02OS00MC03Mi0xMDYgNDZxLTIzLTI2LTUyLTQzLjVUNTM4LTcwOGwtMTQtMTEyaC04OGwtMTQgMTEycS0zNCA3LTYzLjUgMjRUMzA2LTY0MmwtMTA2LTQ2LTQwIDcyIDk0IDY5cS00IDE3LTYuNSAzMy41VDI0NS00ODBxMCAxNyAyLjUgMzMuNVQyNTQtNDEzbC05NCA2OSA0MCA3MiAxMDYtNDZxMjQgMjQgNTMuNSA0MXQ2Mi41IDI1bDE0IDExMlptNDQtMjEwcTU0IDAgOTItMzh0MzgtOTJxMC01NC0zOC05MnQtOTItMzhxLTU0IDAtOTIgMzh0LTM4IDkycTAgNTQgMzggOTJ0OTIgMzhabTAtMTMwWiIvPjwvc3ZnPg=="
ICON_SETTINGS_LIGHT_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iNDhweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSI0OHB4IiBmaWxsPSIjMDAwMDAwIj48cGF0aCBkPSJtMzg4LTgwLTIwLTEyNnEtMTktNy00MC0xOXQtMzctMjVsLTExOCA1NC05My0xNjQgMTA4LTc5cS0yLTktMi41LTIwLjVUMTg1LTQ4MHEwLTkgLjUtMjAuNVQxODgtNTIxTDgwLTYwMGw5My0xNjQgMTE4IDU0cTE2LTEzIDM3LTI1dDQwLTE4bDIwLTEyN2gxODRsMjAgMTI2cTE5IDcgNDAuNSAxOC41VDY2OS03MTBsMTE4LTU0IDkzIDE2NC0xMDggNzdxMiAxMCAyLjUgMjEuNXQuNSAyMS41cTAgMTAtLjUgMjF0LTIuNSAyMWwxMDggNzgtOTMgMTY0LTExOC01NHEtMTYgMTMtMzYuNSAyNS41VDU5Mi0yMDZMNTcyLTgwSDM4OFptNDgtNjBoODhsMTQtMTEycTMzLTggNjIuNS0yNXQ1My41LTQxbDEwNiA0NiA0MC03Mi05NC02OXE0LTE3IDYuNS0zMy41VDcxNS00ODBxMC0xNy0yLTMzLjV0LTctMzMuNWw5NC02OS00MC03Mi0xMDYgNDZxLTIzLTI2LTUyLTQzLjVUNTM4LTcwOGwtMTQtMTEyaC04OGwtMTQgMTEycS0zNCA3LTYzLjUgMjRUMzA2LTY0MmwtMTA2LTQ2LTQwIDcyIDk0IDY5cS00IDE3LTYuNSAzMy41VDI0NS00ODBxMCAxNyAyLjUgMzMuNVQyNTQtNDEzbC05NCA2OSA0MCA3MiAxMDYtNDZxMjQgMjQgNTMuNSA0MXQ2Mi41IDI1bDE0IDExMlptNDQtMjEwcTU0IDAgOTItMzh0MzgtOTJxMC01NC0zOC05MnQtOTItMzhxLTU0IDAtOTIgMzh0LTM4IDkycTAgNTQgMzggOTJ0OTIgMzhabTAtMTMwWiIvPjwvc3ZnPg=="

ESTILO_DARK = """
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
        min-height: 25px;
        padding: 0px 5px;
        border-bottom: none;
    }
    QStatusBar QLabel {
        padding: 0px;
        margin: 0px;
    }
    QStatusBar QProgressBar {
        height: 15px;
        margin: 0px;
        padding: 0px;
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
        width: 4px;
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

ESTILO_LIGHT = """
    QMainWindow, QDialog, QScrollArea > QWidget > QWidget {
        background-color: #f0f0f0;
    }
    QWidget {
        color: #1e1e1e;
        font-family: "Segoe UI";
    }
    QScrollArea, QFrame {
        border: none;
        background-color: transparent;
    }
    #GameCard {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    #GameCard:hover {
        border: 1px solid #0078ff;
    }
    #AchievementCard {
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    #AchievementCard:hover {
        background-color: #f5f5f5;
    }
    QLabel#TitleLabel {
        font-size: 20pt;
        font-weight: bold;
        padding-left: 10px;
    }
    QPushButton {
        background-color: #e0e0e0;
        color: #1e1e1e;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-size: 10pt;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
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
        background-color: #f0f0f0;
        border: 1px solid #ccc;
    }
    QPushButton#ToggleButton:hover {
        background-color: #e5e5e5;
        border: 1px solid #bbb;
    }
    QPushButton#ToggleButton[selected="true"] {
        background-color: #0078ff;
        border: 1px solid #0078ff;
    }
    QPushButton#ToggleButton[achieved="true"] {
        background-color: #e0e0e0;
        border: 1px solid #ccc;
    }
    QStatusBar {
        font-size: 10pt;
    }
    QProgressBar {
        border: 1px solid #ccc;
        border-radius: 5px;
        text-align: center;
        color: #1e1e1e;
    }
    QProgressBar::chunk {
        background-color: #0078ff;
        border-radius: 5px;
    }
    QScrollBar:vertical {
        border: none;
        background: #f0f0f0;
        width: 4px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background: #c0c0c0;
        min-height: 25px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical:hover {
        background: #a0a0a0;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 5px 10px;
        color: #1e1e1e;
        font-size: 10pt;
    }
    QLineEdit:focus {
        border: 1px solid #0078ff;
        outline: none;
    }
"""

TRANSLATIONS = {
    'pt': {
        'app_title': "SAO - Steam Achievement Override",
        'loading_games': "Buscando jogos instalados...",
        'fetching_achievements_data': "Buscando dados das conquistas...",
        'downloading_images': "Baixando {}/{} imagens...",
        'ready': "Pronto.",
        'critical_error': "Erro Crítico",
        'failed_load_games': "Falha ao carregar a lista de jogos:\n{}",
        'info': "Informação",
        'no_achievements': "Este aplicativo não possui conquistas na Steam.",
        'unexpected_error': "Ocorreu um erro inesperado:\n{}",
        'fetching_achievements': "Buscando conquistas para {}...",
        'achievements_title': "Conquistas",
        'failed_fetch_achievements': "Falha ao buscar detalhes das conquistas:\n{}",
        'no_achievements_found_search': "Nenhuma conquista encontrada com os critérios de busca.",
        'unlock_selected': "Desbloquear Conquistas Selecionadas",
        'no_new_achievements_selected': "Nenhuma nova conquista foi selecionada.",
        'success': "Sucesso",
        'achievements_unlocked_success': "Conquista(s) desbloqueada(s) com sucesso!",
        'error': "Erro",
        'failed_unlocker': "Falha ao executar o desbloqueador: {}",
        'search_placeholder_games': "Pesquisar jogos...",
        'search_placeholder_achievements': "Pesquisar conquistas...",
        'settings_title': "Configurações",
        'language_settings': "Idioma:",
        'portuguese': "Português",
        'english': "English",
        'theme_settings': "Tema:",
        'dark_mode': "Modo Escuro",
        'light_mode': "Modo Claro",
        'apply': "Aplicar",
        'cancel': "Cancelar",
        'required_file_missing': "Arquivo necessário não encontrado:\n{}",
        'unlocked_on_date': "Desbloqueada em: {}", 
        'not_unlocked': "Não desbloqueada",   
        'date_format': "%d/%m/%Y %H:%M",
        'no_image': "Sem Imagem",
        'unlocking_achievements_message': "Desbloqueando conquistas...",
        'validating_simple': "Validando..."
    },
    'en': {
        'app_title': "SAO - Steam Achievement Override",
        'loading_games': "Searching for installed games...",
        'fetching_achievements_data': "Fetching achievement data...",
        'downloading_images': "Downloading {}/{} images...",
        'ready': "Ready.",
        'critical_error': "Critical Error",
        'failed_load_games': "Failed to load game list:\n{}",
        'info': "Information",
        'no_achievements': "This application has no achievements on Steam.",
        'unexpected_error': "An unexpected error occurred:\n{}",
        'fetching_achievements': "Fetching achievements for {}...",
        'achievements_title': "Achievements",
        'failed_fetch_achievements': "Failed to fetch achievement details:\n{}",
        'no_achievements_found_search': "No achievements found matching search criteria.",
        'unlock_selected': "Unlock Selected Achievements",
        'no_new_achievements_selected': "No new achievements selected.",
        'success': "Success",
        'achievements_unlocked_success': "Achievement(s) unlocked successfully!",
        'error': "Error",
        'failed_unlocker': "Failed to execute unlocker: {}",
        'search_placeholder_games': "Search games...",
        'search_placeholder_achievements': "Search achievements...",
        'settings_title': "Settings",
        'language_settings': "Language:",
        'portuguese': "Portuguese",
        'english': "English",
        'theme_settings': "Theme:",
        'dark_mode': "Dark Mode",
        'light_mode': "Light Mode",
        'apply': "Apply",
        'cancel': "Cancel",
        'required_file_missing': "Required file not found:\n{}",
        'unlocked_on_date': "Unlocked on: {}", 
        'not_unlocked': "Not unlocked",   
        'date_format': "%m/%d/%Y %H:%M",
        'no_image': "No Image",
        'unlocking_achievements_message': "Unlocking achievements...",
        'validating_simple': "Validating..."
    }
}

class UnlockProcessCompletedEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 6)
    def __init__(self, success_title_key, success_message_key, success_dialog_type, success_args, error_title_key, error_message_key, error_dialog_type, error_args, appid_to_refresh):
        super().__init__(self.TYPE)
        self.success_title_key = success_title_key
        self.success_message_key = success_message_key
        self.success_dialog_type = success_dialog_type
        self.success_args = success_args
        self.error_title_key = error_title_key
        self.error_message_key = error_message_key
        self.error_dialog_type = error_dialog_type
        self.error_args = error_args
        self.appid_to_refresh = appid_to_refresh

class AchievementValidationCompletedEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 7)
    def __init__(self, appid, has_achievements, error_message=None):
        super().__init__(self.TYPE)
        self.appid = appid
        self.has_achievements = has_achievements
        self.error_message = error_message

class CustomDialog(QDialog):
    def __init__(self, parent, title_key, message_content_string, dialog_type='info'):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle(self.parent_app.tr(title_key))
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        container = QFrame(self)
        container.setStyleSheet("background-color: rgba(30, 30, 30, 0.98); border-radius: 10px;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 25, 20, 20)
        layout.setSpacing(15)
        message_to_display = message_content_string
        if dialog_type == 'success':
            message_to_display = "Sucesso!"
        elif dialog_type == 'error':
            icon_label = QLabel(self)
            icon_label.setFixedSize(32, 32)
            pixmap_error = QPixmap()
            pixmap_error.loadFromData(base64.b64decode(ICON_ERROR_B64), "svg")
            icon_label.setPixmap(pixmap_error.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        else:
            icon_label = QLabel(self)
            icon_label.setFixedSize(32, 32)
            pixmap_info = QPixmap()
            pixmap_info.loadFromData(base64.b64decode(ICON_INFO_B64), "svg")
            icon_label.setPixmap(pixmap_info.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        message_label = QLabel(message_to_display, self)
        message_label.setFont(QFont("Segoe UI", 11))
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        layout.addStretch(1)
        ok_button = QPushButton("OK", self)
        ok_button.setObjectName("AccentButton")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedSize(80, 31)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(120)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.updateGeometry()

class UpdateLoadingEvent(QEvent):
    TYPE = QEvent.Type(QEvent.Type.User + 1)
    def __init__(self, text_key, value, maximum, *args):
        super().__init__(self.TYPE)
        self.text_key = text_key
        self.value = value
        self.maximum = maximum
        self.args = args

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
    def __init__(self, title_key, message_key, dialog_type, *args):
        super().__init__(self.TYPE)
        self.title_key = title_key
        self.message_key = message_key
        self.dialog_type = dialog_type
        self.args = args

class SearchLineEdit(QLineEdit):
    def __init__(self, parent=None, search_icon=None, placeholder_key=""):
        super().__init__(parent)
        self._search_icon = search_icon
        self.icon_padding = 10
        self.icon_size = 16
        self.text_start_offset = self.icon_padding + self.icon_size + 5
        self.placeholder_key = placeholder_key
        self.setTextMargins(self.text_start_offset, 0, 0, 0)

    def set_search_icon(self, icon):
        self._search_icon = icon
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._search_icon:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            icon_x = self.icon_padding
            icon_y = (self.height() - self.icon_size) // 2
            painter.drawPixmap(icon_x, icon_y, self.icon_size, self.icon_size,
                               self._search_icon.pixmap(self.icon_size, self.icon_size))
            painter.end()

class SettingsDialog(QDialog):
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, parent_app, current_lang, current_theme):
        super().__init__(parent_app)
        self.parent_app = parent_app
        self.setWindowTitle(self.parent_app.tr('settings_title'))
        self.setModal(True)
        self.setFixedSize(385, 285)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        lang_group_box = QVBoxLayout()
        lang_label = QLabel(self.parent_app.tr('language_settings'))
        lang_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lang_group_box.addWidget(lang_label)
        self.lang_group = QButtonGroup(self)
        self.radio_pt = QRadioButton(self.parent_app.tr('portuguese'))
        self.radio_pt.setChecked(current_lang == 'pt')
        self.lang_group.addButton(self.radio_pt, 0)
        lang_group_box.addWidget(self.radio_pt)
        self.radio_en = QRadioButton(self.parent_app.tr('english'))
        self.radio_en.setChecked(current_lang == 'en')
        self.lang_group.addButton(self.radio_en, 1)
        lang_group_box.addWidget(self.radio_en)
        main_layout.addLayout(lang_group_box)
        theme_group_box = QVBoxLayout()
        theme_label = QLabel(self.parent_app.tr('theme_settings'))
        theme_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        theme_group_box.addWidget(theme_label)
        self.theme_group = QButtonGroup(self)
        self.radio_dark = QRadioButton(self.parent_app.tr('dark_mode'))
        self.radio_dark.setChecked(current_theme == 'dark')
        self.theme_group.addButton(self.radio_dark, 0)
        theme_group_box.addWidget(self.radio_dark)
        self.radio_light = QRadioButton(self.parent_app.tr('light_mode'))
        self.radio_light.setChecked(current_theme == 'light')
        self.theme_group.addButton(self.radio_light, 1)
        theme_group_box.addWidget(self.radio_light)
        main_layout.addLayout(theme_group_box)
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        cancel_button = QPushButton(self.parent_app.tr('cancel'))
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        apply_button = QPushButton(self.parent_app.tr('apply'))
        apply_button.setObjectName("AccentButton")
        apply_button.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_button)
        main_layout.addLayout(button_layout)

    def apply_settings(self):
        if self.radio_pt.isChecked():
            self.language_changed.emit('pt')
        elif self.radio_en.isChecked():
            self.language_changed.emit('en')
        if self.radio_dark.isChecked():
            self.theme_changed.emit('dark')
        elif self.radio_light.isChecked():
            self.theme_changed.emit('light')
        self.accept()

class CustomStatusBar(QStatusBar):
    def __init__(self, parent=None, preferred_height=20):
        super().__init__(parent)
        self.preferred_height = preferred_height

    def sizeHint(self):
        return QSize(super().sizeHint().width(), self.preferred_height)

    def minimumSizeHint(self):
        return QSize(super().minimumSizeHint().width(), self.preferred_height)

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self._BASE_DIR = GLOBAL_BASE_DIR
        self._PACKAGED_RESOURCES_PATH = GLOBAL_PACKAGED_RESOURCES_PATH
        
        self.GAME_READER_PATH = os.path.join(self._PACKAGED_RESOURCES_PATH, "bin", "game_reader.exe")
        self.ACHIEVEMENT_FETCHER_PATH = os.path.join(self._PACKAGED_RESOURCES_PATH, "bin", "achievement_fetcher.exe")
        self.STEAM_POPPER_PATH = os.path.join(self._PACKAGED_RESOURCES_PATH, "bin", "steam_popper.exe")

        self.IMAGE_CACHE_DIR = os.path.join(self._BASE_DIR, "cache", "image_cache")
        self.APP_VALIDATION_CACHE_FILE = os.path.join(self._BASE_DIR, "cache", "app_validation_cache.json")
        self.SETTINGS_FILE = os.path.join(self._BASE_DIR, "cache", "settings.json")
        self.ACHIEVEMENT_DATA_CACHE_DIR = os.path.join(self._BASE_DIR, "cache", "achievements")

        self.current_language = 'pt'
        self.current_theme = 'dark'
        self.translations = TRANSLATIONS

        self.load_icons()
        self.load_settings()
        self.apply_theme(self.current_theme)

        self.setWindowTitle(self.tr('app_title'))
        app_icon_path = os.path.join(self._PACKAGED_RESOURCES_PATH, "src", "icons", "icon.ico")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        self.setGeometry(100, 100, 1280, 800)
        self.setMinimumSize(800, 600)

        self.game_card_map = {}
        self.app_validation_cache = {}
        self.all_games_list = []
        self.currently_displayed_games = []
        self.current_appid = None
        self.current_game_name = ""
        self.achievement_widgets = {}
        self.all_achievements_data = []

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.create_games_panel()
        
        self.apply_theme(self.current_theme)

        self.create_loading_panel()
        self.create_achievements_panel()

        self.status_bar = CustomStatusBar(self, preferred_height=20)
        self.setStatusBar(self.status_bar)

        self.status_content_widget = QWidget()
        status_layout = QHBoxLayout(self.status_content_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(10)
        
        self.status_message_label = QLabel(self.tr('ready'))
        status_layout.addWidget(self.status_message_label, 1)

        self.status_progress_bar = QProgressBar()
        self.status_progress_bar.setFixedWidth(150)
        self.status_progress_bar.setFixedHeight(15)
        self.status_progress_bar.setTextVisible(False)
        self.status_progress_bar.hide()
        status_layout.addWidget(self.status_progress_bar)
        
        self.status_bar.addWidget(self.status_content_widget, 1)

        self.create_cache_directory()
        self.check_binary_files()
        
        self.update_ui_texts()
        self.start_loading_process()

    def load_icons(self):
        self.icon_add = self.create_icon_from_b64(ICON_ADD_B64)
        self.icon_check_white = self.create_icon_from_b64(ICON_CHECK_WHITE_B64)
        self.icon_check_gray = self.create_icon_from_b64(ICON_CHECK_GRAY_B64)
        self.icon_back = self.create_icon_from_b64(ICON_BACK_B64)
        self.icon_search = self.create_icon_from_b64(ICON_SEARCH_DARK_B64)

    def create_icon_from_b64(self, b64_data):
        pixmap = QPixmap()
        pixmap.loadFromData(base64.b64decode(b64_data), "svg")
        return QIcon(pixmap)

    def _perform_achievement_check_and_cache(self, appid):
        appid_str = str(appid)
        achievement_cache_file_path = os.path.join(self.ACHIEVEMENT_DATA_CACHE_DIR, f"{appid_str}.json")
        
        has_achievements_result = False
        error_on_check = None
        cached_data = None

        try:
            if os.path.exists(achievement_cache_file_path):
                try:
                    with open(achievement_cache_file_path, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    if cached_data:
                        has_achievements_result = True
                except Exception:
                    pass

            if not has_achievements_result:
                bin_dir_for_subprocess = os.path.dirname(self.ACHIEVEMENT_FETCHER_PATH)
                
                result = subprocess.run(
                    [self.ACHIEVEMENT_FETCHER_PATH, appid_str],
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding='utf-8',
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=bin_dir_for_subprocess
                )

                if result.returncode != 0:
                    has_achievements_result = False
                else:
                    try:
                        fetched_data = json.loads(result.stdout)
                        if fetched_data:
                            has_achievements_result = True
                            os.makedirs(self.ACHIEVEMENT_DATA_CACHE_DIR, exist_ok=True)
                            with open(achievement_cache_file_path, 'w', encoding='utf-8') as f:
                                json.dump(fetched_data, f, indent=4)
                        else:
                            has_achievements_result = False
                            if os.path.exists(achievement_cache_file_path):
                                os.remove(achievement_cache_file_path)
                    except json.JSONDecodeError as e:
                        has_achievements_result = False
                        if os.path.exists(achievement_cache_file_path):
                            os.remove(achievement_cache_file_path)
                    except Exception as e:
                        has_achievements_result = False
                        print(f"Erro inesperado ao processar saída do fetcher para {appid_str}: {e}")

        except Exception as e:
            error_on_check = str(e) if str(e) else f"Erro desconhecido na validação para {appid_str}."
            has_achievements_result = False

        self.app_validation_cache[appid_str] = has_achievements_result
        try:
            with open(self.APP_VALIDATION_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.app_validation_cache, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar app_validation_cache: {e}")

        QApplication.instance().postEvent(self, AchievementValidationCompletedEvent(
            appid, has_achievements_result, error_on_check
        ))

    def tr(self, key, *args):
        text = self.translations[self.current_language].get(key, key)
        if args:
            try:
                return text.format(*args)
            except (IndexError, KeyError):
                return f"{text} (Erro de formatação com args: {args})"
        return text

    def load_settings(self):
        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_language = settings.get('language', 'pt')
                    self.current_theme = settings.get('theme', 'dark')
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                self.current_language = 'pt'
                self.current_theme = 'dark'
        else:
            self.create_cache_directory()
            self.save_settings()

    def save_settings(self):
        self.create_cache_directory()
        settings = {
            'language': self.current_language,
            'theme': self.current_theme
        }
        try:
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def apply_theme(self, theme):
        if theme == 'dark':
            self.setStyleSheet(ESTILO_DARK)
            self.current_theme = 'dark'
            if hasattr(self, 'settings_button') and self.settings_button is not None:
                self.settings_button.setIcon(self.create_icon_from_b64(ICON_SETTINGS_DARK_B64))

            if hasattr(self, 'game_search_input') and self.game_search_input is not None:
                self.game_search_input.set_search_icon(self.create_icon_from_b64(ICON_SEARCH_DARK_B64))
            if hasattr(self, 'achievement_search_input') and self.achievement_search_input is not None:
                self.achievement_search_input.set_search_icon(self.create_icon_from_b64(ICON_SEARCH_DARK_B64))

        elif theme == 'light':
            self.setStyleSheet(ESTILO_LIGHT)
            self.current_theme = 'light'
            if hasattr(self, 'settings_button') and self.settings_button is not None:
                self.settings_button.setIcon(self.create_icon_from_b64(ICON_SETTINGS_LIGHT_B64))

            if hasattr(self, 'game_search_input') and self.game_search_input is not None:
                self.game_search_input.set_search_icon(self.create_icon_from_b64(ICON_SEARCH_LIGHT_B64))
            if hasattr(self, 'achievement_search_input') and self.achievement_search_input is not None:
                self.achievement_search_input.set_search_icon(self.create_icon_from_b64(ICON_SEARCH_LIGHT_B64))
        self.save_settings()

    def update_ui_texts(self):
        self.setWindowTitle(self.tr('app_title'))
        self.loading_status_label.setText(self.tr('loading_games'))
        if hasattr(self, 'ach_loading_widget'):
            self.ach_loading_widget.setText(self.tr('fetching_achievements_data'))
        self.game_search_input.setPlaceholderText(self.tr('search_placeholder_games'))
        self.ach_title_label.setText(self.tr('achievements_title'))
        self.achievement_search_input.setPlaceholderText(self.tr('search_placeholder_achievements'))
        self.unlock_button.setText(self.tr('unlock_selected'))
        if self.stacked_widget.currentWidget() == self.achievements_panel and self.all_achievements_data:
            self.display_achievements(self.all_achievements_data)

    def create_cache_directory(self):
        if not os.path.exists(self.IMAGE_CACHE_DIR):
            os.makedirs(self.IMAGE_CACHE_DIR)
        if not os.path.exists(os.path.dirname(self.SETTINGS_FILE)):
            os.makedirs(os.path.dirname(self.SETTINGS_FILE))
        if not os.path.exists(self.ACHIEVEMENT_DATA_CACHE_DIR):
            os.makedirs(self.ACHIEVEMENT_DATA_CACHE_DIR)

    def check_binary_files(self):
        required_executables = [
            self.GAME_READER_PATH,
            self.ACHIEVEMENT_FETCHER_PATH,
            self.STEAM_POPPER_PATH
        ]
        for exe_path in required_executables:
            if not os.path.exists(exe_path):
                self.show_custom_message('critical_error', 'required_file_missing', 'error', exe_path)
                sys.exit(1)

    def create_loading_panel(self):
        self.loading_panel = QWidget()
        main_layout = QVBoxLayout(self.loading_panel)
        gradient_style = """
            QWidget#loading_panel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 #1a1a1a, stop:1 #121212);
            }
        """
        self.loading_panel.setObjectName("loading_panel")
        self.loading_panel.setStyleSheet(gradient_style)

        icon_path = os.path.join(self._PACKAGED_RESOURCES_PATH, "src", "icons", "icon.png")
        original_pixmap = QPixmap(icon_path)
        icon_size = 250
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
        glow_effect = QGraphicsDropShadowEffect()
        glow_effect.setBlurRadius(25)
        glow_effect.setOffset(0, 0)
        icon_label.setGraphicsEffect(glow_effect)
        self.glow_animation = QPropertyAnimation(glow_effect, b"color")
        self.glow_animation.setDuration(2000)
        start_color = QColor("#0078ff"); start_color.setAlpha(100)
        end_color = QColor("#0078ff"); end_color.setAlpha(255)
        self.glow_animation.setStartValue(start_color)
        self.glow_animation.setKeyValueAt(0.5, end_color)
        self.glow_animation.setEndValue(start_color)
        self.glow_animation.setLoopCount(-1)
        self.glow_animation.start()
        icon_layout = QHBoxLayout()
        icon_layout.addStretch(1)
        icon_layout.addWidget(icon_label)
        icon_layout.addStretch(1)
        self.loading_status_label = QLabel(self.tr('loading_games'))
        self.loading_status_label.setFont(QFont("Segoe UI", 10))
        self.loading_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_progress_bar = QProgressBar()
        self.loading_progress_bar.setFixedWidth(400)
        self.loading_progress_bar.setTextVisible(False)
        progress_bar_layout = QHBoxLayout()
        progress_bar_layout.addStretch(1)
        progress_bar_layout.addWidget(self.loading_progress_bar)
        progress_bar_layout.addStretch(1)
        main_layout.addStretch(1)
        main_layout.addLayout(icon_layout)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.loading_status_label)
        main_layout.addLayout(progress_bar_layout)
        main_layout.addStretch(1)
        self.stacked_widget.addWidget(self.loading_panel)

    def create_games_panel(self):
        self.games_panel = QWidget()
        main_layout = QVBoxLayout(self.games_panel)
        main_layout.setContentsMargins(CARD_PADDING, CARD_PADDING, CARD_PADDING, 0)
        top_bar_layout = QHBoxLayout()
        top_bar_layout.setSpacing(10)
        self.game_search_input = SearchLineEdit(self, search_icon=self.icon_search,
                                                placeholder_key='search_placeholder_games')
        self.game_search_input.setFixedHeight(40)
        self.game_search_input.textChanged.connect(self.filter_games)
        top_bar_layout.addWidget(self.game_search_input, 1)
        self.settings_button = QPushButton()
        self.settings_button.setIconSize(QSize(24, 24))
        self.settings_button.setFixedSize(40, 40)
        self.settings_button.clicked.connect(self.show_settings_dialog)
        top_bar_layout.addWidget(self.settings_button)
        main_layout.addLayout(top_bar_layout)
        main_layout.addSpacing(CARD_PADDING)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scroll_content = QWidget()
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(CARD_PADDING)
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
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
        self.ach_title_label = QLabel(self.tr('achievements_title'))
        self.ach_title_label.setObjectName("TitleLabel")
        self.achievement_search_input = SearchLineEdit(self, search_icon=self.icon_search,
                                                       placeholder_key='search_placeholder_achievements')
        self.achievement_search_input.setFixedHeight(40)
        self.achievement_search_input.setFixedWidth(200)
        self.achievement_search_input.textChanged.connect(self.filter_achievements)
        title_bar.addWidget(back_button)
        title_bar.addWidget(self.ach_title_label)
        title_bar.addStretch(1)
        title_bar.addWidget(self.achievement_search_input)
        main_layout.addLayout(title_bar)
        
        self.ach_loading_widget = QLabel(self.tr('fetching_achievements_data'))
        self.ach_loading_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ach_loading_widget.setFont(QFont("Segoe UI", 14))
        main_layout.addWidget(self.ach_loading_widget)

        self.ach_scroll = QScrollArea()
        self.ach_scroll.setWidgetResizable(True)
        self.ach_scroll.setFrameShape(QFrame.Shape.NoFrame)
        ach_scroll_content = QWidget()
        self.ach_list_layout = QVBoxLayout(ach_scroll_content)
        self.ach_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.ach_list_layout.setSpacing(10)
        self.ach_scroll.setWidget(ach_scroll_content)
        main_layout.addWidget(self.ach_scroll)
        
        self.unlock_button = QPushButton(self.tr('unlock_selected'))
        self.unlock_button.setObjectName("AccentButton")
        self.unlock_button.setFixedHeight(40)
        self.unlock_button.clicked.connect(self.unlock_selected_achievements)
        main_layout.addWidget(self.unlock_button)
        
        self.ach_scroll.hide()
        self.unlock_button.hide()
        
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
        path = os.path.join(self.IMAGE_CACHE_DIR, f"{appid}.jpg")
        if os.path.exists(path):
            pixmap = QPixmap(path)
            image_label.setPixmap(pixmap.scaled(CARD_WIDTH, CARD_IMAGE_HEIGHT, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        else:
            image_label.setText(self.tr('no_image'))
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
                self.show_custom_message('info', 'no_achievements', 'info', self.current_game_name)
        else:
            self.status_bar.showMessage(self.tr('validating_simple'))
            threading.Thread(target=self._perform_achievement_check_and_cache, args=(appid,), daemon=True).start()

    def show_custom_message(self, title_key, message_key, dialog_type='info', *args):
        formatted_message = self.tr(message_key)
        if args:
            try:
                formatted_message = formatted_message.format(*args)
            except (IndexError, KeyError):
                formatted_message += f"\nDetalhes: {args}"
        dialog = CustomDialog(self, title_key, formatted_message, dialog_type)
        dialog.exec()

    def show_settings_dialog(self):
        dialog = SettingsDialog(self, self.current_language, self.current_theme)
        dialog.language_changed.connect(self.set_language)
        dialog.theme_changed.connect(self.apply_theme)
        dialog.exec()

    def set_language(self, lang):
        if self.current_language != lang:
            self.current_language = lang
            self.save_settings()
            self.update_ui_texts()
            self.build_grid(self.currently_displayed_games)

    def resizeEvent(self, event):
        if self.stacked_widget.currentWidget() == self.games_panel:
            self.build_grid(self.currently_displayed_games)
        super().resizeEvent(event)
        
    def _master_loader_thread(self):
        try:
            QApplication.instance().postEvent(self, UpdateLoadingEvent('loading_games', 0, 0))
            
            bin_dir_for_subprocess = os.path.dirname(self.GAME_READER_PATH)
            
            result = subprocess.run(
                [self.GAME_READER_PATH],
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=bin_dir_for_subprocess
            )

            if result.returncode != 0:
                QApplication.instance().postEvent(self, ShowMessageEvent('critical_error', 'failed_load_games', 'error', result.stderr))
                return
            
            games_dict = {int(m.group(2)): m.group(1).strip() for line in result.stdout.splitlines() if (m := re.match(r'^(.*) \(AppID: (\d+)\)$', line.strip()))}
            self.all_games_list = sorted([{'appid': appid, 'name': name} for appid, name in games_dict.items()], key=lambda g: g['name'])

            appids_with_images = self._fetch_all_images_parallel(self.all_games_list)
            
            games_to_display = [game for game in self.all_games_list if game['appid'] in appids_with_images]
            self.all_games_list = games_to_display

            QApplication.instance().postEvent(self, BuildGridEvent(games_to_display))
            QApplication.instance().postEvent(self, UpdateLoadingEvent('ready', len(games_to_display), len(games_to_display)))
        except Exception as e:
            QApplication.instance().postEvent(self, ShowMessageEvent('critical_error', 'unexpected_error', 'error', str(e)))
            pass

    def _fetch_all_images_parallel(self, games_to_fetch):
        total = len(games_to_fetch)
        QApplication.instance().postEvent(self, UpdateLoadingEvent('downloading_images', 0, total, 0, total))
        
        appids_with_images = set()
        
        def check_and_download(appid, index):
            path = os.path.join(self.IMAGE_CACHE_DIR, f"{appid}.jpg")
            image_is_valid = False
            
            if os.path.exists(path):
                pixmap = QPixmap()
                if pixmap.load(path) and not pixmap.isNull():
                    image_is_valid = True
            
            if not image_is_valid:
                try:
                    r = requests.get(f"https://cdn.akamai.steamstatic.com/steam/apps/{appid}/header.jpg", timeout=5)
                    if r.status_code == 200 and len(r.content) > 5000:
                        temp_pixmap = QPixmap()
                        if temp_pixmap.loadFromData(r.content, "JPG") and not temp_pixmap.isNull():
                            with open(path, 'wb') as f: f.write(r.content)
                            image_is_valid = True
                except:
                    pass

            if image_is_valid:
                appids_with_images.add(appid)
            
            QApplication.instance().postEvent(self, UpdateLoadingEvent('downloading_images', index + 1, total, index + 1, total))

        with concurrent.futures.ThreadPoolExecutor(max_workers=(os.cpu_count() or 1) * 2) as executor:
            list(executor.map(check_and_download, [g['appid'] for g in games_to_fetch], range(total)))
        
        return appids_with_images

    def _background_validation_worker(self, games_list):
        if os.path.exists(self.APP_VALIDATION_CACHE_FILE):
            try:
                with open(self.APP_VALIDATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.app_validation_cache = json.load(f)
            except Exception as e:
                print(f"Erro ao carregar cache de validação de apps: {e}")
                self.app_validation_cache = {}
        try:
            with open(self.APP_VALIDATION_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.app_validation_cache, f, indent=4)
        except Exception as e:
            print(f"Erro ao salvar cache de validação de apps: {e}")

    def _check_and_display_achievements_worker(self, appid):
        appid_str = str(appid)
        achievement_cache_path = os.path.join(self.ACHIEVEMENT_DATA_CACHE_DIR, f"{appid_str}.json")
        
        achievements_data = []
        try:
            if os.path.exists(achievement_cache_path):
                with open(achievement_cache_path, 'r', encoding='utf-8') as f:
                    achievements_data = json.load(f)
                
                if not achievements_data:
                    raise ValueError("Cache de conquistas vazio, buscando novamente.")

            if not achievements_data:
                bin_dir_for_subprocess = os.path.dirname(self.ACHIEVEMENT_FETCHER_PATH)
                result = subprocess.run(
                    [self.ACHIEVEMENT_FETCHER_PATH, appid_str],
                    capture_output=True,
                    text=True,
                    check=False,
                    encoding='utf-8',
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    cwd=bin_dir_for_subprocess
                )
                
                if result.returncode != 0:
                    QApplication.instance().postEvent(self, ShowMessageEvent('error', 'failed_fetch_achievements', 'error', result.stderr))
                    return
                achievements_data = json.loads(result.stdout)
                
                os.makedirs(self.ACHIEVEMENT_DATA_CACHE_DIR, exist_ok=True)
                with open(achievement_cache_path, 'w', encoding='utf-8') as f:
                    json.dump(achievements_data, f, indent=4)

            QApplication.instance().postEvent(self, DisplayAchievementsEvent(achievements_data))

        except json.JSONDecodeError as e:
            QApplication.instance().postEvent(self, ShowMessageEvent('error', 'failed_fetch_achievements', 'error', str(e)))
        except Exception as e:
            QApplication.instance().postEvent(self, ShowMessageEvent('error', 'unexpected_error', 'error', str(e)))

    def _show_achievements_for_valid_game(self):
        self.status_bar.showMessage(self.tr('fetching_achievements', self.current_game_name))
        self.ach_title_label.setText(self.current_game_name)
        self.stacked_widget.setCurrentWidget(self.achievements_panel)
        self.achievement_search_input.clear()

        self.ach_loading_widget.show()
        self.ach_scroll.hide()
        self.unlock_button.hide()

        for i in reversed(range(self.ach_list_layout.count())):
            widget = self.ach_list_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.achievement_widgets.clear()
        self.all_achievements_data = []

        threading.Thread(target=self._check_and_display_achievements_worker, args=(self.current_appid,), daemon=True).start()

    def display_achievements(self, achievements_to_display):
        for i in reversed(range(self.ach_list_layout.count())):
            self.ach_list_layout.itemAt(i).widget().setParent(None)
        self.achievement_widgets.clear()

        if not achievements_to_display:
            self.unlock_button.hide()
            self.ach_list_layout.addWidget(QLabel(self.tr('no_achievements_found_search')), alignment=Qt.AlignmentFlag.AlignCenter)
            return

        self.unlock_button.show()
        for ach in achievements_to_display:
            widget = self.create_achievement_widget(ach, self)
            self.ach_list_layout.addWidget(widget)

    def create_achievement_widget(self, ach_data, app_instance):
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
                pixmap = QPixmap()
                
                if side * side * 4 == len(icon_data):
                    q_image = QImage(icon_data, side, side, QImage.Format.Format_RGBA8888)
                    pixmap = QPixmap.fromImage(q_image)
                
                if pixmap.isNull():
                    if pixmap.loadFromData(icon_data, "PNG"): pass
                    elif pixmap.loadFromData(icon_data, "JPG"): pass
                    elif pixmap.loadFromData(icon_data, "SVG"): pass

                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                else:
                    icon_label.setText("?"); icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter); icon_label.setStyleSheet("background-color: #444; border-radius: 4px; color: #bbb; font-size: 24pt; font-weight: bold;")
            except Exception as e:
                print(f"Erro ao processar ícone de conquista (Base64) para {ach_data['apiName']}: {e}")
        else:
            icon_label.setText("?"); icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter); icon_label.setStyleSheet("background-color: #444; border-radius: 4px; color: #bbb; font-size: 24pt; font-weight: bold;")

        toggle_button = QPushButton()
        toggle_button.setObjectName("ToggleButton")
        toggle_button.setFixedSize(36, 36)
        toggle_button.setIconSize(QSize(24, 24))
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        name_label = QLabel(ach_data['name']); name_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        desc_label = QLabel(ach_data['description']); desc_label.setWordWrap(True)
        text_layout.addWidget(name_label); text_layout.addWidget(desc_label)
        
        unlocked_time_label = QLabel()
        unlocked_time_label.setFont(QFont("Segoe UI", 8))
        unlocked_time_label.setStyleSheet("color: #888;")

        if ach_data.get('isAchieved', False) and ach_data.get('unlockedTimestamp', 0) != 0:
            timestamp = ach_data['unlockedTimestamp']
            dt_object = datetime.datetime.fromtimestamp(timestamp)
            formatted_date = dt_object.strftime(app_instance.tr('date_format'))
            unlocked_time_label.setText(app_instance.tr('unlocked_on_date').format(formatted_date))
        else:
            unlocked_time_label.setText(app_instance.tr('not_unlocked'))
        
        text_layout.addWidget(unlocked_time_label)

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
            self.display_achievements(self.all_achievements_data)
        else:
            filtered_achievements = [
                ach for ach in self.all_achievements_data
                if search_text in ach['name'].lower()
            ]
            self.display_achievements(filtered_achievements)

    def filter_games(self, text):
        search_text = text.lower()
        if not search_text:
            self.build_grid(self.all_games_list)
        else:
            filtered_games = [
                game for game in self.all_games_list
                if search_text in game['name'].lower()
            ]
            self.build_grid(filtered_games)

    def unlock_selected_achievements(self):
        to_unlock = [name for name, data in self.achievement_widgets.items() if data['selected'] and not data['initial_state']]
        if not to_unlock:
            self.show_custom_message('info', 'no_new_achievements_selected', 'info')
            return
        self.unlock_button.setEnabled(False)
        self.status_bar.showMessage(self.tr('unlocking_achievements_message'))
        
        threading.Thread(target=self._unlock_achievements_worker, args=(to_unlock, self.current_appid), daemon=True).start()
    
    def _unlock_achievements_worker(self, to_unlock, appid_to_refresh):
        try:
            bin_dir_for_subprocess = os.path.dirname(self.STEAM_POPPER_PATH)
            command = [self.STEAM_POPPER_PATH, str(appid_to_refresh)] + to_unlock
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW,
                cwd=bin_dir_for_subprocess
            )

            if result.returncode != 0:
                error_message = result.stderr or result.stdout or f"Código de erro {result.returncode}"
                QApplication.instance().postEvent(self, UnlockProcessCompletedEvent(
                    None, None, None, None,
                    'error', 'failed_unlocker', 'error', (error_message,),
                    appid_to_refresh
                ))
            else:
                achievement_cache_path = os.path.join(self.ACHIEVEMENT_DATA_CACHE_DIR, f"{appid_to_refresh}.json")
                if os.path.exists(achievement_cache_path):
                    try:
                        with open(achievement_cache_path, 'r+', encoding='utf-8') as f:
                            ach_data = json.load(f)
                            unlocked_set = set(to_unlock)
                            current_timestamp = int(time.time())
                            for ach in ach_data:
                                if ach['apiName'] in unlocked_set:
                                    ach['isAchieved'] = True
                                    ach['unlockedTimestamp'] = current_timestamp
                            f.seek(0)
                            json.dump(ach_data, f, indent=4)
                            f.truncate()
                    except Exception as e:
                        print(f"Alerta: Falha ao atualizar o cache de conquistas para {appid_to_refresh}: {e}")
                
                time.sleep(2)
                
                QApplication.instance().postEvent(self, UnlockProcessCompletedEvent(
                    'success', 'achievements_unlocked_success', 'success', (),
                    None, None, None, None,
                    appid_to_refresh
                ))
        except Exception as e:
            QApplication.instance().postEvent(self, UnlockProcessCompletedEvent(
                None, None, None, None,
                'error', 'failed_unlocker', 'error', (str(e),),
                appid_to_refresh
            ))

    def show_games_panel(self):
        self.stacked_widget.setCurrentWidget(self.games_panel)
        self.status_message_label.setText(self.tr('ready'))
        self.game_search_input.clear()

    def customEvent(self, event):
        if event.type() == UpdateLoadingEvent.TYPE:
            self.loading_status_label.setText(self.tr(event.text_key, *event.args))
            self.loading_progress_bar.setMaximum(event.maximum)
            self.loading_progress_bar.setValue(event.value)
        elif event.type() == BuildGridEvent.TYPE:
            self.currently_displayed_games = event.games
            self.stacked_widget.setCurrentWidget(self.games_panel)
            self.build_grid(event.games)
            self.status_bar.show()
        elif event.type() == ShowAchievementsEvent.TYPE: self._show_achievements_for_valid_game()
        elif event.type() == DisplayAchievementsEvent.TYPE:
            self.all_achievements_data = sorted(event.data, key=lambda x: (x['isAchieved'], x['name'].lower()))
            self.display_achievements(self.all_achievements_data)
            self.status_bar.showMessage(self.tr('ready'))
            self.ach_loading_widget.hide()
            self.ach_scroll.show()

        elif event.type() == ShowMessageEvent.TYPE:
            self.show_custom_message(event.title_key, event.message_key, event.dialog_type, *event.args)
            self.status_message_label.setText(self.tr('ready'))
        elif event.type() == UnlockProcessCompletedEvent.TYPE:
            self.unlock_button.setEnabled(True)
            self.status_bar.showMessage(self.tr('ready'))
            if event.success_title_key:
                self.show_custom_message(event.success_title_key, event.success_message_key, event.success_dialog_type, *event.success_args)
                threading.Thread(target=self._check_and_display_achievements_worker, args=(event.appid_to_refresh,), daemon=True).start()
            else:
                self.show_custom_message(event.error_title_key, event.error_message_key, event.error_dialog_type, *event.error_args)
        elif event.type() == AchievementValidationCompletedEvent.TYPE:
            self.status_bar.showMessage(self.tr('ready'))
            if event.error_message:
                self.show_custom_message('error', 'failed_fetch_achievements', 'error', event.error_message)
            elif event.has_achievements:
                self._show_achievements_for_valid_game()
            else:
                self.show_custom_message('info', 'no_achievements', 'info', self.current_game_name)

if __name__ == '__main__':
    myappid = u'sao.override'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())