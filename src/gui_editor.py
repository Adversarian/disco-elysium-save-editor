import sys
import os
import tempfile
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QTabWidget,
    QGridLayout, QSizePolicy, QMessageBox, QFileDialog, QCheckBox
)
from PyQt6.QtCore import Qt, QSize, QByteArray, QBuffer, QIODevice, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPalette, QBrush, QPainter, QColor, QIcon, QImage
from PIL import Image, ImageEnhance
from io import BytesIO

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))
from edits import SaveState, MAPS
from utils import auto_discover, parse_saves, discover_baks, restore_save

# Path to assets
ASSETS_DIR = Path(__file__).parent.parent / "assets" / "textures" / "paper_by_darkwood67"

# Disco Elysium Authentic Color Palette
DE_COLORS = {
    # Base colors
    "bg_darkest": "#0a0805",
    "bg_dark": "#1a1410",
    "bg_medium": "#2d2419",
    "bg_paper": "#e8dcc4",
    "bg_paper_dark": "#cbb896",

    # Attribute colors
    "intellect": "#5bb4e8",
    "psyche": "#a874c4",
    "physique": "#e74c3c",
    "motorics": "#f39c12",

    # Accent colors
    "accent_orange": "#ff6b35",
    "accent_amber": "#f7931e",
    "accent_gold": "#d4af37",

    # Text colors
    "text_light": "#f0e6d2",
    "text_medium": "#c4b5a0",
    "text_dark": "#2d2419",
}


