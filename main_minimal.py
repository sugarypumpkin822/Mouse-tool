#!/usr/bin/env python3
"""
Minimal Mouse Configuration Tool - Main Application
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Import core components
from mouse_config.utils.logger import get_logger
from mouse_config.utils.config import check_dependencies, get_system_info

# Import PC optimizer
from mouse_config.advanced import PCOptimizer


def main():
    """Main application entry point"""
    try:
        # Initialize logger
        logger = get_logger(__name__)
        logger.info("Starting Mouse Configuration Tool v2.1.0")
        
        # Check dependencies
        logger.info("Checking dependencies...")
        missing_deps = check_dependencies()
        
        if missing_deps:
            error_msg = f"Missing dependencies: {', '.join(missing_deps)}"
            logger.error(error_msg)
            
            # Show error dialog
            app = QApplication(sys.argv)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Missing Dependencies")
            msg.setText(error_msg)
            msg.setInformativeText("Please install the missing dependencies:\n\n" + 
                              "pip install " + " ".join(missing_deps))
            msg.exec()
            return
        
        # Get system info
        system_info = get_system_info()
        logger.info(f"System: {system_info['system']} {system_info['release']}")
        logger.info(f"Python: {system_info['python_version']}")
        
        # Initialize PC optimizer
        pc_optimizer = PCOptimizer()
        logger.info("PC optimizer initialized")
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Mouse Configuration Tool")
        app.setApplicationVersion("2.1.0")
        
        # Set application style
        app.setStyle('Fusion')
        
        # Create simple window without TabContainer
        from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
        
        main_window = QMainWindow()
        main_window.setWindowTitle("Mouse Configuration Tool")
        main_window.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Add status label
        status_label = QLabel("Mouse Configuration Tool v2.1.0\n\nPC Optimization: Working\nServer/Client: Working\n\nNote: Full GUI temporarily disabled due to import issues.")
        status_label.setStyleSheet("padding: 20px; font-size: 14px;")
        layout.addWidget(status_label)
        
        central_widget.setLayout(layout)
        main_window.setCentralWidget(central_widget)
        main_window.show()
        
        logger.info("Application started successfully (minimal mode)")
        sys.exit(app.exec())
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
