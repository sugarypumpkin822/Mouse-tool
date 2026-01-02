"""
Modern UI styling for the application
"""

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


def apply_modern_style(app):
    """Apply modern styling to the application"""
    logger = get_logger(__name__)
    
    try:
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #667eea;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: white;
            }
            
            QPushButton {
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                background-color: #667eea;
                color: white;
                border: none;
            }
            
            QPushButton:hover {
                background-color: #5a6fd8;
            }
            
            QPushButton:pressed {
                background-color: #4e5fc6;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QSpinBox, QComboBox, QLineEdit {
                padding: 5px;
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 12px;
            }
            
            QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border-color: #667eea;
            }
            
            QSlider::groove:horizontal {
                height: 8px;
                background: #ddd;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #667eea;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid white;
            }
            
            QSlider::handle:horizontal:hover {
                background: #5a6fd8;
            }
            
            QTabWidget::pane {
                border: 2px solid #667eea;
                border-radius: 5px;
                background: white;
            }
            
            QTabBar::tab {
                padding: 10px 20px;
                font-weight: bold;
                background: #f0f0f0;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            
            QTabBar::tab:hover:!selected {
                background: #e0e0e0;
            }
            
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background-color: #667eea;
                border-radius: 3px;
            }
            
            QListWidget {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            
            QListWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            
            QTableWidget {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #eee;
            }
            
            QTableWidget::item {
                padding: 5px;
            }
            
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #ddd;
            }
            
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            
            QCheckBox {
                font-weight: bold;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #667eea;
                border-radius: 3px;
                background-color: white;
            }
            
            QCheckBox::indicator:checked {
                background-color: #667eea;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xMSAwLjVMMy41IDhMMSA0LjVIMTEWiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+);
            }
            
            QRadioButton {
                font-weight: bold;
                spacing: 8px;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #667eea;
                border-radius: 9px;
                background-color: white;
            }
            
            QRadioButton::indicator:checked {
                background-color: #667eea;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNiIgY3k9IjYiIHI9IjQiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPg==);
            }
            
            QLabel {
                font-size: 12px;
            }
            
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #ddd;
            }
            
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #ddd;
            }
            
            QMenuBar::item {
                padding: 5px 10px;
                background-color: transparent;
            }
            
            QMenuBar::item:selected {
                background-color: #667eea;
                color: white;
            }
            
            QMenu {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            
            QMenu::item {
                padding: 8px 20px;
            }
            
            QMenu::item:selected {
                background-color: #667eea;
                color: white;
            }
            
            QToolTip {
                background-color: #333;
                color: white;
                border: 1px solid #667eea;
                border-radius: 3px;
                padding: 5px;
            }
            
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: #ccc;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #667eea;
            }
        """)
        
        logger.info("Modern style applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying modern style: {e}")


def apply_dark_style(app):
    """Apply dark theme styling"""
    logger = get_logger(__name__)
    
    try:
        app.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            
            QPushButton {
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                background-color: #555;
                color: white;
                border: none;
            }
            
            QPushButton:hover {
                background-color: #666;
            }
            
            QPushButton:pressed {
                background-color: #444;
            }
            
            QPushButton:disabled {
                background-color: #333;
                color: #888;
            }
            
            QSpinBox, QComboBox, QLineEdit {
                padding: 5px;
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #3c3c3c;
                color: #ffffff;
                font-size: 12px;
            }
            
            QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border-color: #667eea;
            }
            
            QSlider::groove:horizontal {
                height: 8px;
                background: #555;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #667eea;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid white;
            }
            
            QSlider::handle:horizontal:hover {
                background: #7f8fd8;
            }
            
            QTabWidget::pane {
                border: 2px solid #555;
                border-radius: 5px;
                background: #3c3c3c;
            }
            
            QTabBar::tab {
                padding: 10px 20px;
                font-weight: bold;
                background: #555;
                border: 1px solid #333;
                border-bottom: none;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                margin-right: 2px;
                color: #ffffff;
            }
            
            QTabBar::tab:selected {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            
            QTabBar::tab:hover:!selected {
                background: #666;
            }
            
            QLabel {
                color: #ffffff;
            }
            
            QTextEdit {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #2b2b2b;
                color: #00ff00;
                padding: 5px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        logger.info("Dark style applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying dark style: {e}")