class TextureManager:
    """Manages loading and tinting paper textures"""

    def __init__(self):
        self.base_textures = {}
        self.tinted_textures = {}
        self.load_textures()
        self.create_tinted_textures()

    def load_textures(self):
        """Load all base paper textures"""
        texture_files = {
            "vintage": "vintage_paper_by_darkwood67.jpg",
            "old": "old_paper_by_darkwood67.jpg",
            "brown_age": "brown_age_by_darkwood67.jpg",
            "brown_ice": "brown_ice_by_darkwood67.jpg"
        }

        for name, filename in texture_files.items():
            try:
                texture_path = ASSETS_DIR / filename
                if texture_path.exists():
                    img = Image.open(texture_path)
                    # Use larger tiles for better stretch effect (less visible tiling)
                    img = img.resize((800, 800), Image.Resampling.LANCZOS)
                    self.base_textures[name] = img
            except Exception as e:
                print(f"Could not load texture {name}: {e}")

    def tint_texture(self, texture, color_hex, blend_amount=0.4):
        """Tint a texture with a color"""
        try:
            color_hex = color_hex.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))

            texture_copy = texture.copy().convert('RGBA')
            color_overlay = Image.new('RGBA', texture_copy.size, (r, g, b, int(255 * blend_amount)))

            tinted = Image.alpha_composite(texture_copy.convert('RGBA'), color_overlay)
            return tinted.convert('RGB')
        except Exception as e:
            print(f"Could not tint texture: {e}")
            return texture

    def create_tinted_textures(self):
        """Pre-create tinted textures for each UI color"""
        if not self.base_textures:
            return

        texture_mapping = {
            "bg_darkest": ("brown_age", 0.7),    # More visible texture
            "bg_dark": ("brown_age", 0.6),       # More visible
            "bg_medium": ("brown_ice", 0.5),     # More visible
            "bg_paper": ("vintage", 0.25),       # Slightly more visible
            "intellect": ("old", 0.4),           # Better contrast
            "psyche": ("vintage", 0.4),          # Better contrast
            "physique": ("brown_age", 0.55),     # More saturated red for rollback button
            "motorics": ("old", 0.4),            # Better contrast
            "accent_orange": ("brown_ice", 0.5), # More visible
            "accent_gold": ("vintage", 0.45),    # More visible
        }

        for color_key, (texture_name, blend) in texture_mapping.items():
            if texture_name in self.base_textures and color_key in DE_COLORS:
                tinted = self.tint_texture(
                    self.base_textures[texture_name],
                    DE_COLORS[color_key],
                    blend
                )
                self.tinted_textures[color_key] = tinted

    def get_qpixmap(self, color_key, width=None, height=None):
        """Get a QPixmap for a color key, tiled if dimensions provided"""
        if color_key not in self.tinted_textures:
            return None

        texture = self.tinted_textures[color_key]

        if width and height:
            # Tile the texture
            tex_width, tex_height = texture.size
            tiles_x = (width // tex_width) + 2
            tiles_y = (height // tex_height) + 2

            tiled = Image.new('RGB', (tiles_x * tex_width, tiles_y * tex_height))
            for i in range(tiles_x):
                for j in range(tiles_y):
                    tiled.paste(texture, (i * tex_width, j * tex_height))

            tiled = tiled.crop((0, 0, width, height))
            texture = tiled

        # Convert PIL Image to QPixmap without temp files
        # Convert to bytes
        buffer = BytesIO()
        texture.save(buffer, format='PNG')
        buffer.seek(0)

        # Load into QPixmap
        qimg = QImage()
        qimg.loadFromData(buffer.read())
        pixmap = QPixmap.fromImage(qimg)

        return pixmap


# Global texture manager
texture_manager = TextureManager()


# QSS Stylesheet for Disco Elysium styling
QSS_STYLE = f"""
QMainWindow {{
    background-color: {DE_COLORS['bg_darkest']};
}}

QLabel {{
    color: {DE_COLORS['text_light']};
    background: transparent;
}}

QLineEdit {{
    background-color: {DE_COLORS['bg_paper']};
    color: {DE_COLORS['text_dark']};
    border: 3px solid {DE_COLORS['accent_gold']};
    border-radius: 2px;
    padding: 10px;
    font-family: 'Courier New';
    font-size: 13pt;
    font-weight: bold;
    selection-background-color: {DE_COLORS['accent_orange']};
}}

QLineEdit:focus {{
    border-color: {DE_COLORS['accent_amber']};
    background-color: #fff8e8;
}}

QPushButton {{
    background-color: {DE_COLORS['accent_orange']};
    color: {DE_COLORS['bg_darkest']};
    border: 2px solid {DE_COLORS['accent_gold']};
    padding: 8px 16px;
    font-family: 'Book Antiqua';
    font-size: 11pt;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {DE_COLORS['accent_amber']};
}}

QPushButton:pressed {{
    background-color: {DE_COLORS['accent_gold']};
}}

QTabWidget::pane {{
    border: 3px solid {DE_COLORS['accent_gold']};
    background-color: {DE_COLORS['bg_darkest']};
}}

QTabBar::tab {{
    background-color: {DE_COLORS['bg_medium']};
    color: {DE_COLORS['text_light']};
    border: 2px solid {DE_COLORS['accent_gold']};
    padding: 12px 24px;
    margin: 2px;
    font-family: 'Cambria';
    font-size: 16pt;
    font-weight: bold;
}}

QTabBar::tab:selected {{
    background-color: {DE_COLORS['accent_orange']};
    color: {DE_COLORS['bg_darkest']};
}}

QTabBar::tab:hover {{
    background-color: {DE_COLORS['accent_amber']};
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background-color: {DE_COLORS['bg_dark']};
    width: 16px;
    border: 2px solid {DE_COLORS['accent_gold']};
    border-radius: 2px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {DE_COLORS['accent_orange']};
    min-height: 30px;
    border: 1px solid {DE_COLORS['accent_gold']};
    border-radius: 2px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {DE_COLORS['accent_amber']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {DE_COLORS['bg_dark']};
    height: 16px;
    border: 2px solid {DE_COLORS['accent_gold']};
    border-radius: 2px;
}}

QScrollBar::handle:horizontal {{
    background-color: {DE_COLORS['accent_orange']};
    min-width: 30px;
    border: 1px solid {DE_COLORS['accent_gold']};
    border-radius: 2px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {DE_COLORS['accent_amber']};
}}
"""


class OrnateFrame(QFrame):
    """Ornate frame with decorative border and textured background"""

    def __init__(self, parent=None, title="", title_color=None, bg_color_key="bg_paper"):
        super().__init__(parent)
        self.bg_color_key = bg_color_key
        self.title = title
        self.title_color = title_color or DE_COLORS['accent_gold']

        # Set frame style
        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(3)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)

        # Title if provided
        if title:
            title_frame = QFrame()
            title_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {DE_COLORS['bg_darkest']};
                    border-bottom: 2px solid {self.title_color};
                }}
            """)
            title_frame.setFixedHeight(40)

            title_layout = QHBoxLayout(title_frame)
            title_layout.setContentsMargins(10, 5, 10, 5)

            # Ornamental brackets
            left_ornament = QLabel("╔═")
            left_ornament.setStyleSheet(f"color: {self.title_color}; font-size: 14pt; font-weight: bold;")

            title_label = QLabel(f"  {title.upper()}  ")
            title_label.setStyleSheet(f"color: {self.title_color}; font-size: 12pt; font-weight: bold; font-family: 'Cambria';")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            right_ornament = QLabel("═╗")
            right_ornament.setStyleSheet(f"color: {self.title_color}; font-size: 14pt; font-weight: bold;")

            title_layout.addWidget(left_ornament)
            title_layout.addWidget(title_label, 1)
            title_layout.addWidget(right_ornament)

            layout.addWidget(title_frame)

        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(5, 5, 5, 5)

        layout.addWidget(self.content_widget)

        # Apply texture as background
        self.apply_texture()

    def apply_texture(self):
        """Apply textured background to the frame"""
        pixmap = texture_manager.get_qpixmap(self.bg_color_key, 800, 600)
        if pixmap:
            palette = self.palette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)


class StatEntry(QWidget):
    """Individual stat entry with label and input"""

    def __init__(self, parent=None, label="", description="", width=120):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"""
            QLabel {{
                color: {DE_COLORS['text_light']};
                font-family: 'Book Antiqua';
                font-size: 12pt;
                font-weight: bold;
            }}
        """)
        layout.addWidget(label_widget)

        # Description
        if description:
            desc_widget = QLabel(description)
            desc_widget.setStyleSheet(f"""
                QLabel {{
                    color: {DE_COLORS['accent_gold']};
                    font-family: 'Book Antiqua';
                    font-size: 9pt;
                    font-style: italic;
                }}
            """)
            desc_widget.setWordWrap(True)
            layout.addWidget(desc_widget)

        # Entry field
        self.entry = QLineEdit()
        self.entry.setFixedWidth(width)
        self.entry.setFixedHeight(38)
        layout.addWidget(self.entry)

        layout.addStretch()


class DiscoElysiumSaveEditor(QMainWindow):
    """Main window for Disco Elysium Save Editor"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DISCO ELYSIUM - Save State Editor")
        self.setGeometry(100, 100, 1400, 850)

        # State management
        self.save_state: Optional[SaveState] = None
        self.current_save_path: Optional[str] = None
        self.save_files: dict = {}
        self.save_buttons: dict = {}

        # Entry widgets for editing
        self.entry_widgets = {}
        self.door_checkboxes = {}

        # References for texture application
        self.commit_button = None
        self.rollback_button = None

        # Apply QSS stylesheet
        self.setStyleSheet(QSS_STYLE)

        # Setup UI
        self.setup_ui()
        self.auto_discover_saves()

        # Apply textures after widgets are rendered (longer delay for full layout)
        QTimer.singleShot(500, self.apply_ui_textures)

    def setup_ui(self):
        """Build the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        self.setup_header(main_layout)

        # Content area
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)

        # Left panel - Save selection
        self.setup_left_panel(content_layout)

        # Right panel - Tabbed editor
        self.setup_right_panel(content_layout)

        main_layout.addWidget(content_widget)

        # Apply texture to content area
        pixmap = texture_manager.get_qpixmap("bg_darkest", 1400, 800)
        if pixmap:
            palette = content_widget.palette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            content_widget.setPalette(palette)
            content_widget.setAutoFillBackground(True)

    def setup_header(self, parent_layout):
        """Setup ornate header"""
        header = QFrame()
        header.setFixedHeight(100)
        # Don't set stylesheet background-color as it will override the texture
        # header.setStyleSheet(f"background-color: {DE_COLORS['bg_paper']};")

        # Apply texture
        pixmap = texture_manager.get_qpixmap("bg_paper", 1400, 100)
        if pixmap:
            palette = header.palette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
            header.setPalette(palette)
            header.setAutoFillBackground(True)
        else:
            # Fallback to solid color if texture fails
            header.setStyleSheet(f"background-color: {DE_COLORS['bg_paper']};")

        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)

        # Top line
        top_line = QFrame()
        top_line.setFixedHeight(4)
        top_line.setStyleSheet(f"background-color: {DE_COLORS['accent_orange']};")
        header_layout.addWidget(top_line)

        # Title area
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Ornaments
        ornament_row = QHBoxLayout()
        ornament_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        left_ornament = QLabel("◆")
        left_ornament.setStyleSheet(f"color: {DE_COLORS['accent_orange']}; font-size: 14pt;")
        ornament_row.addWidget(left_ornament)

        title = QLabel("D I S C O   E L Y S I U M")
        title.setStyleSheet(f"""
            color: {DE_COLORS['text_dark']};
            font-family: 'Cambria';
            font-size: 28pt;
            font-weight: bold;
            letter-spacing: 8px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ornament_row.addWidget(title)

        right_ornament = QLabel("◆")
        right_ornament.setStyleSheet(f"color: {DE_COLORS['accent_orange']}; font-size: 14pt;")
        ornament_row.addWidget(right_ornament)

        title_layout.addLayout(ornament_row)

        # Subtitle
        subtitle = QLabel("— S A V E   S T A T E   E D I T O R —")
        subtitle.setStyleSheet(f"""
            color: {DE_COLORS['accent_orange']};
            font-family: 'Book Antiqua';
            font-size: 11pt;
            font-style: italic;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(title_container)

        # Bottom line
        bottom_line = QFrame()
        bottom_line.setFixedHeight(3)
        bottom_line.setStyleSheet(f"background-color: {DE_COLORS['accent_amber']};")
        header_layout.addWidget(bottom_line)

        parent_layout.addWidget(header)

    def setup_left_panel(self, parent_layout):
        """Setup save file selection panel"""
        left_panel = OrnateFrame(title="Save Files", title_color=DE_COLORS['accent_orange'], bg_color_key="bg_medium")
        left_panel.setFixedWidth(280)

        # Save list scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background-color: {DE_COLORS['bg_dark']};")

        self.save_list_widget = QWidget()
        self.save_list_layout = QVBoxLayout(self.save_list_widget)
        self.save_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.save_list_widget)
        left_panel.content_layout.addWidget(scroll)

        # Buttons
        buttons = [
            ("Browse Files", self.browse_save_file),
            ("Refresh List", self.auto_discover_saves),
            ("Restore Backup", self.restore_backup)
        ]

        for btn_text, cmd in buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(cmd)
            btn.setFixedHeight(32)
            left_panel.content_layout.addWidget(btn)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                background-color: {DE_COLORS['bg_darkest']};
                color: {DE_COLORS['accent_gold']};
                padding: 10px;
                border: 1px solid {DE_COLORS['accent_gold']};
                font-family: 'Consolas';
                font-size: 9pt;
            }}
        """)
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.content_layout.addWidget(self.status_label)

        parent_layout.addWidget(left_panel)

    def setup_right_panel(self, parent_layout):
        """Setup tabbed editing panel"""
        right_panel = OrnateFrame(bg_color_key="bg_paper")

        # Tab widget
        self.tabs = QTabWidget()

        # Create tabs
        self.tab_resources = QWidget()
        self.tab_stats = QWidget()
        self.tab_doors = QWidget()
        self.tab_thoughts = QWidget()
        self.tab_time = QWidget()

        self.tabs.addTab(self.tab_resources, "◆ Resources")
        self.tabs.addTab(self.tab_stats, "◇ Character")
        self.tabs.addTab(self.tab_doors, "◈ Doors")
        self.tabs.addTab(self.tab_thoughts, "◉ Thoughts")
        self.tabs.addTab(self.tab_time, "⧗ Time")

        # Setup each tab
        self.setup_resources_tab()
        self.setup_stats_tab()
        self.setup_doors_tab()
        self.setup_thoughts_tab()
        self.setup_time_tab()

        right_panel.content_layout.addWidget(self.tabs)

        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        self.commit_button = QPushButton("⚡ COMMIT CHANGES ⚡")
        self.commit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DE_COLORS['accent_orange']};
                font-size: 13pt;
                padding: 12px;
                border: 3px solid {DE_COLORS['accent_amber']};
            }}
            QPushButton:hover {{
                background-color: {DE_COLORS['accent_amber']};
            }}
        """)
        self.commit_button.clicked.connect(self.commit_changes)
        control_layout.addWidget(self.commit_button)

        self.rollback_button = QPushButton("↻ ROLLBACK")
        self.rollback_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DE_COLORS['accent_orange']};
                font-size: 13pt;
                padding: 12px;
                border: 3px solid {DE_COLORS['accent_amber']};
            }}
            QPushButton:hover {{
                background-color: {DE_COLORS['accent_amber']};
            }}
        """)
        self.rollback_button.clicked.connect(self.rollback_changes)
        control_layout.addWidget(self.rollback_button)

        right_panel.content_layout.addLayout(control_layout)

        parent_layout.addWidget(right_panel, 1)

    def setup_resources_tab(self):
        """Setup resources tab"""
        layout = QVBoxLayout(self.tab_resources)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QHBoxLayout(scroll_content)

        # Currency & Points
        currency_frame = OrnateFrame(title="Currency & Points", title_color=DE_COLORS['motorics'], bg_color_key="bg_dark")
        currency_layout = QVBoxLayout()

        self.entry_widgets['skill_points'] = self.create_stat_entry(
            currency_frame, "Skill Points", "Unspent points for leveling skills"
        )
        self.entry_widgets['money'] = self.create_stat_entry(
            currency_frame, "Money (Réal)", "Game currency in Réal"
        )

        currency_frame.content_layout.addLayout(currency_layout)
        scroll_layout.addWidget(currency_frame)

        # Consumables
        consumables_frame = OrnateFrame(title="Consumables", title_color=DE_COLORS['physique'], bg_color_key="bg_dark")

        self.entry_widgets['health'] = self.create_stat_entry(
            consumables_frame, "Health Consumables", "Medicine for restoring health"
        )
        self.entry_widgets['morale'] = self.create_stat_entry(
            consumables_frame, "Morale Consumables", "Items for restoring morale"
        )

        scroll_layout.addWidget(consumables_frame)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def setup_stats_tab(self):
        """Setup character stats tab"""
        layout = QVBoxLayout(self.tab_stats)

        # Grid layout for 4 attributes
        grid = QGridLayout()
        grid.setSpacing(10)

        attributes = [
            {"name": "Intellect", "color": DE_COLORS['intellect'], "row": 0, "col": 0,
             "skills": "Logic • Encyclopedia • Rhetoric • Drama • Conceptualization • Visual Calculus"},
            {"name": "Psyche", "color": DE_COLORS['psyche'], "row": 0, "col": 1,
             "skills": "Volition • Inland Empire • Empathy • Authority • Esprit de Corps • Suggestion"},
            {"name": "Physique", "color": DE_COLORS['physique'], "row": 1, "col": 0,
             "skills": "Endurance • Pain Threshold • Physical Instrument • Electrochemistry • Shivers • Half Light"},
            {"name": "Motorics", "color": DE_COLORS['motorics'], "row": 1, "col": 1,
             "skills": "Hand/Eye Coordination • Perception • Reaction Speed • Savoir Faire • Interfacing • Composure"}
        ]

        for attr in attributes:
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            frame.setLineWidth(2)
            frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {DE_COLORS['bg_medium']};
                    border: 2px solid {attr['color']};
                }}
            """)
            frame.setFixedHeight(170)

            # Apply texture
            pixmap = texture_manager.get_qpixmap("bg_medium", 400, 170)
            if pixmap:
                palette = frame.palette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
                frame.setPalette(palette)
                frame.setAutoFillBackground(True)

            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(10, 8, 10, 8)
            frame_layout.setSpacing(4)

            # Header
            header = QLabel(f"◆ {attr['name'].upper()}")
            header.setStyleSheet(f"""
                QLabel {{
                    background-color: {attr['color']};
                    color: {DE_COLORS['bg_darkest']};
                    padding: 6px;
                    font-family: 'Cambria';
                    font-size: 13pt;
                    font-weight: bold;
                }}
            """)
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(header)

            # Skills list
            skills = QLabel(attr['skills'])
            skills.setStyleSheet(f"""
                QLabel {{
                    color: {DE_COLORS['text_medium']};
                    font-family: 'Book Antiqua';
                    font-size: 8pt;
                }}
            """)
            skills.setWordWrap(True)
            skills.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(skills)

            # Entry
            self.entry_widgets[attr['name'].lower()] = QLineEdit()
            self.entry_widgets[attr['name'].lower()].setFixedHeight(36)
            frame_layout.addWidget(self.entry_widgets[attr['name'].lower()])

            grid.addWidget(frame, attr['row'], attr['col'])

        layout.addLayout(grid)

    def setup_doors_tab(self):
        """Setup doors tab"""
        layout = QVBoxLayout(self.tab_doors)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        doors_frame = OrnateFrame(title="Door States", title_color=DE_COLORS['accent_gold'], bg_color_key="bg_dark")

        # Get all door names from MAPS
        door_names = [key for key in MAPS["Doors"].keys() if key != "common_ancestor"]

        # Create checkboxes for each door
        self.door_checkboxes = {}

        for door_name in door_names:
            door_widget = QWidget()
            door_layout = QHBoxLayout(door_widget)
            door_layout.setContentsMargins(10, 5, 10, 5)

            # Checkbox
            checkbox = QCheckBox(door_name)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {DE_COLORS['text_light']};
                    font-family: 'Book Antiqua';
                    font-size: 11pt;
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                    border: 2px solid {DE_COLORS['accent_gold']};
                    background-color: {DE_COLORS['bg_paper']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {DE_COLORS['accent_orange']};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {DE_COLORS['accent_amber']};
                }}
            """)
            door_layout.addWidget(checkbox)
            door_layout.addStretch()

            doors_frame.content_layout.addWidget(door_widget)
            self.door_checkboxes[door_name] = checkbox

        scroll_layout.addWidget(doors_frame)
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def setup_thoughts_tab(self):
        """Setup thoughts tab"""
        layout = QVBoxLayout(self.tab_thoughts)

        unlock_btn = QPushButton("🔓 UNLOCK ALL THOUGHTS")
        unlock_btn.setFixedHeight(50)
        unlock_btn.clicked.connect(self.unlock_thoughts)
        layout.addWidget(unlock_btn)

        layout.addStretch()

    def setup_time_tab(self):
        """Setup time tab"""
        layout = QVBoxLayout(self.tab_time)

        time_frame = OrnateFrame(title="Game Time", title_color=DE_COLORS['accent_gold'], bg_color_key="bg_dark")

        self.entry_widgets['time'] = self.create_stat_entry(
            time_frame, "Time of Day (HH:MM)", "24-hour format"
        )

        layout.addWidget(time_frame)
        layout.addStretch()

    def create_stat_entry(self, parent, label, description=""):
        """Helper to create a stat entry widget"""
        entry = StatEntry(parent, label, description)
        parent.content_layout.addWidget(entry)
        return entry.entry

    def lighten_pixmap(self, pixmap, factor=1.3):
        """Lighten a QPixmap by a given factor"""
        try:
            # Save pixmap to temp file
            temp_in = Path(tempfile.gettempdir()) / f"temp_lighten_in_{id(pixmap)}.png"
            pixmap.save(str(temp_in))

            # Load with PIL
            img = Image.open(temp_in)

            # Brighten the image
            enhancer = ImageEnhance.Brightness(img)
            brightened = enhancer.enhance(factor)

            # Save back to temp file
            temp_out = Path(tempfile.gettempdir()) / f"temp_lighten_out_{id(pixmap)}.png"
            brightened.save(str(temp_out))

            # Load as QPixmap
            result = QPixmap(str(temp_out))

            # Cleanup
            temp_in.unlink(missing_ok=True)
            temp_out.unlink(missing_ok=True)

            return result
        except Exception as e:
            print(f"Error lightening pixmap: {e}")
            return pixmap

    def apply_ui_textures(self):
        """Apply textures to buttons and tab bar after rendering using border-image"""
        try:
            # Commit and rollback buttons stay as solid color (no textures)
            pass

        except Exception as e:
            print(f"Error applying UI textures: {e}")
            import traceback
            traceback.print_exc()

    def auto_discover_saves(self):
        """Auto-discover save files"""
        try:
            result = auto_discover()
            # auto_discover returns (success, path) tuple
            if isinstance(result, tuple):
                success, save_dir = result
            else:
                save_dir = result
                success = bool(save_dir)

            if not success or not save_dir:
                self.set_status("[PERCEPTION - Failed] Could not find save directory")
                print("Save directory not found")
                return

            print(f"Found save directory: {save_dir}")
            self.save_files = parse_saves(save_dir)
            print(f"Parsed {len(self.save_files)} save files")

            self.populate_save_list()
            self.set_status(f"[PERCEPTION - Success] Found {len(self.save_files)} save files")
        except Exception as e:
            error_msg = f"[LOGIC - Failed] Error discovering saves: {e}"
            self.set_status(error_msg)
            print(error_msg)
            import traceback
            traceback.print_exc()

    def populate_save_list(self):
        """Populate the save file list"""
        # Clear existing
        while self.save_list_layout.count():
            child = self.save_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.save_buttons = {}

        for name, path in self.save_files.items():
            btn = QPushButton(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding: 10px;
                    background-color: {DE_COLORS['bg_medium']};
                    color: {DE_COLORS['text_light']};
                }}
                QPushButton:hover {{
                    background-color: {DE_COLORS['accent_orange']};
                    color: {DE_COLORS['bg_darkest']};
                }}
                QPushButton:pressed {{
                    background-color: {DE_COLORS['accent_amber']};
                    color: {DE_COLORS['bg_darkest']};
                }}
            """)
            btn.clicked.connect(lambda checked, p=path, n=name: self.load_save(p, n))
            self.save_list_layout.addWidget(btn)
            self.save_buttons[name] = btn

    def load_save(self, path, name=None):
        """Load a save file"""
        try:
            self.save_state = SaveState(path)
            self.current_save_path = path
            self.populate_fields()

            # Highlight selected save button
            if name and name in self.save_buttons:
                for btn_name, btn in self.save_buttons.items():
                    if btn_name == name:
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                text-align: left;
                                padding: 10px;
                                background-color: {DE_COLORS['accent_orange']};
                                color: {DE_COLORS['bg_darkest']};
                                border: 2px solid {DE_COLORS['accent_amber']};
                            }}
                        """)
                    else:
                        btn.setStyleSheet(f"""
                            QPushButton {{
                                text-align: left;
                                padding: 10px;
                                background-color: {DE_COLORS['bg_medium']};
                                color: {DE_COLORS['text_light']};
                            }}
                            QPushButton:hover {{
                                background-color: {DE_COLORS['accent_orange']};
                                color: {DE_COLORS['bg_darkest']};
                            }}
                        """)

            self.set_status(f"Loaded: {Path(path).name}")
        except Exception as e:
            self.set_status(f"Error loading: {e}")
            QMessageBox.critical(self, "Error", f"Could not load save: {e}")

    def populate_fields(self):
        """Populate UI fields from save state"""
        if not self.save_state:
            return

        try:
            # Resources
            self.entry_widgets['skill_points'].setText(str(self.save_state.get_resource("Skill Points")))
            self.entry_widgets['money'].setText(str(self.save_state.get_resource("Money") // 100))
            self.entry_widgets['health'].setText(str(self.save_state.get_resource("Health Consumables")))
            self.entry_widgets['morale'].setText(str(self.save_state.get_resource("Morale Consumables")))

            # Character stats
            self.entry_widgets['intellect'].setText(str(self.save_state.get_char_sheet_stat("Intellect")))
            self.entry_widgets['psyche'].setText(str(self.save_state.get_char_sheet_stat("Psyche")))
            self.entry_widgets['physique'].setText(str(self.save_state.get_char_sheet_stat("Physique")))
            self.entry_widgets['motorics'].setText(str(self.save_state.get_char_sheet_stat("Motorics")))

            # Time
            self.entry_widgets['time'].setText(self.save_state.get_time())

            # Doors
            for door_name, checkbox in self.door_checkboxes.items():
                checkbox.setChecked(self.save_state.get_door(door_name))
        except Exception as e:
            self.set_status(f"Error populating fields: {e}")

    def commit_changes(self):
        """Commit changes to save file"""
        if not self.save_state:
            QMessageBox.warning(self, "Warning", "No save file loaded")
            return

        try:
            # Apply changes from UI to save state
            # Convert via float first to handle decimal inputs like "0.0"
            self.save_state.set_resource("Skill Points", int(float(self.entry_widgets['skill_points'].text() or "0")))
            # Money accepts decimals (e.g., 10.50) - set_resource will multiply by 100 for cents
            self.save_state.set_resource("Money", float(self.entry_widgets['money'].text() or "0"))
            self.save_state.set_resource("Health Consumables", int(float(self.entry_widgets['health'].text() or "0")))
            self.save_state.set_resource("Morale Consumables", int(float(self.entry_widgets['morale'].text() or "0")))

            self.save_state.set_char_sheet_stat("Intellect", int(float(self.entry_widgets['intellect'].text() or "1")))
            self.save_state.set_char_sheet_stat("Psyche", int(float(self.entry_widgets['psyche'].text() or "1")))
            self.save_state.set_char_sheet_stat("Physique", int(float(self.entry_widgets['physique'].text() or "1")))
            self.save_state.set_char_sheet_stat("Motorics", int(float(self.entry_widgets['motorics'].text() or "1")))

            self.save_state.set_time(value=self.entry_widgets['time'].text())

            # Doors
            for door_name, checkbox in self.door_checkboxes.items():
                self.save_state.set_door(door_name, checkbox.isChecked())

            # Commit
            self.save_state.commit()

            self.set_status("Changes committed successfully!")
            QMessageBox.information(self, "Success", "Changes saved successfully!")
        except Exception as e:
            self.set_status(f"Error committing: {e}")
            QMessageBox.critical(self, "Error", f"Could not save changes: {e}")

    def rollback_changes(self):
        """Rollback changes"""
        if not self.save_state:
            return

        try:
            self.save_state.rollback()
            self.set_status("Changes rolled back")
            self.populate_fields()
        except Exception as e:
            self.set_status(f"Error rolling back: {e}")

    def unlock_thoughts(self):
        """Unlock all thoughts"""
        if not self.save_state:
            QMessageBox.warning(self, "Warning", "No save file loaded")
            return

        try:
            self.save_state.set_all_unknown_and_forgotten_thoughts()
            self.set_status("All thoughts unlocked!")
            QMessageBox.information(self, "Success", "All thoughts have been unlocked!")
        except Exception as e:
            self.set_status(f"Error: {e}")

    def browse_save_file(self):
        """Browse for save file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Save File", "", "Disco Elysium Saves (*.7z)"
        )

        if file_path:
            self.load_save(file_path)

    def restore_backup(self):
        """Restore from backup"""
        try:
            save_dir = auto_discover()
            if not save_dir:
                return

            backups = discover_baks(save_dir)
            if not backups:
                QMessageBox.information(self, "Info", "No backup files found")
                return

            # Show dialog to select backup
            # For now, just show message
            QMessageBox.information(self, "Backups", f"Found {len(backups)} backup files")
        except Exception as e:
            self.set_status(f"Error: {e}")

    def set_status(self, message):
        """Update status label"""
        self.status_label.setText(message)


def main():
    app = QApplication(sys.argv)

    # Set application icon (for taskbar and window)
    # Try multiple paths for development vs compiled executable
    icon_paths = [
        Path(__file__).parent.parent / "assets" / "save.png",  # Running from src/
        Path(sys.executable).parent / "assets" / "save.png",   # Nuitka compiled
        Path.cwd() / "assets" / "save.png",                    # Current directory
    ]

    for icon_path in icon_paths:
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            app.setWindowIcon(icon)  # Set globally for taskbar
            break

    # Set default font
    font = QFont("Book Antiqua", 10)
    app.setFont(font)

    window = DiscoElysiumSaveEditor()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
