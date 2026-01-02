"""
Macro recording and management tab
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QGroupBox, QTableWidget,
                             QTableWidgetItem, QComboBox, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt

try:
    from mouse_config.utils.logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)


class MacrosTab(QWidget):
    """Macro recording and button remapping tab"""
    
    settings_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.controller = None
        self.macro_recorder = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Macro Recording Section
        macro_group = QGroupBox("🎬 Macro Recording")
        macro_layout = QVBoxLayout()
        
        # Recording controls
        record_layout = QHBoxLayout()
        self.record_btn = QPushButton("🔴 Record Macro")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_macro_recording)
        record_layout.addWidget(self.record_btn)
        
        self.stop_record_btn = QPushButton("⏹️ Stop")
        self.stop_record_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.stop_record_btn.clicked.connect(self.stop_macro_recording)
        self.stop_record_btn.setEnabled(False)
        record_layout.addWidget(self.stop_record_btn)
        
        self.play_macro_btn = QPushButton("▶️ Play Macro")
        self.play_macro_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50; 
                color: white; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        self.play_macro_btn.clicked.connect(self.play_macro)
        self.play_macro_btn.setEnabled(False)
        record_layout.addWidget(self.play_macro_btn)
        
        macro_layout.addLayout(record_layout)
        
        # Macro list
        self.macro_list = QListWidget()
        self.macro_list.setMaximumHeight(150)
        macro_layout.addWidget(QLabel("Recorded Macros:"))
        macro_layout.addWidget(self.macro_list)
        
        macro_group.setLayout(macro_layout)
        layout.addWidget(macro_group)
        
        # Button Remapping Section
        remap_group = QGroupBox("🔄 Button Remapping")
        remap_layout = QVBoxLayout()
        
        # Button selection
        button_layout = QHBoxLayout()
        button_layout.addWidget(QLabel("Button:"))
        self.button_combo = QComboBox()
        self.button_combo.addItems(["Left Click", "Right Click", "Middle Click", "Side 1", "Side 2", "Side 3", "Side 4"])
        button_layout.addWidget(self.button_combo)
        
        button_layout.addWidget(QLabel("Action:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Default", "DPI Up", "DPI Down", "Profile Switch", "Macro 1", "Macro 2", "Macro 3", "Disable"])
        button_layout.addWidget(self.action_combo)
        
        remap_btn = QPushButton("🔄 Remap Button")
        remap_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px; 
                font-weight: bold; 
                border-radius: 5px;
            }
        """)
        remap_btn.clicked.connect(self.remap_button)
        button_layout.addWidget(remap_btn)
        
        remap_layout.addLayout(button_layout)
        
        # Current mappings
        self.mappings_table = QTableWidget(0, 3)
        self.mappings_table.setHorizontalHeaderLabels(["Button", "Action", "Status"])
        self.mappings_table.horizontalHeader().setStretchLastSection(True)
        remap_layout.addWidget(self.mappings_table)
        
        remap_group.setLayout(remap_layout)
        layout.addWidget(remap_group)
        
        layout.addStretch()
    
    def set_controller(self, controller):
        """Set the device controller"""
        self.controller = controller
        if controller:
            # Initialize macro recorder with controller
            try:
                from mouse_config.advanced import MacroRecorder
                self.macro_recorder = MacroRecorder()
            except ImportError:
                self.macro_recorder = None
    
    def toggle_macro_recording(self):
        """Toggle macro recording state"""
        try:
            if not self.macro_recorder:
                QMessageBox.warning(self, "Warning", "No device connected for macro recording!")
                return
            
            if not self.macro_recorder.recording:
                if self.macro_recorder.start_recording():
                    self.record_btn.setText("⏸️ Recording...")
                    self.record_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #FF6B6B; 
                            color: white; 
                            padding: 10px; 
                            font-weight: bold; 
                            border-radius: 5px;
                        }
                    """)
                    self.stop_record_btn.setEnabled(True)
                    self.play_macro_btn.setEnabled(False)
                    self.logger.info("Started macro recording")
            else:
                self.stop_macro_recording()
                
        except Exception as e:
            self.logger.error(f"Error toggling macro recording: {e}")
            QMessageBox.critical(self, "Error", f"Failed to toggle macro recording: {e}")
    
    def stop_macro_recording(self):
        """Stop macro recording"""
        try:
            if self.macro_recorder and self.macro_recorder.recording:
                actions = self.macro_recorder.stop_recording()
                self.record_btn.setText("🔴 Record Macro")
                self.record_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FF0000; 
                        color: white; 
                        padding: 10px; 
                        font-weight: bold; 
                        border-radius: 5px;
                    }
                """)
                self.stop_record_btn.setEnabled(False)
                
                if actions:
                    macro_name = f"Macro {len(actions)} actions"
                    self.macro_list.addItem(macro_name)
                    self.macro_list.item(self.macro_list.count() - 1).setData(Qt.ItemDataRole.UserRole, actions)
                    self.play_macro_btn.setEnabled(True)
                    self.logger.info(f"Recorded macro with {len(actions)} actions")
                else:
                    self.logger.warning("No actions recorded")
                    
        except Exception as e:
            self.logger.error(f"Error stopping macro recording: {e}")
    
    def play_macro(self):
        """Play selected macro"""
        try:
            current_item = self.macro_list.currentItem()
            if current_item and self.macro_recorder:
                actions = current_item.data(Qt.ItemDataRole.UserRole)
                if actions:
                    self.logger.info(f"Playing macro with {len(actions)} actions")
                    # Play macro in separate thread
                    import threading
                    threading.Thread(
                        target=self.macro_recorder.play_macro,
                        args=(actions, 1),
                        daemon=True
                    ).start()
                    
        except Exception as e:
            self.logger.error(f"Error playing macro: {e}")
            QMessageBox.critical(self, "Error", f"Failed to play macro: {e}")
    
    def remap_button(self):
        """Remap mouse button"""
        try:
            if not self.controller or not self.controller.connected:
                QMessageBox.warning(self, "Warning", "No mouse connected!")
                return
            
            button = self.button_combo.currentText()
            action = self.action_combo.currentText()
            
            # Add to mappings table
            row = self.mappings_table.rowCount()
            self.mappings_table.insertRow(row)
            self.mappings_table.setItem(row, 0, QTableWidgetItem(button))
            self.mappings_table.setItem(row, 1, QTableWidgetItem(action))
            self.mappings_table.setItem(row, 2, QTableWidgetItem("Applied"))
            
            self.logger.info(f"Remapped {button} to {action}")
            
            # Apply to device
            button_map = {"Left Click": 1, "Right Click": 2, "Middle Click": 3, "Side 1": 4, "Side 2": 5, "Side 3": 6, "Side 4": 7}
            action_map = {"Default": 0, "DPI Up": 1, "DPI Down": 2, "Profile Switch": 3, "Macro 1": 4, "Macro 2": 5, "Macro 3": 6, "Disable": 255}
            
            button_id = button_map.get(button, 1)
            action_id = action_map.get(action, 0)
            
            if hasattr(self.controller.protocol, 'set_button_mapping'):
                command = self.controller.protocol.set_button_mapping(button_id, action_id)
                self.controller.send_command(command)
                
        except Exception as e:
            self.logger.error(f"Error remapping button: {e}")
            QMessageBox.critical(self, "Error", f"Failed to remap button: {e}")
    
    def load_settings(self, settings):
        """Load settings into the tab"""
        # Macro settings are handled separately
        pass
    
    def update_settings(self, settings):
        """Update settings from the tab"""
        # Macro settings are handled separately
        pass
    
    def apply_settings(self, controller):
        """Apply settings to the device"""
        results = {}
        
        try:
            # Apply button mappings
            if controller and controller.connected:
                mappings_applied = 0
                for row in range(self.mappings_table.rowCount()):
                    button_item = self.mappings_table.item(row, 0)
                    action_item = self.mappings_table.item(row, 1)
                    
                    if button_item and action_item:
                        button = button_item.text()
                        action = action_item.text()
                        
                        # Apply mapping
                        button_map = {"Left Click": 1, "Right Click": 2, "Middle Click": 3, "Side 1": 4, "Side 2": 5, "Side 3": 6, "Side 4": 7}
                        action_map = {"Default": 0, "DPI Up": 1, "DPI Down": 2, "Profile Switch": 3, "Macro 1": 4, "Macro 2": 5, "Macro 3": 6, "Disable": 255}
                        
                        button_id = button_map.get(button, 1)
                        action_id = action_map.get(action, 0)
                        
                        if hasattr(controller.protocol, 'set_button_mapping'):
                            command = controller.protocol.set_button_mapping(button_id, action_id)
                            if controller.send_command(command):
                                mappings_applied += 1
                
                results['button_mappings'] = mappings_applied > 0
            else:
                results['button_mappings'] = None
                
        except Exception as e:
            self.logger.error(f"Error applying macro settings: {e}")
            results['error'] = str(e)
        
        return results
